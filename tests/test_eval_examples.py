"""Hand-worked example (D106, D118) and the frozen golden table from the real download."""
from pathlib import Path

from fpl.eval import download, report, run
from fpl.eval.measures import top20

DATA = Path(__file__).parent / "data"
SKIP = ("Folder:", "Commit:")  # the comparison ignores these header lines


def table(folder):
    text = report.render(run.run(download.load(folder)), 8027067, "folder", "commit")
    return [ln for ln in text.splitlines() if not ln.startswith(SKIP)]


def expected(name):
    return (DATA / name).read_text(encoding="utf-8").splitlines()


def test_hand_worked_example(monkeypatch):
    monkeypatch.setattr(top20, "TOP_N", 3)  # D118
    assert table(DATA / "eval_example") == expected("eval_expected.txt")


def test_golden_table():
    assert table(DATA / "eval_real") == expected("eval_golden.txt")


def result(rows):
    return {"rows": {i + 2: r for i, r in enumerate(rows)}}


def test_verdict_counts_strict_wins_only():
    rows = [
        {"top20 a": 1.0, "top20 b": 2.0, "ranking a": 0.1, "ranking b": 0.2},   # both better
        {"top20 a": 2.0, "top20 b": 2.0, "ranking a": 0.3, "ranking b": 0.2},   # tie, worse
        {"top20 a": 2.0, "top20 b": 1.0, "ranking a": None, "ranking b": 0.9},  # worse, "-"
        {"top20 a": 1.0, "top20 b": 1.5, "ranking a": 0.1, "ranking b": None},  # better, "-"
    ]
    out = report.verdict(result(rows), ["a", "b"])
    assert out == ["b vs a: top 20 better in 2 of 4 gameweeks, ranking better in 1 of 4"]
    assert "switch" not in out[0]


def test_verdict_one_line_per_extra_formula():
    r = result([{"top20 a": 1, "top20 b": 2, "top20 c": 0, "ranking a": 0, "ranking b": 0,
                 "ranking c": 1}])
    assert report.verdict(r, ["a", "b", "c"]) == [
        "b vs a: top 20 better in 1 of 1 gameweeks, ranking better in 0 of 1",
        "c vs a: top 20 better in 0 of 1 gameweeks, ranking better in 1 of 1"]
    assert report.verdict(r, ["a"]) == []
