from pathlib import Path

from fpl import brief, feed as feedmod
from fpl.explain import block

DATA = Path(__file__).parent / "data"


def test_frozen_block_for_gameweek_6():
    f = feedmod.load(str(DATA / "snapshot"))
    got = block.build(brief.build(f), f) + "\n"
    assert got == (DATA / "explain_block.txt").read_text(encoding="utf-8")
