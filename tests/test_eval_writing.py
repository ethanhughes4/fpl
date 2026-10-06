from fpl.claude import AskError
from fpl.eval import report as base
from fpl.eval.writing import __main__ as cli, checks, report, run

import pytest

from fpl.explain import check as _check
from fpl.explain.checks import names, numbers


@pytest.fixture(autouse=True)
def _two_checks(monkeypatch):
    # the one-line fake text cannot satisfy the coverage checks of every brief; those have own tests
    monkeypatch.setattr(_check, "CHECKS", [numbers, names])
    monkeypatch.setattr(run, "SCORERS", [checks])  # the judge has its own tests


GOOD = "Pick Hart as captain."
BAD = "Pick Hart, he scores 91.7."  # 91.7 is not in any brief


def fake(text=GOOD, tokens=10, seen=None):
    def ask(prompt, system, model, timeout):
        if seen is not None:
            seen.append((prompt, model))
        return text, tokens, "claude-haiku-4-5-20251001"
    return ask


def test_twelve_rows_all_pass():
    seen = []
    r = run.run(fake(seen=seen))
    assert len(r["rows"]) == 12 and r["calls"] == 12 and r["tokens"] == 120
    assert {x["brief"] for x in r["rows"]} == {"example_a", "example_b", "example_c", "snapshot"}
    assert all(x["scores"]["numbers"] for x in r["rows"])
    assert all(m == "sonnet" for _, m in seen)
    text = report.render(r, "abc1234")
    assert "Verdict: PASS" in text and "code checks pass rate: 100%" in text
    assert "Total tokens: 120" in text and "claude-haiku-4-5-20251001" in text
    assert text.count("--- ") == 12 and GOOD in text


def test_bad_text_fails_column_and_verdict():
    r = run.run(fake(BAD), runs=1)
    assert [x["scores"]["numbers"] for x in r["rows"]] == [False] * 4
    text = report.render(r, "abc1234")
    assert "FAIL" in text and "Verdict: FAIL" in text and "code checks pass rate: 0%" in text


def test_pass_rate_counts_explanations_not_cells():
    rows = [{"scores": {"numbers": True, "names": False}}, {"scores": {"numbers": True, "names": True}}]
    assert checks.summary(rows)[0][1] == "50%"
    assert checks.summary(rows[1:])[0][1:] == ("100%", True)


def test_tokens_dash_when_none():
    r = run.run(fake(tokens=None), runs=1)
    assert r["tokens"] is None
    assert "Total tokens: -" in report.render(r, "c")


def test_cap_stops_and_says_so():
    r = run.run(fake(), max_calls=5)
    assert r["calls"] == 5 and len(r["rows"]) == 5
    text = report.render(r, "c")
    assert "stopped at the 5-call cap, after 5 rows" in text and "Verdict: FAIL" in text


def test_writer_failure_row_fails():
    def ask(*a):
        raise AskError("timed out")
    r = run.run(ask, runs=1)
    assert all(x["error"] and not any(x["scores"].values()) for x in r["rows"])
    assert "(call failed: timed out)" in report.render(r, "c")


def test_saved_as_writing_file(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(base, "commit", lambda: "abc1234")
    assert cli.main([], ask=fake(), results=tmp_path) == 0
    files = list(tmp_path.glob("*-abc1234-writing.txt"))
    assert len(files) == 1 and "Verdict: PASS" in files[0].read_text(encoding="utf-8")
    assert "Saved to" in capsys.readouterr().out


def test_parallel_same_as_one_at_a_time_and_at_most_five_at_once():
    # D200: calls overlap (sleeps finish out of order) yet rows, scores and report match
    import random
    import threading
    import time
    live, most, lock = [0], [0], threading.Lock()

    def ask(prompt, system, model, timeout, **kw):
        with lock:
            live[0] += 1
            most[0] = max(most[0], live[0])
        time.sleep(random.uniform(0, 0.02))
        with lock:
            live[0] -= 1
        name = "Hart" if "Hart" in prompt else "Groß"
        return f"Pick {name}, he scores 91.7." if "Gale" in prompt else f"Pick {name}.", 3, "m"
    one = report.render(run.run(ask, parallel=1), "c")
    most[0] = 0
    five = report.render(run.run(ask), "c")
    assert one == five and 1 < most[0] <= run.PARALLEL == 5


def test_cap_reached_in_start_says_so():
    class Start:
        def start(ctx):
            for _ in range(3):
                ctx["ask"]("p", "s", "opus", 1)
            return []
        score = staticmethod(lambda text, ctx: {})
        summary = staticmethod(lambda rows: [])
    r = run.run(fake(), scorers=[checks, Start], max_calls=2)
    assert r["rows"] == [] and r["stopped"] == "stopped at the 2-call cap before any explanation"


def test_plan_limit_said_plainly():
    def ask(*a, **k):
        raise AskError("the model call failed (Claude usage limit reached)", plan_limit=True)
    r = run.run(ask, runs=1)
    assert r["plan_limit"] == 4
    text = report.render(r, "c")
    assert "PLAN LIMIT: 4 model calls failed because a Claude plan limit was reached." in text
    assert "PLAN LIMIT" not in report.render(run.run(fake(), runs=1), "c")
