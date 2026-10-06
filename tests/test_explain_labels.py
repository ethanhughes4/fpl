"""D199: the input block says things the writer kept getting wrong, in words it can't misread."""
from pathlib import Path

import pytest

from fpl import brief, feed as feedmod
from fpl.explain import block
from fpl.explain.parts import brief as brief_part, close

DATA = Path(__file__).parent / "data"


def blk(folder):
    f = feedmod.load(str(DATA / folder))
    return block.build(brief.build(f), f)


def test_transfers_labelled_as_suggestions():
    text = blk("example_b")
    assert "Suggested transfers (not made yet)\n  Hart -> Wren" in text
    assert "\nTransfers\n" not in text


def test_no_transfer_line_unchanged():
    assert "No transfer worth making. Save it — you'll have 4 free next week." in blk("example_a")


def test_net_gain_after_hit_is_its_own_number():
    # C: printed gain +10.8, hit 4 -> +6.8
    text = blk("example_c")
    assert "  Lowe -> Yates  (4.5m -> 5.0m)  6 GW gain +10.8  [hit]\n" \
           "    net gain after the 4-point hit +6.8" in text
    assert "net gain" not in blk("example_b")  # a free transfer has no hit


@pytest.mark.parametrize("pct, words", [(0, "ruled out"), (25, "likely to miss"), (49, "likely to miss"),
                                        (50, "doubtful"), (75, "doubtful"), (100, "expected to play")])
def test_chance_words(pct, words):
    assert brief_part.chance_text(pct) == f"chance of playing: {pct}% ({words})"


def test_warning_and_breakdown_use_chance_words():
    text = blk("example_b")
    assert "  Hart             chance of playing: 25% (likely to miss)  Hamstring" in text
    assert "next opponent T4 (H), fixture difficulty 3, chance of playing: 25% (likely to miss)" in text
    assert "playing chance" not in text


def test_form_explained():
    assert "form 7.4 (average points per match over the last 30 days)" in blk("example_b")


def _bench(starter, bench):
    data = {"captain": {"captain": {"name": "A", "score": 5.0}, "vice": {"name": "B", "score": 4.0}},
            "lineup": {"starters": [{"name": "S", "position": "DEF", "next": starter}],
                       "bench": [{"name": "X", "position": "MID", "next": bench}]},
            "transfers": {"transfers": []}}
    return close.lines(data, None)[-1]


def test_bench_call_in_full():
    assert _bench(2.9, 2.6) == ("  bench call: S starts as the lowest outfield starter with 2.9; "
                                "X is the best outfield player on the bench with 2.6; "
                                "S (starting) is ahead by 0.3: close")
    assert _bench(2.6, 2.9).endswith("X (bench) is ahead by 0.3: close")
    assert _bench(4.1, 4.1).endswith("they are level, gap 0.0: close")
