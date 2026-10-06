"""Runs the writer over the briefs and scores every text. Nothing here prints."""
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fpl import brief, feed as feedmod
from fpl.claude import AskError
from fpl.eval.writing import checks, judge
from fpl.explain import WRITER_MODEL, WRITER_TIMEOUT, block, writer_prompt

DATA = Path(__file__).parents[3] / "tests" / "data"
BRIEFS = [(n, DATA / n) for n in ("example_a", "example_b", "example_c", "snapshot")]
RUNS = 3  # D150
MAX_CALLS = 40  # D180
PARALLEL = 5  # D200: model calls at a time
SCORERS = [checks, judge]


class CapReached(Exception):
    pass


class CountedAsk:
    """Wraps `ask`: counts calls, tokens and plan-limit failures, refuses call MAX_CALLS + 1.
    Safe to call from several threads."""

    def __init__(self, ask, max_calls=MAX_CALLS):
        self.ask, self.max_calls = ask, max_calls
        self.calls, self.tokens, self.models, self.plan_limit = 0, None, [], 0
        self.lock = threading.Lock()

    def __call__(self, prompt, system, model, timeout, **kw):
        with self.lock:
            if self.calls >= self.max_calls:
                raise CapReached
            self.calls += 1
        try:
            result = self.ask(prompt, system, model, timeout, **kw)
            tokens, model_id = result[-2:]  # also wraps claude.ask_tools: (events, text, tokens, model_id)
        except AskError as e:
            if e.plan_limit:
                with self.lock:
                    self.plan_limit += 1
            raise
        with self.lock:
            if tokens is not None:
                self.tokens = (self.tokens or 0) + tokens
            if model_id and model_id not in self.models:
                self.models.append(model_id)
        return result


def run(ask, briefs=BRIEFS, runs=RUNS, scorers=None, max_calls=MAX_CALLS, parallel=None):
    """-> {rows, notices, summary, calls, tokens, models, stopped, plan_limit}.
    Three phases, each `parallel` calls at a time and kept in order: the scorers' start (the
    judge check), every writer call, then every score. The same result as one at a time (D200).
    A writer failure is a row that fails every column."""
    scorers = SCORERS if scorers is None else scorers
    counted = CountedAsk(ask, max_calls)
    out = {"rows": [], "notices": [], "stopped": None}
    with ThreadPoolExecutor(max_workers=parallel or PARALLEL) as pool:
        in_order = lambda f, items: list(pool.map(f, items))
        try:
            for s in scorers:
                out["notices"] += s.start({"ask": counted, "map": in_order})
        except CapReached:
            out["stopped"] = f"stopped at the {max_calls}-call cap before any explanation"
            briefs = []

        todo = []
        for name, folder in briefs:
            feed = feedmod.load(folder)
            data = brief.build(feed)
            blk = block.build(data, feed)
            ctx = {"data": data, "feed": feed, "block": blk, "ask": counted}
            todo += [(name, n, ctx) for n in range(1, runs + 1)]
        # the cap is planned before any writer call, so the same rows run every time
        per_row = 1 + sum(getattr(s, "CALLS_PER_TEXT", 0) for s in scorers)
        fit = max(0, (max_calls - counted.calls) // per_row)
        if fit < len(todo) and not out["stopped"]:
            todo = todo[:fit]
            out["stopped"] = f"stopped at the {max_calls}-call cap, after {fit} rows"

        prompt = writer_prompt()

        def write(job):
            name, n, ctx = job
            row = {"brief": name, "run": n, "tokens": None, "error": None, "scores": {}}
            try:
                text, row["tokens"], _ = counted(ctx["block"], prompt, WRITER_MODEL, WRITER_TIMEOUT)
            except AskError as e:
                row["text"], row["error"] = "", e.reason
            else:
                row["text"] = text.strip()
            return row, ctx

        def score(done):
            row, ctx = done
            for s in scorers:
                row["scores"].update(s.score(row["text"], ctx))
            if row["error"]:  # no text is never a pass
                row["scores"] = {k: False for k in row["scores"]}
            return row

        out["rows"] = in_order(score, in_order(write, todo))
    out["summary"] = [t for s in scorers for t in s.summary(out["rows"])]
    out.update(calls=counted.calls, tokens=counted.tokens, models=counted.models,
               plan_limit=counted.plan_limit)
    return out
