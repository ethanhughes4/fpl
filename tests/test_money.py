from pathlib import Path

from fpl import money
from fpl.feed import load
from fpl.sections import money as section
from tests.fakefeed import player, transfer


def test_price():
    assert money.price(61) == "6.1m"
    assert money.price(5) == "0.5m"


def sell(feed, **kw):
    p = player(99, 3, 1, **kw)
    return money.selling_price(feed, p)


def test_selling_price_rise_rounds_down(feed):
    feed["transfers"] = [transfer(99, 1, 3, in_cost=50)]
    assert sell(feed, cost=53) == 51  # rise 3 * 0.5 = 1.5 -> 1
    assert sell(feed, cost=54) == 52


def test_selling_price_fall_is_now_cost(feed):
    feed["transfers"] = [transfer(99, 1, 3, in_cost=50)]
    assert sell(feed, cost=48) == 48


def test_held_since_start_uses_cost_change_start(feed):
    assert sell(feed, cost=54, cost_change_start=2) == 53  # bought 52, rise 2


def test_free_hit_buy_back_ignored(feed):
    feed["history"]["chips"] = [{"name": "freehit", "event": 4}]
    feed["transfers"] = [transfer(99, 1, 2, in_cost=50), transfer(99, 2, 4, in_cost=56)]
    assert money.purchase_price(feed, player(99, 3, 1, cost=56)) == 50


def test_bank_from_picks_or_this_week_file(feed):
    assert money.bank(feed) == 5
    feed["transfers"] = [transfer(20, 1, 6, in_cost=60, out_cost=52)]  # feed transfers ignored (D66)
    assert money.bank(feed) == 5
    feed["this_week"] = {"gameweek": 6, "transfers": [], "bank": 0.8}
    assert money.bank(feed) == 8  # D67: the bank given, in tenths


def test_free_transfers_snapshot():
    feed = load(Path(__file__).parent / "data" / "snapshot")
    assert money.free_transfers(feed) == 4
    assert section.render(section.build(feed))[0].endswith("Free transfers 4")


def test_free_transfers_cap(feed):
    feed["bootstrap"]["game_settings"]["max_extra_free_transfers"] = 1
    assert money.free_transfers(feed) == 2


def test_free_transfers_used_and_hit(feed):
    feed["history"]["current"][2]["event_transfers"] = 1  # gw3: 2 -> 1 -> 2, one behind 5
    assert money.free_transfers(feed) == 4
    feed["history"]["current"][2]["event_transfers"] = 4  # hit; back to 0, +1
    assert money.free_transfers(feed) == 3


def test_chip_weeks_keep_count(feed):
    feed["history"]["current"][2]["event_transfers"] = 15
    feed["history"]["chips"] = [{"name": "wildcard", "event": 3}]
    assert money.free_transfers(feed) == 4  # gw3 adds no +1: 2 stays 2, then 3, 4


def test_free_hit_week_count_unchanged_no_plus_one(feed):
    # D32 example: 4 saved before GW29, Free Hit in GW29, still 4 for GW30.
    for e in feed["bootstrap"]["events"]:
        e["is_next"] = e["id"] == 30
    feed["history"]["current"] = [{"event": g, "event_transfers": 0, "event_transfers_cost": 0}
                                  for g in range(1, 30)]
    feed["history"]["current"][27]["event_transfers"] = 2  # gw28: 5 -> 3, +1 = 4 before gw29
    feed["history"]["current"][28]["event_transfers"] = 9  # gw29: Free Hit transfers
    feed["history"]["chips"] = [{"name": "freehit", "event": 29}]
    assert money.free_transfers(feed) == 4
    feed["history"]["chips"] = []
    feed["history"]["current"][28]["event_transfers"] = 0
    assert money.free_transfers(feed) == 5  # a normal week with no transfers would add 1


def test_hand_entered_transfers_use_free_transfers(feed):
    feed["bootstrap"]["elements"] += [player(20, 2, 1), player(21, 2, 1), player(22, 3, 1)]
    feed["this_week"] = {"gameweek": 6, "bank": 0.8, "transfers": [
        {"out": "P3", "in": "P20"}, {"out": "P4", "in": "P21"}]}
    assert money.free_transfers(feed) == 5 - 2
    feed["this_week"]["transfers"] += [{"out": f"P{o}", "in": f"P{i}"} for o, i in
                                       [(20, 3), (21, 4), (3, 20), (4, 21), (8, 22)]]
    assert money.free_transfers(feed) == 0  # 7 entered, never below 0


def test_player_bought_by_hand_sells_at_now_cost(feed):
    feed["bootstrap"]["elements"].append(player(20, 2, 1, cost=60, cost_change_start=10))
    feed["this_week"] = {"gameweek": 6, "transfers": [{"out": "P3", "in": "P20"}], "bank": 0}
    assert money.purchase_price(feed, feed["bootstrap"]["elements"][-1]) == 60


def test_render_line(feed):
    assert section.render(section.build(feed)) == ["Bank 0.5m · Free transfers 5"]
