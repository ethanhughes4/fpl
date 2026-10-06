"""Runs the writer over the briefs and scores every text. Nothing here prints."""
from pathlib import Path

from fpl import brief, feed as feedmod
from fpl.claude import AskError
from fpl.eval.writing import checks, judge
from fpl.explain import WRITER_MODEL, WRITER_TIMEOUT, block, writer_prompt

DATA = Path(__file__).parents[3] / "tests" / "data"
BRIEFS = [(n, DATA / n) for n in ("example_a", "example_b", "example_c", "snapshot")]
RUNS = 3  # D150
MAX_CALLS = 40  # D180
SCORERS = [checks, judge]


class CapReached(Exception):
    pass


class CountedAsk:
    """Wraps `ask`: counts calls and tokens, refuses call MAX_CALLS + 1."""

    def __init__(self, ask, max_calls=MAX_CALLS):
        self.ask, self.max_calls = ask, max_calls
        self.calls, self.tokens, self.models = 0, None, []

    def __call__(self, prompt, system, model, timeout, **kw):
        if self.calls >= self.max_calls:
            raise CapReached
        self.calls += 1
        text, tokens, model_id = self.ask(prompt, system, model, timeout, **kw)
        if tokens is not None:
            self.tokens = (self.tokens or 0) + tokens
        if model_id and model_id not in self.models:
            self.models.append(model_id)
        return text, tokens, model_id


def run(ask, briefs=BRIEFS, runs=RUNS, scorers=None, max_calls=MAX_CALLS):
    """-> {rows, notices, summary, calls, tokens, models, stopped}.
    A writer failure is a row that fails every column."""
    scorers = SCORERS if scorers is None else scorers
    counted = CountedAsk(ask, max_calls)
    out = {"rows": [], "notices": [], "stopped": None}
    try:
        for s in scorers:
            out["notices"] += s.start({"ask": counted})
        prompt = writer_prompt()
        for name, folder in briefs:
            feed = feedmod.load(folder)
            data = brief.build(feed)
            blk = block.build(data, feed)
            ctx = {"data": data, "feed": feed, "block": blk, "ask": counted}
            for n in range(1, runs + 1):
                row = {"brief": name, "run": n, "tokens": None, "error": None, "scores": {}}
                try:
                    text, row["tokens"], _ = counted(blk, prompt, WRITER_MODEL, WRITER_TIMEOUT)
                except AskError as e:
                    row["text"], row["error"] = "", e.reason
                else:
                    row["text"] = text.strip()
                for s in scorers:
                    row["scores"].update(s.score(row["text"], ctx))
                if row["error"]:  # no text is never a pass
                    row["scores"] = {k: False for k in row["scores"]}
                out["rows"].append(row)
    except CapReached:
        out["stopped"] = f"stopped at the {max_calls}-call cap, after {len(out['rows'])} rows"
    out["summary"] = [t for s in scorers for t in s.summary(out["rows"])]
    out.update(calls=counted.calls, tokens=counted.tokens, models=counted.models)
    return out
