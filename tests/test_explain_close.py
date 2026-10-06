from pathlib import Path

from fpl import brief, feed as feedmod
from fpl.explain.parts import close

DATA = Path(__file__).parent / "data"


def build(x):
    return brief.build(feedmod.load(str(DATA / f"example_{x}")))


def get(x):
    return close.calls(build(x))


def by_kind(cs, k):
    return next(c for c in cs if c["kind"] == k)


def test_a():
    cs = get("a")
    assert len(cs) == 2  # no transfer
    c = by_kind(cs, "captain")
    assert (c["players"], c["numbers"], c["gap"], c["close"]) == (["Hart", "Marsh"], [7.9, 7.3], 0.6, True)
    b = by_kind(cs, "bench")
    assert b["players"][0] in ("Fry", "Kemp") and b["players"][1] == "Orr"
    assert (b["numbers"], b["gap"], b["close"]) == ([4.1, 3.8], 0.3, True)


def test_b():
    cs = get("b")
    c = by_kind(cs, "captain")
    assert (c["players"], c["gap"], c["close"]) == (["Marsh", "Innes"], 0.1, True)
    t = by_kind(cs, "transfer")
    assert (t["players"], t["numbers"], t["gap"], t["close"]) == (["Hart", "Wren"], [13.4, 2], 11.4, False)


def test_c():
    cs = get("c")
    c = by_kind(cs, "captain")
    assert (c["players"], c["gap"], c["close"]) == (["Hart", "Marsh"], 0.6, True)
    b = by_kind(cs, "bench")
    assert (b["players"], b["numbers"], b["gap"], b["close"]) == (["Fry", "Kemp"], [4.1, 4.1], 0.0, True)
    t = by_kind(cs, "transfer")
    assert (t["players"], t["numbers"], t["gap"], t["close"]) == (["Lowe", "Yates"], [10.8, 8], 2.8, False)


def test_rounding_first():
    data = {"captain": {"captain": {"name": "X", "score": 7.34}, "vice": {"name": "Y", "score": 7.15}},
            "lineup": {"starters": [], "bench": []}, "transfers": {"transfers": []}}
    c = close.calls(data)[0]
    assert c["numbers"] == [7.3, 7.2] and c["gap"] == 0.1


def test_lines():
    text = "\n".join(close.lines(build("b"), None))
    assert "Close calls" in text
    assert "captain Marsh 7.3 vs vice Innes 7.2, gap 0.1: close" in text
    assert "Hart -> Wren gain +13.4 against a bar of 2, margin 11.4: not close" in text
