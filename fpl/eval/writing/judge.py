"""The judge as a scorer (D149), and a check of the judge on fixed texts (D179, D196)."""
import json
from pathlib import Path

from fpl.claude import AskError

JUDGE_MODEL = "opus"  # D167, D174: no fallback
JUDGE_TIMEOUT = 180  # D176
CLARITY_BAR = 4.0
SHOWN_ANSWER = 200  # characters of an unreadable judge answer quoted in the report
HERE = Path(__file__).parent
CHECK_BLOCK = Path(__file__).parents[3] / "tests" / "data" / "explain_block.txt"
# D201: the judge lists what the brief does not support; code decides faithful (list empty).
# Answered through --json-schema (D198), so nothing can come before the answer.
SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["unsupported", "clarity"],
          "properties": {"unsupported": {"type": "array", "items": {"type": "string"}},
                         "clarity": {"type": "integer", "minimum": 1, "maximum": 5}}}
NONE_FOUND = "none"
COLUMN = "unsupported claims"
CALLS_PER_TEXT = 1  # D200: so the eval can plan its call cap
JUDGE_FAILED = "judge failed"  # D193: shown apart from faithful=no, never a pass
_state = {"proven": None}  # ponytail: module state, since summary(rows) gets no ctx


def parse(text):
    """-> (clarity, faithful, claims), or None when the answer cannot be read (D175).
    faithful = no unsupported claims (D201); claims = the list joined by "; ", or "none"."""
    try:
        d = json.loads(text)
    except ValueError:
        return None
    if not isinstance(d, dict) or set(d) != set(SCHEMA["required"]):
        return None
    c, claims = d["clarity"], d["unsupported"]
    if type(c) is not int or not 1 <= c <= 5 or not isinstance(claims, list)             or not all(isinstance(x, str) and x.strip() for x in claims):
        return None
    claims = [" ".join(x.split()) for x in claims]
    return c, not claims, "; ".join(claims) or NONE_FOUND


def _judge(blk, text, ask):
    """-> (clarity, faithful, claims); a judge failure is (None, JUDGE_FAILED, why)."""
    system = (HERE / "judge.txt").read_text(encoding="utf-8")
    try:
        answer = ask(f"BRIEF\n{blk}\n\nEXPLANATION\n{text}", system, JUDGE_MODEL, JUDGE_TIMEOUT,
                     schema=SCHEMA)[0]
    except AskError as e:
        return None, JUDGE_FAILED, f"judge call failed: {e.reason}"
    shown = " ".join(answer.split())[:SHOWN_ANSWER]
    return parse(answer) or (None, JUDGE_FAILED, f"unreadable answer: {shown!r}")


def texts():
    """-> [(faulty, text)] from judge_check.txt."""
    return [(f, t) for f, _, t in labelled()]


def labelled():
    """-> [(faulty, label, text)]; the label is the "=== " line, e.g. "faulty 2 made-up player name"."""
    parts = (HERE / "judge_check.txt").read_text(encoding="utf-8").split("=== ")[1:]
    return [(not p.startswith("clean"), p.split("\n", 1)[0].strip(), p.split("\n", 1)[1].strip())
            for p in parts]


def start(ctx):
    """Judges every fixed text (D179); one line per text with the judge's reason (D195)."""
    blk = CHECK_BLOCK.read_text(encoding="utf-8")
    bad, lines = [], []
    fixed = labelled()
    each = ctx.get("map") or (lambda f, items: list(map(f, items)))  # D200: in parallel, in order
    answers = each(lambda t: _judge(blk, t[2], ctx["ask"]), fixed)
    for n, ((faulty, label, text), (clarity, faithful, reason)) in enumerate(zip(fixed, answers), 1):
        wrong = clarity is None or faithful == faulty  # faulty must be "no", clean must be "yes"
        if wrong:
            bad.append(n)
        got = faithful if faithful == JUDGE_FAILED else ("yes" if faithful else "no")
        lines.append(f"  {'WRONG' if wrong else 'right'}  text {n} ({label}): expected "
                     f"{'no' if faulty else 'yes'}, got {got}; {reason}")
    _state["proven"] = not bad
    total = len(lines)
    if bad:
        head = ("JUDGE CHECK FAILED on text " + ", ".join(map(str, bad))
                + ": the judge scores below are unproven.")
    else:
        head = f"Judge check passed: all {total} fixed texts judged correctly."
    return [head] + lines


def score(text, ctx):
    if not text:
        return {"clarity": None, "faithful": False, COLUMN: "no text to judge"}
    clarity, faithful, claims = _judge(ctx["block"], text, ctx["ask"])
    return {"clarity": clarity, "faithful": faithful, COLUMN: claims}


def summary(rows):
    rows = [r for r in rows if "faithful" in r["scores"]]
    if not rows:
        return []
    """D193: judge failures are left out of the faithful rate and mean clarity, so they do not
    count against the writer; they get their own line, which fails the verdict (D175)."""
    judged = [r for r in rows if r["scores"]["faithful"] != JUDGE_FAILED]
    failed = len(rows) - len(judged)
    marks = [r["scores"]["clarity"] for r in judged if type(r["scores"]["clarity"]) is int]
    mean = sum(marks) / len(marks) if marks else 0.0
    rate = sum(r["scores"]["faithful"] is True for r in judged) / len(judged) if judged else 0.0
    proven = _state["proven"] is not False
    return [("faithful rate", f"{rate:.0%} of {len(judged)} judged", proven and bool(judged) and rate == 1.0),
            ("mean clarity", f"{mean:.1f}", proven and bool(marks) and mean >= CLARITY_BAR),
            ("judge failures", str(failed), failed == 0),
            ("judge check", "passed" if proven else "FAILED, scores unproven", proven)]
