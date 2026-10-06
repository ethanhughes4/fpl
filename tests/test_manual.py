import pytest

from fpl import manual
from fpl.sections import header
from tests.fakefeed import player


def entered(feed, *pairs, gw=6, bank=0.8):
    feed["this_week"] = {"gameweek": gw, "bank": bank,
                         "transfers": [{"out": o, "in": i} for o, i in pairs]}
    return feed


def named(id, pos, first, second, web):
    return player(id, pos, 1, first_name=first, second_name=second, web_name=web)


def test_absent(feed):
    assert manual.status(feed) == "absent" and manual.swaps(feed) == [] and manual.bank(feed) is None


def test_used_matches_web_name_any_case(feed):
    feed["bootstrap"]["elements"].append(named(20, 2, "Ben", "Davies", "Davies"))
    entered(feed, ("p3", "davies"))
    assert manual.status(feed) == "used"
    assert [(o["id"], i["id"]) for o, i in manual.swaps(feed)] == [(3, 20)]
    assert manual.bank(feed) == 8


def test_full_name_settles_a_shared_web_name(feed):
    feed["bootstrap"]["elements"] += [named(20, 2, "Ben", "Davies", "Davies"),
                                      named(21, 2, "Keane", "Davies", "Davies")]
    with pytest.raises(manual.ManualError, match='"Davies" matches more than one player'):
        manual.swaps(entered(feed, ("P3", "Davies")))
    assert manual.swaps(entered(feed, ("P3", "Keane Davies")))[0][1]["id"] == 21


def test_name_matching_nobody(feed):
    with pytest.raises(manual.ManualError, match='"Nobody" matches no player outside your squad'):
        manual.swaps(entered(feed, ("P3", "Nobody")))
    with pytest.raises(manual.ManualError, match='"P99" matches no player in your squad'):
        manual.swaps(entered(feed, ("P99", "P3")))


def test_positions_must_match(feed):
    feed["bootstrap"]["elements"].append(player(20, 4, 1))
    with pytest.raises(manual.ManualError, match="different positions"):
        manual.swaps(entered(feed, ("P3", "P20")))


def test_second_transfer_can_sell_the_first_buy(feed):
    feed["bootstrap"]["elements"] += [player(20, 2, 1), player(21, 2, 1)]
    got = manual.swaps(entered(feed, ("P3", "P20"), ("P20", "P21")))
    assert [(o["id"], i["id"]) for o, i in got] == [(3, 20), (20, 21)]


def test_other_gameweek_ignored(feed):
    entered(feed, ("Nobody", "Nobody"), gw=5)  # names are not even checked
    assert manual.status(feed) == "ignored" and manual.swaps(feed) == [] and manual.bank(feed) is None


def test_missing_keys(feed):
    feed["this_week"] = {"gameweek": 6}
    with pytest.raises(manual.ManualError, match='needs "gameweek", "transfers" and "bank"'):
        manual.status(feed)


def test_header_lines(feed):
    lines = header.render(header.build(feed))
    assert lines[1] == ("Shows your team at the last deadline. "
                        "Transfers made since are not visible in the public feed.")
    feed["bootstrap"]["elements"] += [player(20, 2, 1), player(21, 2, 1)]
    (line,) = header.render(header.build(entered(feed, ("P3", "P20"))))
    assert line.endswith(" · includes 1 transfer entered by hand")
    (line,) = header.render(header.build(entered(feed, ("P3", "P20"), ("P4", "P21"))))
    assert line.endswith(" · includes 2 transfers entered by hand")
    lines = header.render(header.build(entered(feed, gw=5)))
    assert lines[1] == "this-week.json is for gameweek 5, not 6: ignored."
    assert lines[2].startswith("Shows your team at the last deadline.")
