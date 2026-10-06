from pathlib import Path

import pytest

from fpl import brief, feed as feedmod
from fpl.claude import AskError
from fpl.eval.writing import judge, report, run
from fpl.explain import check

DATA = Path(__file__).parent / "data"
BLOCK = (DATA / "explain_block.txt").read_text(encoding="utf-8").strip()


@pytest.fixture(autouse=True)
def _reset():
    judge._state["proven"] = None


def test_parse():
    assert judge.parse("clarity=4 faithful=yes reason=Clear.") == (4, True, "Clear.")
    assert judge.parse("clarity=2 faithful=no reason=Wrong captain.\n") == (2, False, "Wrong captain.")
    for bad in ["clarity=6 faithful=yes reason=x", "clarity=4 faithful=yes",
                "Sure! clarity=4 faithful=yes reason=x", "clarity=4 faithful=yes reason=x\nmore", ""]:
        assert judge.parse(bad) is None


def test_eight_texts_six_faulty():
    t = judge.texts()
    assert len(t) == 8 and sum(f for f, _ in t) == 6


def test_all_eight_texts_pass_every_code_check():
    f = feedmod.load(str(DATA / "snapshot"))
    ctx = {"data": brief.build(f), "feed": f, "block": BLOCK}
    for n, (_, text) in enumerate(judge.texts(), 1):
        assert check.run(text, ctx) is None, n
        assert len(check.CHECKS) == 6


def right_judge(text_by_prompt):
    """A judge that is right about every fixed text."""
    def ask(prompt, system, model, timeout):
        assert model == "opus" and timeout == 180 and "EXPLANATION" in prompt
        faulty = text_by_prompt.get(prompt.split("EXPLANATION\n")[1])
        if faulty is None:
            return "clarity=5 faithful=yes reason=Fine.", 1, "m"
        return f"clarity=3 faithful={'no' if faulty else 'yes'} reason=r", 1, "m"
    return ask


def ctx_for(ask):
    return {"ask": ask}


def test_judge_check_passes():
    ask = right_judge({t: f for f, t in judge.texts()})
    assert judge.start(ctx_for(ask))[0].startswith("Judge check passed")
    assert judge._state["proven"] is True


def test_judge_check_fails_and_is_said_and_scores_unproven():
    texts = judge.texts()
    ask = right_judge({t: False for _, t in texts})  # calls every text clean
    notice = judge.start(ctx_for(ask))[0]
    assert "FAILED" in notice and "unproven" in notice
    rows = [{"scores": {"clarity": 5, "faithful": True, "judge reason": "ok"}}] * 2
    unproven = {label: p for label, _, p in judge.summary(rows)}
    assert not any(unproven[k] for k in ("faithful rate", "mean clarity", "judge check"))


def test_judge_check_unreadable_or_failed_call_fails():
    assert "FAILED" in judge.start(ctx_for(lambda *a: ("hello", 1, "m")))[0]

    def boom(*a):
        raise AskError("nope")
    assert "FAILED" in judge.start(ctx_for(boom))[0]


def test_score_and_failure():
    ok = lambda *a: ("clarity=4 faithful=yes reason=Good.", 1, "m")
    assert judge.score("text", {"ask": ok, "block": BLOCK}) == \
        {"clarity": 4, "faithful": True, "judge reason": "Good."}
    bad = judge.score("text", {"ask": lambda *a: ("clarity=9", 1, "m"), "block": BLOCK})
    assert bad["faithful"] == judge.JUDGE_FAILED and bad["clarity"] is None


def rows(*pairs):
    return [{"scores": {"clarity": c, "faithful": f, "judge reason": "r"}} for c, f in pairs]


def test_verdict_needs_all_three_bars():
    assert all(p for *_, p in judge.summary(rows((4, True), (4, True))))
    assert not judge.summary(rows((4, True), (4, False)))[0][2]  # faithful
    assert not judge.summary(rows((3, True), (4, True)))[1][2]  # clarity 3.5
    assert not judge.summary(rows((5, True), (5, False)))[0][2]  # a real faithful=no
    judge._state["proven"] = False
    s = {label: p for label, _, p in judge.summary(rows((5, True)))}  # judge check failed
    assert not any(s[k] for k in ("faithful rate", "mean clarity", "judge check"))


def test_judge_failure_shown_apart_and_not_against_the_writer():
    # D193: an unreadable judge answer is not a faithful=no; the writer's rates ignore it,
    # but the judge failures line fails the verdict
    s = judge.summary(rows((5, True), (None, judge.JUDGE_FAILED)))
    assert s[0] == ("faithful rate", "100% of 1 judged", True)
    assert s[1][1:] == ("5.0", True)
    assert s[2] == ("judge failures", "1", False)
    from fpl.eval.writing import report as rep
    assert rep.cell(judge.JUDGE_FAILED) == "judge failed"


def test_full_run_counts_calls_and_reports(monkeypatch):
    from fpl.explain.checks import names, numbers
    monkeypatch.setattr(check, "CHECKS", [numbers, names])
    seen = []

    def ask(prompt, system, model, timeout):
        seen.append(model)
        if model == "opus":
            ok = prompt.split("EXPLANATION\n")[1]
            faulty = dict((t, f) for f, t in judge.texts()).get(ok)
            return f"clarity=4 faithful={'no' if faulty else 'yes'} reason=r", 1, "m"
        return "Pick Hart as captain.", 1, "m"
    r = run.run(ask, runs=1)
    assert r["calls"] == len(seen) == 8 + 4 + 4 and r["stopped"] is None
    text = report.render(r, "c")
    assert "Judge check passed" in text and "mean clarity: 4.0" in text and "Verdict: PASS" in text
