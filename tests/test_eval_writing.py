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


GOOD = "Pick Hart as captain."
BAD = "Pick Hart, he scores 7.4."  # 7.4 is not in the brief


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
    assert all(m == "haiku" for _, m in seen)
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
    assert cli.main(ask=fake(), results=tmp_path) == 0
    files = list(tmp_path.glob("*-abc1234-writing.txt"))
    assert len(files) == 1 and "Verdict: PASS" in files[0].read_text(encoding="utf-8")
    assert "Saved to" in capsys.readouterr().out
