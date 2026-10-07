"""The bank, free transfers and formation tiles (D275, D289, D330, D333)."""
from pathlib import Path

import pytest

from fpl.page.parts import tiles as tiles_part
from fpl import brief, feed as feedmod, page

DATA = Path(__file__).parent / "data"


@pytest.mark.parametrize("name, tiles", [
    ("snapshot", ("0.0m", "4", "3-4-3")),
    ("example_a", ("0.0m", "3", "4-4-2")),  # D331: 3 free now
    ("example_b", ("0.0m", "1", "4-3-3")),
    ("example_c", ("0.5m", "0", "4-3-3")),  # D333, one hand-entered transfer
])
def test_tiles(name, tiles):
    feed = feedmod.load(DATA / name)
    got = tiles_part.build({"data": brief.build(feed), "feed": feed})
    assert got == dict(zip(("bank", "free_transfers", "formation"), tiles))
