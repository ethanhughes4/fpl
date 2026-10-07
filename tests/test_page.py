"""The data file `python -m fpl` writes for the web page (D287, D288, D302, D321)."""
import json
import shutil
from pathlib import Path

import pytest

from fpl import brief, feed as feedmod, page
from fpl.__main__ import main

DATA = Path(__file__).parent / "data"
SNAP = str(DATA / "snapshot")
REAL_PATH = page.PATH  # read before the autouse fixture swaps it


def header(name):
    feed = feedmod.load(DATA / name)
    return page.build(brief.build(feed), feed, None, None)["header"]


@pytest.mark.parametrize("name, team, deadline", [
    ("snapshot", "Ethans Team", "Deadline Sat 10 Oct 12:00"),  # 10:00Z, PC is UTC+2
    ("example_a", "Example A FC", "Deadline Sat 10 Oct 13:00"),  # 11:00Z
    ("example_b", "Example B FC", "Deadline Sat 10 Oct 13:00"),
    ("example_c", "Example C FC", "Deadline Sat 10 Oct 13:00"),
])
def test_header(name, team, deadline):
    assert header(name) == {"team": team, "gameweek": "Gameweek 6", "deadline": deadline}


def test_path_is_the_repos():
    assert REAL_PATH == Path(__file__).parents[1] / "web" / "public" / "brief.json"


def test_from_writes_the_file(page_file, capsys):
    assert main(["--from", SNAP, "--no-explain"]) == 0
    assert json.loads(page_file.read_text(encoding="utf-8"))["header"]["team"] == "Ethans Team"


def test_json_writes_nothing(page_file, capsys):
    assert main(["--from", SNAP, "--json"]) == 0
    assert not page_file.exists()


def test_team_writes_the_file(monkeypatch, page_file, capsys):
    import fpl.__main__ as m
    monkeypatch.setattr(m, "download", lambda team: SNAP)
    assert main(["--team", "123", "--no-explain"]) == 0
    assert page_file.exists()


def test_failed_run_keeps_the_old_file(tmp_path, page_file, capsys):
    page_file.parent.mkdir(parents=True)
    page_file.write_text("old", encoding="utf-8")
    shutil.copytree(SNAP, tmp_path / "s")
    (tmp_path / "s" / "fixtures.json").unlink()
    assert main(["--from", str(tmp_path / "s")]) == 1
    (tmp_path / "s2").mkdir()
    shutil.copytree(SNAP, tmp_path / "s2" / "x")
    (tmp_path / "s2" / "x" / "this-week.json").write_text(
        json.dumps({"gameweek": 6, "transfers": [{"out": "Nobody", "in": "Davis"}]}), encoding="utf-8")
    assert main(["--from", str(tmp_path / "s2" / "x")]) == 1  # ManualError
    assert page_file.read_text(encoding="utf-8") == "old"
