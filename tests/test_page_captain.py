"""Captain card text (D290, D334)."""
import copy
from pathlib import Path

from fpl import brief, feed as feedmod, page
from fpl.explain.parts import close
from fpl.page.parts import captain

DATA = Path(__file__).parent / "data"


def run_for(name="snapshot"):
    feed = feedmod.load(DATA / name)
    return {"data": brief.build(feed), "feed": feed, "downloaded": None, "explanation": None}


def test_snapshot_is_close():
    assert captain.build(run_for()) == {
        "captain": "Groß", "captain_score": "7.9", "vice": "Tarkowski", "vice_score": "7.2",
        "close": True,
        "sentence": "Gap of 0.7 for next gameweek. Anything at 1.0 or under counts as close."}


def test_not_close_sentence():
    run = run_for()
    d = copy.deepcopy(run["data"])
    d["captain"]["captain"]["score"] = d["captain"]["vice"]["score"] + 1.4
    out = captain.build({**run, "data": d})
    assert out["close"] is False
    assert out["sentence"] == "Gap of 1.4 for next gameweek. Over 1.0, so not close."


def test_close_line_unchanged():
    d = run_for()["data"]
    assert close._line(close.calls(d)[0]) == (
        "  captain Groß 7.9 vs vice Tarkowski 7.2, gap 0.7: close")


def test_in_page_build():
    run = run_for()
    assert page.build(run["data"], run["feed"], None, None)["captain"]["close"] is True
