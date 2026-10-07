"""The deadline part of the page file (D300)."""
from pathlib import Path

from fpl.page.parts import deadline
from fpl import brief, feed as feedmod, page

DATA = Path(__file__).parent / "data"


def test_snapshot_time_and_text():
    feed = feedmod.load(DATA / "snapshot")
    d = deadline.build({"data": brief.build(feed), "feed": feed})
    assert d == {"utc": "2026-10-10T10:00:00Z",
                 "passed": "Gameweek 6's deadline has passed. Run python -m fpl."}
