import json
import shutil
from pathlib import Path

from fpl.__main__ import main

SNAP = str(Path(__file__).parent / "data" / "snapshot")


def test_from_prints_header(capsys):
    assert main(["--from", SNAP]) == 0
    assert capsys.readouterr().out.startswith("Gameweek 6 · deadline ")


def test_json(capsys):
    assert main(["--from", SNAP, "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["header"]["gameweek"] == 6


def test_missing_file(tmp_path, capsys):
    shutil.copytree(SNAP, tmp_path / "s")
    (tmp_path / "s" / "fixtures.json").unlink()
    assert main(["--from", str(tmp_path / "s")]) == 1
    assert "fixtures.json" in capsys.readouterr().out


def test_no_upcoming(tmp_path, capsys):
    shutil.copytree(SNAP, tmp_path / "s")
    p = tmp_path / "s" / "bootstrap-static.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for e in d["events"]:
        e["is_next"] = False
    p.write_text(json.dumps(d), encoding="utf-8")
    assert main(["--from", str(tmp_path / "s")]) == 0
    assert capsys.readouterr().out.strip() == "No upcoming gameweek."


def test_feed_error_and_unknown_team(monkeypatch, capsys):
    import fpl.__main__ as m
    from fpl.download import FeedError, TeamNotFound

    def boom(exc):
        def f(team):
            raise exc
        return f

    monkeypatch.setattr(m, "download", boom(FeedError(503)))
    assert main([]) == 1
    assert capsys.readouterr().out.strip() == (
        "Could not reach FPL (HTTP 503). Try again later or use --from <folder>")
    monkeypatch.setattr(m, "download", boom(TeamNotFound(7)))
    assert main(["--team", "7"]) == 1
    assert capsys.readouterr().out.strip() == "Team 7 not found."
