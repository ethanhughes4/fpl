"""The footer part: download time, header notes and eval lines (D290, D294, D297, D308, D322, D338)."""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from fpl import brief, feed as feedmod, page
from fpl.mcp.tools import get_eval_results as g
from fpl.sections.header import NOTE_NO_FILE

DATA = Path(__file__).parent / "data"
SET_TIME = datetime(2026, 10, 6, 12, 55, tzinfo=timezone.utc)


def footer(folder, downloaded=SET_TIME):
    feed = feedmod.load(folder)
    return page.build(brief.build(feed), feed, downloaded, None)["footer"]


@pytest.fixture
def res(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(g, "_log", lambda: ["new", "old"])
    (tmp_path / "results").mkdir()

    def put(name, *lines):
        (tmp_path / "results" / name).write_text("\n".join(lines), encoding="utf-8")
    return put


def test_download_time_in_local_time():
    utc = datetime(2026, 10, 7, 10, 55, tzinfo=timezone.utc)
    d = utc.astimezone()
    assert footer(DATA / "snapshot", utc)["downloaded"] == f"Data downloaded Wed 7 Oct {d:%H:%M}"


def test_notes_without_a_file():
    assert footer(DATA / "snapshot")["notes"] == [NOTE_NO_FILE]


def test_notes_for_a_transfer_entered_by_hand():
    assert footer(DATA / "example_c")["notes"] == ["includes 1 transfer entered by hand"]


def test_notes_for_an_ignored_file(tmp_path):
    shutil.copytree(DATA / "snapshot", tmp_path / "s")
    (tmp_path / "s" / "this-week.json").write_text(json.dumps({"gameweek": 5, "transfers": [], "bank": 0}),
                                                    encoding="utf-8")
    n = footer(tmp_path / "s")["notes"]
    assert n[0].endswith("is for gameweek 5, not 6: ignored.") and n[1:] == [NOTE_NO_FILE]


def test_eval_lines_quote_the_newest_files(res):
    res("2026-10-01-old.txt", "shrink vs current: old")
    res("2026-10-02-new.txt", "x", "shrink vs current: top 20 better in 4 of 4")
    res("2026-10-02-new-writing.txt", "faithful rate: 92% of 12 judged")
    res("2026-10-02-new-tools.txt", "path right: 30 of 30",
        "answers passing number and name checks: 28 of 30")
    assert footer(DATA / "snapshot")["evals"] == [
        "Scoring eval: shrink vs current: top 20 better in 4 of 4",
        "Writing eval: faithful rate: 92% of 12 judged",
        "Tools eval: path right: 30 of 30",
        "Tools eval: answers passing number and name checks: 28 of 30"]


def test_missing_results(res):
    res("2026-10-02-new-writing.txt", "faithful rate: 92% of 12 judged")
    assert footer(DATA / "snapshot")["evals"] == [
        "Scoring eval: no results yet",
        "Writing eval: faithful rate: 92% of 12 judged",
        "Tools eval: no results yet"]
