# What the one real call found (2026-10-07, Claude Code 2.1.292, model opus = claude-opus-5-5, D233, D242):
#
# Flags tried first: --safe-mode with --mcp-config. The server did NOT load: the init event had
#   "mcp_servers": [] and "tools": [], and Claude said it had no get_brief. So --safe-mode is out.
# Flags used (fpl.claude.ask_tools), which worked:
#   claude -p --setting-sources "" --model opus --mcp-config <file> --strict-mcp-config --tools ""
#     --allowedTools mcp__fpl --no-session-persistence --max-turns 6 --output-format stream-json
#     --verbose --permission-prompts none        (prompt on stdin, cwd = an empty temp folder)
#   --verbose is required with stream-json. --setting-sources "" (empty) loads no user, project or
#   local settings.
# MCP config: {"mcpServers": {"fpl": {"command": <python.exe>, "args": ["-m", "fpl.mcp", "--from",
#   <repo>/tests/data/snapshot], "env": {"PYTHONPATH": <repo>}}}}. Claude ran in a temp folder and the
#   server still imported fpl and connected ("mcp_servers": [{"name": "fpl", "status": "connected"}]),
#   so PYTHONPATH in the env entry is enough (D253 does not apply to this eval).
# Stream-json lines (one JSON object per line):
#   {"type": "system", "subtype": "init", "tools": [the five mcp__fpl__<name>], "mcp_servers": [...], ...}
#   {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "mcp__fpl__get_brief",
#       "input": {}}], "usage": {...}}}
#   {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": ...,
#       "content": "<a JSON string: {\"result\": \"<the tool's text>\"}>"}]}}   (the SDK wraps a str reply)
#   {"type": "assistant", "message": {"content": [{"type": "text", "text": "<answer>"}]}}
#   {"type": "result", "subtype": "success", "is_error": false, "num_turns": 2, "result": "<answer>",
#       "usage": {"input_tokens", "output_tokens", "cache_creation_input_tokens",
#       "cache_read_input_tokens"}, "modelUsage": {"claude-opus-5-5": {...}}, "permission_denials": []}
#   Also rate_limit_event and system thinking_tokens lines, which are ignored.
# Checks: the five mcp__fpl__ tools ran with no prompt (permission_denials empty). Claude had only
#   those five tools ("tools" in init), and asked to read the repo's README it said it had no file or
#   shell tool. The owner's CLAUDE.md, hooks and plugins were kept out: Claude said it saw none, and the
#   whole first request was 4,392 input tokens (4,390 cache creation + 2) including the five tool
#   definitions, far under what the owner's CLAUDE.md, skills and hooks would add (D169).
# A turn-limit hit ends with subtype "error_max_turns", so ask_tools raises AskError: a wrong path.
"""Asks every question of the tools eval through `claude -p` and scores each run (D233-D247)."""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fpl import feed as feedmod
from fpl.claude import AskError, ask_tools
from fpl.eval.tools import path
from fpl.eval.tools.questions import QUESTIONS
from fpl.eval.writing.run import CapReached, CountedAsk
from fpl.explain.checks import names, numbers

ROOT = Path(__file__).parents[3]
SNAPSHOT = ROOT / "tests" / "data" / "snapshot"
RUNS = 3  # D234
MAX_CALLS = 40  # D234
MAX_TURNS = 6  # D244
TIMEOUT = 180  # seconds per call, D244
MODEL = "opus"  # D235
PASS_PATH = 0.9  # D236: share of runs with the right path
PARALLEL = 5  # D200: model calls at a time
ANSWER_CHECKS = (numbers, names)  # D233


def mcp_config(snapshot=SNAPSHOT, root=ROOT):
    """The temp config: server fpl on the snapshot. PYTHONPATH finds the package from any folder."""
    return {"mcpServers": {"fpl": {"command": sys.executable,
                                   "args": ["-m", "fpl.mcp", "--from", str(snapshot)],
                                   "env": {"PYTHONPATH": str(root)}}}}


def run(ask=ask_tools, runs=RUNS, max_calls=MAX_CALLS, parallel=None, snapshot=SNAPSHOT,
        questions=QUESTIONS):
    """-> {rows, summary, calls, tokens, models, stopped, plan_limit}. Rows keep question order."""
    feed = feedmod.load(snapshot)
    pool = feed["bootstrap"]["elements"]
    counted = CountedAsk(ask, max_calls)
    config = mcp_config(snapshot)
    todo = [(i, q, n) for i, q in enumerate(questions, 1) for n in range(1, runs + 1)]
    stopped = None
    if len(todo) > max_calls:  # planned before any call, so the same rows run every time
        todo, stopped = todo[:max_calls], f"stopped at the {max_calls}-call cap, after {max_calls} rows"

    def one(job):
        i, q, n = job
        row = {"q": i, "question": q.text, "run": n, "calls": [], "path": False, "why": "",
               "numbers": False, "names": False, "tokens": None, "error": None, "text": ""}
        try:
            events, text, row["tokens"], _ = counted(q.text, config, MODEL, TIMEOUT, max_turns=MAX_TURNS)
        except (AskError, CapReached) as e:
            row["error"] = getattr(e, "reason", "stopped at the call cap")
            row["why"] = "no answer: " + row["error"]  # a turn-limit hit or timeout is a wrong path
            return row
        row["text"] = text.strip()
        made = path.calls(events)
        row["calls"] = made
        row["path"], row["why"] = path.check(q, made, pool)
        # D246: only numbers in the tool outputs pass; no output means any number fails.
        # D260: names may also come from the question itself.
        out = "\n".join(path.outputs(events))
        row["numbers"] = numbers.check(row["text"], {"block": out, "feed": feed}) is None
        row["names"] = names.check(row["text"], {"block": q.text + "\n" + out, "feed": feed}) is None
        return row

    with ThreadPoolExecutor(max_workers=parallel or PARALLEL) as pool_:
        rows = list(pool_.map(one, todo))
    n = len(rows)
    right = sum(r["path"] for r in rows)
    answers = sum(r["numbers"] and r["names"] for r in rows)
    summary = [("path right", f"{right} of {n}", bool(n) and right / n >= PASS_PATH),
               ("answers passing number and name checks", f"{answers} of {n}", bool(n) and answers == n)]
    return {"rows": rows, "summary": summary, "calls": counted.calls, "tokens": counted.tokens,
            "models": counted.models, "stopped": stopped, "plan_limit": counted.plan_limit}
