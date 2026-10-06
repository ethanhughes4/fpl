import json
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


def ans(claims=(), clarity=4):
    """The judge's structured answer (D201)."""
    return json.dumps({"unsupported": list(claims), "clarity": clarity})


def test_parse():
    # D201: faithful is worked out by code from the list
    assert judge.parse(ans([], 4)) == (4, True, "none")
    assert judge.parse(ans(["Says nine, brief gives 7.9.", "Calls  Haaland\ncaptain."], 2)) == \
        (2, False, "Says nine, brief gives 7.9.; Calls Haaland captain.")
    for bad in [ans([], 6), ans([], 0), '{"unsupported": [], "clarity": true}',
                ans([" "]), '{"unsupported": [1], "clarity": 4}', '{"unsupported": "x", "clarity": 4}',
                '{"clarity": 4}', '{"unsupported": [], "clarity": 4, "faithful": "yes"}',
                "clarity=4 faithful=yes reason=x", "[1, 2]", ""]:
        assert judge.parse(bad) is None, bad


def test_eleven_texts_nine_faulty():
    t = judge.texts()
    assert len(t) == 11 and sum(f for f, _ in t) == 9  # D196


def test_all_fixed_texts_pass_every_code_check():
    f = feedmod.load(str(DATA / "snapshot"))
    ctx = {"data": brief.build(f), "feed": f, "block": BLOCK}
    for n, (_, text) in enumerate(judge.texts(), 1):
        assert check.run(text, ctx) is None, n
        assert len(check.CHECKS) == 6


def right_judge(text_by_prompt):
    """A judge that is right about every fixed text."""
    def ask(prompt, system, model, timeout, **kw):
        assert model == "opus" and timeout == 180 and "EXPLANATION" in prompt
        faulty = text_by_prompt.get(prompt.split("EXPLANATION\n")[1])
        if faulty is None:
            return ans([], 5), 1, "m"
        return ans(["r"] if faulty else [], 3), 1, "m"
    return ask


def ctx_for(ask):
    return {"ask": ask}


def test_judge_check_prints_each_reason():
    def ask(prompt, system, model, timeout, **kw):
        return ans([]), 1, "m"
    lines = judge.start(ctx_for(ask))
    assert lines[0].startswith("JUDGE CHECK FAILED") and len(lines) == 12
    assert lines[1] == "  right  text 1 (clean): expected yes, got yes; none"
    assert lines[3] == ("  WRONG  text 3 (faulty 1 number on the wrong player): "
                        "expected no, got yes; none")


def test_judge_check_flag_runs_only_the_check(capsys):
    from fpl.eval.writing import __main__ as cli
    seen = []

    def ask(prompt, system, model, timeout, **kw):
        seen.append(model)
        return ans(["r"]), 7, "claude-opus-5-5"
    assert cli.main(["--judge-check"], ask=ask) == 0
    out = capsys.readouterr().out
    assert seen == ["opus"] * 11 and "Calls: 11" in out and "Total tokens: 77" in out
    assert "text 1 (clean): expected yes, got no; r" in out


def test_judge_check_passes():
    ask = right_judge({t: f for f, t in judge.texts()})
    assert judge.start(ctx_for(ask))[0].startswith("Judge check passed")
    assert judge._state["proven"] is True


def test_judge_check_fails_and_is_said_and_scores_unproven():
    texts = judge.texts()
    ask = right_judge({t: False for _, t in texts})  # calls every text clean
    notice = judge.start(ctx_for(ask))[0]
    assert "FAILED" in notice and "unproven" in notice
    rows = [{"scores": {"clarity": 5, "faithful": True, judge.COLUMN: "none"}}] * 2
    unproven = {label: p for label, _, p in judge.summary(rows)}
    assert not any(unproven[k] for k in ("faithful rate", "mean clarity", "judge check"))


def test_judge_check_unreadable_or_failed_call_fails():
    assert "FAILED" in judge.start(ctx_for(lambda *a, **k: ("hello", 1, "m")))[0]

    def boom(*a, **k):
        raise AskError("nope")
    assert "FAILED" in judge.start(ctx_for(boom))[0]


def test_score_and_failure():
    ok = lambda *a, **k: (ans([]), 1, "m")
    assert judge.score("text", {"ask": ok, "block": BLOCK}) == \
        {"clarity": 4, "faithful": True, "unsupported claims": "none"}
    no = lambda *a, **k: (ans(["Says 9, brief gives 7.9."], 3), 1, "m")
    assert judge.score("text", {"ask": no, "block": BLOCK}) == \
        {"clarity": 3, "faithful": False, "unsupported claims": "Says 9, brief gives 7.9."}
    bad = judge.score("text", {"ask": lambda *a, **k: ("clarity=9", 1, "m"), "block": BLOCK})
    assert bad["faithful"] == judge.JUDGE_FAILED and bad["clarity"] is None


def rows(*pairs):
    return [{"scores": {"clarity": c, "faithful": f, judge.COLUMN: "r"}} for c, f in pairs]


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
    assert report.cell(judge.JUDGE_FAILED) == "judge failed"


def test_full_run_counts_calls_and_reports(monkeypatch):
    from fpl.explain.checks import names, numbers
    monkeypatch.setattr(check, "CHECKS", [numbers, names])
    seen = []

    def ask(prompt, system, model, timeout, **kw):
        seen.append(model)
        if model == "opus":
            ok = prompt.split("EXPLANATION\n")[1]
            faulty = dict((t, f) for f, t in judge.texts()).get(ok)
            return ans(["r"] if faulty else []), 1, "m"
        return "Pick Hart as captain.", 1, "m"
    r = run.run(ask, runs=1)
    assert r["calls"] == len(seen) == 11 + 4 + 4 and r["stopped"] is None
    text = report.render(r, "c")
    assert "Judge check passed" in text and "mean clarity: 4.0" in text and "Verdict: PASS" in text
    assert "unsupported claims" in text


def test_unreadable_answer_is_quoted_on_one_line_and_cut():
    long = "Looking at this:\nclarity=4 faithful=no " + "x" * 300
    got = judge.score("text", {"ask": lambda *a, **k: (long, 1, "m"), "block": BLOCK})
    assert got["faithful"] == judge.JUDGE_FAILED
    reason = got[judge.COLUMN]
    assert reason.startswith("unreadable answer: 'Looking at this: clarity=4") and "\n" not in reason
    assert len(reason) <= len("unreadable answer: ''") + judge.SHOWN_ANSWER


def test_judge_asks_with_the_schema():
    seen = {}

    def ask(prompt, system, model, timeout, **kw):
        seen.update(kw)
        return ans([], 5), 1, "m"
    assert judge.score("text", {"ask": ask, "block": BLOCK})["faithful"] is True
    assert seen == {"schema": judge.SCHEMA}
    assert judge.SCHEMA["required"] == ["unsupported", "clarity"]  # no faithful field (D201)
