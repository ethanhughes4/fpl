from pathlib import Path

from fpl import brief, feed as feedmod, page
from fpl.page.parts import bench_call

DATA = Path(__file__).parent / "data"


def sentence(name):
    feed = feedmod.load(DATA / name)
    return page.build(brief.build(feed), feed, None, None)["bench_call"]["sentence"]


def test_snapshot_close():
    assert sentence("snapshot") == ("Calvert-Lewin starts at 2.9. Diop is the best outfield player "
                                    "on the bench at 2.6. Calvert-Lewin is 0.3 ahead, which is close.")


def test_example_b_not_close():
    assert sentence("example_b") == ("Orr starts at 3.8. Gale is the best outfield player on the bench "
                                    "at 3.0. Orr is 0.8 ahead, which is not close.")


def test_example_c_level():
    s = sentence("example_c")
    assert s.endswith("They are level, which is close.")
    assert "at 4.1." in s


def call(gap, close):
    return {"players": ["Fry", "Kemp"], "numbers": [4.1, 4.1 + (-gap)], "gap": gap, "close": close}


def test_four_forms():
    assert bench_call.sentence(call(0.8, False)).endswith("Fry is 0.8 ahead, which is not close.")
    assert bench_call.sentence(call(0.0, True)).endswith("They are level, which is close.")
    assert bench_call.sentence(call(-0.2, True)).endswith("Kemp is 0.2 ahead, which is close.")


def test_no_bench_call():
    data = {"lineup": {"starters": [], "bench": []},
            "captain": {"captain": {"name": "A", "score": 5.0}, "vice": {"name": "B", "score": 4.0}},
            "transfers": {"transfers": []}}
    assert bench_call.build({"data": data}) == {"sentence": None}
