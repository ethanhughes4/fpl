"""The transfers part of the page file (D289, D295, D296, D331, D333, D335, D336)."""
from pathlib import Path

from fpl import brief, feed as feedmod, page
from fpl.page.parts import transfers

DATA = Path(__file__).parent / "data"


def part(name):
    feed = feedmod.load(DATA / name)
    return transfers.build({"data": brief.build(feed), "feed": feed})


def test_snapshot_two_rows():
    p = part("snapshot")
    assert [(r["out"], r["in"], r["prices"], r["gain"], r["tags"]) for r in p["rows"]] == [
        ("Szoboszlai", "Schade", "6.9m → 6.2m", "+14.7", []),
        ("O'Shea", "Davis", "4.0m → 4.0m", "+11.4", [])]
    assert p["hit_line"] is None and p["empty"] is None


def test_example_a_empty_line():
    p = part("example_a")
    assert p["rows"] == [] and p["hit_line"] is None
    assert p["empty"] == "No transfer worth making. Save your 3 free transfers — you'll have 4 free next week."


def test_example_c_hit():
    p = part("example_c")
    assert (p["rows"][0]["out"], p["rows"][0]["in"]) == ("Lowe", "Yates")
    assert p["rows"][0]["tags"] == ["−4 hit"]
    assert p["hit_line"] == "Hit: -4 points"


def test_two_hits_and_bench_tag():
    t = {"transfers": [
        {"out": "A", "in": "B", "gain": 9.0, "out_price": 50, "in_price": 55, "starts": True, "hit": True},
        {"out": "C", "in": "D", "gain": 3.04, "out_price": 40, "in_price": 40, "starts": False, "hit": False},
        {"out": "E", "in": "F", "gain": 9.0, "out_price": 40, "in_price": 40, "starts": True, "hit": True}],
        "hit_points": 8, "free_now": 1, "free_next_week": 1}
    p = transfers.build({"data": {"transfers": t}})
    assert p["hit_line"] == "Hit: -8 points"
    assert [r["tags"] for r in p["rows"]] == [["−4 hit"], ["bench, half gain"], ["−4 hit"]]
    assert p["rows"][1]["gain"] == "+3.0" and p["rows"][0]["prices"] == "5.0m → 5.5m"
