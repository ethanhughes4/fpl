from pathlib import Path

import pytest

from fpl import brief, feed as feedmod
from fpl.explain import block
from fpl.mcp import session
from fpl.mcp.tools import get_brief

DATA = Path(__file__).parent / "data"


@pytest.mark.parametrize("name", ["example_a", "example_b", "example_c", "snapshot"])
def test_get_brief_is_header_plus_block(name):
    session.start(DATA / name)
    f = feedmod.load(DATA / name)
    head, _, body = get_brief.tool().partition("\n\n")
    assert head.startswith("Data downloaded ") and head.endswith(f"gameweek {feedmod.upcoming(f)['id']}")
    assert body == block.build(brief.build(f), f)
    assert "Explanation" not in body


def test_snapshot_matches_frozen_block():
    session.start(DATA / "snapshot")
    body = get_brief.tool().partition("\n\n")[2]
    assert body + "\n" == (DATA / "explain_block.txt").read_text(encoding="utf-8")
