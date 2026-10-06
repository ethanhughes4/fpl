"""D205: the explanation names the player coming in on every suggested transfer."""
from pathlib import Path

from fpl import brief, feed as feedmod
from fpl.explain.checks import incoming

DATA = Path(__file__).parent / "data"


def ctx(folder):
    f = feedmod.load(str(DATA / folder))
    return {"data": brief.build(f), "feed": f}


def test_named_passes_missing_fails():
    c = ctx("example_b")  # Hart -> Wren
    assert incoming.check("Swap Hart for WREN.", c) is None
    assert incoming.check("Swap Hart out.", c) == \
        "it did not name Wren, who comes in on a suggested transfer"


def test_every_transfer_and_none():
    c = ctx("snapshot")  # Szoboszlai -> Schade, O'Shea -> Davis
    assert incoming.check("Bring in Schade and Davis.", c) is None
    assert "Davis" in incoming.check("Bring in Schade.", c)
    assert incoming.check("No moves.", ctx("example_a")) is None  # no suggested transfer


def test_eval_only():
    assert incoming.LIVE is False and incoming.NAME == "incoming"
