"""The judge as a scorer (D149), and a check of the judge on fixed texts (D179, D196)."""
import re
from pathlib import Path

from fpl.claude import AskError

JUDGE_MODEL = "opus"  # D167, D174: no fallback
JUDGE_TIMEOUT = 180  # D176
CLARITY_BAR = 4.0
SHOWN_ANSWER = 200  # characters of an unreadable judge answer quoted in the report
HERE = Path(__file__).parent
CHECK_BLOCK = Path(__file__).parents[3] / "tests" / "data" / "explain_block.txt"
LINE = re.compile(r"clarity=([1-5]) faithful=(yes|no) reason=(\S.*)")
JUDGE_FAILED = "judge failed"  # D193: shown apart from faithful=no, never a pass
_state = {"proven": None}  # ponytail: module state, since summary(rows) gets no ctx


def parse(text):
    """-> (clarity, faithful, reason), or None when the line cannot be read (D175)."""
    m = LINE.fullmatch(text.strip())
    return (int(m[1]), m[2] == "yes", m[3]) if m else None


def _judge(blk, text, ask):
    """-> (clarity, faithful, reason); a judge failure is (None, JUDGE_FAILED, why)."""
    system = (HERE / "judge.txt").read_text(encoding="utf-8")
    try:
        answer = ask(f"BRIEF\n{blk}\n\nEXPLANATION\n{text}", system, JUDGE_MODEL, JUDGE_TIMEOUT)[0]
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
    for n, (faulty, label, text) in enumerate(labelled(), 1):
        clarity, faithful, reason = _judge(blk, text, ctx["ask"])
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
        return {"clarity": None, "faithful": False, "judge reason": "no text to judge"}
    clarity, faithful, reason = _judge(ctx["block"], text, ctx["ask"])
    return {"clarity": clarity, "faithful": faithful, "judge reason": reason}


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
