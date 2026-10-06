"""The judge as a scorer (D149), and a check of the judge on 8 fixed texts (D179)."""
import re
from pathlib import Path

from fpl.claude import AskError

JUDGE_MODEL = "opus"  # D167, D174: no fallback
JUDGE_TIMEOUT = 180  # D176
CLARITY_BAR = 4.0
HERE = Path(__file__).parent
CHECK_BLOCK = Path(__file__).parents[3] / "tests" / "data" / "explain_block.txt"
LINE = re.compile(r"clarity=([1-5]) faithful=(yes|no) reason=(\S.*)")
_state = {"proven": None}  # ponytail: module state, since summary(rows) gets no ctx


def parse(text):
    """-> (clarity, faithful, reason), or None when the line cannot be read (D175)."""
    m = LINE.fullmatch(text.strip())
    return (int(m[1]), m[2] == "yes", m[3]) if m else None


def _judge(blk, text, ask):
    """-> (clarity, faithful, reason); a judge failure is (None, False, why)."""
    system = (HERE / "judge.txt").read_text(encoding="utf-8")
    try:
        got = parse(ask(f"BRIEF\n{blk}\n\nEXPLANATION\n{text}", system, JUDGE_MODEL, JUDGE_TIMEOUT)[0])
    except AskError as e:
        return None, False, f"judge call failed: {e.reason}"
    return got or (None, False, "judge failure: unreadable answer")


def texts():
    """-> [(faulty, text)] from judge_check.txt."""
    parts = (HERE / "judge_check.txt").read_text(encoding="utf-8").split("=== ")[1:]
    return [(not p.startswith("clean"), p.split("\n", 1)[1].strip()) for p in parts]


def start(ctx):
    blk = CHECK_BLOCK.read_text(encoding="utf-8")
    bad = []
    for n, (faulty, text) in enumerate(texts(), 1):
        got = _judge(blk, text, ctx["ask"])
        if got[0] is None or got[1] == faulty:  # faulty must be "no", clean must be "yes"
            bad.append(n)
    _state["proven"] = not bad
    if bad:
        return ["JUDGE CHECK FAILED on text " + ", ".join(map(str, bad))
                + ": the judge scores below are unproven."]
    return ["Judge check passed: all 8 fixed texts judged correctly."]


def score(text, ctx):
    if not text:
        return {"clarity": None, "faithful": False, "judge reason": "no text to judge"}
    clarity, faithful, reason = _judge(ctx["block"], text, ctx["ask"])
    return {"clarity": clarity, "faithful": faithful, "judge reason": reason}


def summary(rows):
    rows = [r for r in rows if "faithful" in r["scores"]]
    if not rows:
        return []
    marks = [r["scores"]["clarity"] for r in rows if type(r["scores"]["clarity"]) is int]
    mean = sum(marks) / len(marks) if marks else 0.0
    rate = sum(r["scores"]["faithful"] is True for r in rows) / len(rows)
    proven = _state["proven"] is not False
    return [("faithful rate", f"{rate:.0%}", proven and rate == 1.0),
            ("mean clarity", f"{mean:.1f}", proven and len(marks) == len(rows) and mean >= CLARITY_BAR),
            ("judge check", "passed" if proven else "FAILED, scores unproven", proven)]
