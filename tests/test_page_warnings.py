"""Warnings part of the page file (step 6)."""
from pathlib import Path

from fpl import brief, feed as feedmod, page
from fpl.page.parts import warnings

DATA = Path(__file__).parent / "data"


def part(name):
    feed = feedmod.load(DATA / name)
    return page.build(brief.build(feed), feed, None, None)["warnings"]


def test_snapshot_row():
    assert part("snapshot") == {"rows": [{"name": "João Pedro", "chance": "75%",
                                          "news": "Knee injury - 75% chance of playing"}], "empty": None}


def test_example_a_none():
    assert part("example_a") == {"rows": [], "empty": "Warnings: none"}


def test_example_b_hart():
    rows = part("example_b")["rows"]
    assert [(r["name"], r["chance"]) for r in rows] == [("Hart", "25%")]


def test_blank_player_news():
    run = {"data": {"warnings": [{"name": "X", "chance": 100, "blank": True, "news": ""}]}}
    assert warnings.build(run)["rows"] == [{"name": "X", "chance": "100%", "news": "no fixture next gameweek"}]
