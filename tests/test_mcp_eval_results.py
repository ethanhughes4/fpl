import pytest

from fpl.mcp.tools import get_eval_results as g


@pytest.fixture
def res(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "RESULTS", tmp_path)
    monkeypatch.setattr(g, "_log", lambda: ["new", "mid", "old"])  # newest first

    def put(*names):
        for n in names:
            (tmp_path / n).write_text(n, encoding="utf-8")
    return put


def test_newest_by_commit_not_date(res):
    res("2026-10-09-old.txt", "2026-10-01-new.txt", "2026-10-05-mid.txt")
    assert g.tool("scoring") == "2026-10-01-new.txt\n\n2026-10-01-new.txt"


def test_dirty_counts_as_base_and_same_commit_later_date(res):
    res("2026-10-01-mid.txt", "2026-10-02-mid-dirty.txt", "2026-10-09-old.txt")
    assert g.tool("scoring").startswith("2026-10-02-mid-dirty.txt")


def test_unknown_commits_last(res):
    res("2026-10-09-unknown.txt", "2026-10-09-abc1234.txt", "2026-10-01-old.txt")
    assert g.tool("scoring").startswith("2026-10-01-old.txt")


def test_tools_ignores_quick_and_scoring_ignores_others(res):
    res("2026-10-01-old-tools.txt", "2026-10-02-new-tools-quick.txt",
        "2026-10-02-new-writing.txt", "2026-10-03-new-tools-quick.txt", "2026-10-01-mid.txt")
    assert g.tool("tools").startswith("2026-10-01-old-tools.txt")
    assert g.tool("writing").startswith("2026-10-02-new-writing.txt")
    assert g.tool("scoring").startswith("2026-10-01-mid.txt")


def test_bad_kind_and_empty(res):
    assert "\n" not in g.tool("quick")
    assert g.tool("scoring") == "No scoring results file found."
    res("2026-10-01-new-writing.txt")
    assert g.tool("scoring") == "No scoring results file found."
