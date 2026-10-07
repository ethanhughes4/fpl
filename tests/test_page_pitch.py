"""The pitch part: rows, roles, bench and doubts as text (D289, D292, D293)."""
from pathlib import Path

from fpl.page.parts import pitch as pitch_part
from fpl import brief, feed as feedmod, page

DATA = Path(__file__).parent / "data"


def pitch(name, edit=None):
    feed = feedmod.load(DATA / name)
    data = brief.build(feed)
    if edit:
        edit(data)
    return pitch_part.build({"data": data, "feed": feed})


def names(p):
    return [[x["name"] for x in r["players"]] for r in p["rows"]]


def test_snapshot_rows_and_roles():
    p = pitch("snapshot")
    assert names(p) == [["Verbruggen"], ["Tarkowski", "Calafiori", "Ajer"],
                        ["Groß", "B.Fernandes", "Mbeumo", "Szoboszlai"],
                        ["Haaland", "João Pedro", "Calvert-Lewin"]]
    assert p["rows"][1]["players"][0] == {"name": "Tarkowski", "next": "7.2", "six": "29.0",
                                          "role": "VICE", "doubt": None}
    assert p["rows"][2]["players"][0] == {"name": "Groß", "next": "7.9", "six": "34.9",
                                          "role": "CAPTAIN", "doubt": None}
    assert p["rows"][3]["players"][1]["doubt"] == "75% to play"
    assert [(b["label"], b["name"], b["next"]) for b in p["bench"]] == [
        ("GK", "Kinsky", "3.1"), ("1st", "Diop", "2.6"), ("2nd", "M.Sangaré", "2.3"), ("3rd", "O'Shea", "2.2")]


def test_example_a_no_doubts():
    p = pitch("example_a")
    assert names(p)[0] == ["Ames"]
    assert [x["name"] for r in p["rows"] for x in r["players"] if x["role"]] == ["Hart", "Marsh"]
    assert not any(x["doubt"] for r in p["rows"] for x in r["players"])
    assert [b["name"] for b in p["bench"]] == ["Birch", "Orr", "Gale", "Lowe"]


def test_example_b_bench_doubt():
    p = pitch("example_b")
    assert p["bench"][3] == {"label": "3rd", "name": "Hart", "next": "2.0", "six": p["bench"][3]["six"],
                             "role": None, "doubt": "25% to play"}  # D332
    assert [x["name"] for r in p["rows"] for x in r["players"] if x["role"] == "CAPTAIN"] == ["Marsh"]


def test_example_c_captain_vice():
    p = pitch("example_c")
    roles = {x["name"]: x["role"] for r in p["rows"] for x in r["players"] if x["role"]}
    assert roles == {"Hart": "CAPTAIN", "Marsh": "VICE"}
    assert p["bench"][1]["name"] == "Kemp"


def test_blank_player_reads_no_match():
    def blank(data):
        data["warnings"][0].update(blank=True, chance=100)
    p = pitch("snapshot", blank)
    assert p["rows"][3]["players"][1]["doubt"] == "No match"
