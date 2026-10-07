import asyncio
from pathlib import Path

from mcp import Client

from fpl import feed as feedmod
from fpl.mcp import server, session
from fpl.mcp.tools import find_replacements as fr
from fpl.sections import transfers
from tests.fakefeed import player
from tests.test_mcp_server import loopback_only  # noqa: F401  (autouse, D252)

DATA = Path(__file__).parent / "data"


def run(folder, name):
    session.start(DATA / folder)
    return fr.tool(name).partition("\n\n")[2]


def star(id, pos=4, team=5, cost=55, base="9.0", **kw):
    return player(id, pos, team, cost, form=base, points_per_game=base, **kw)


def rows(feed, *cands, name="P13"):
    feed["bootstrap"]["elements"] += list(cands)
    return fr._body(name, feed).splitlines()[1:]  # fake feed: bank 5, P13 sells at 50


def test_example_b_hart_to_wren_and_bench_shaw():
    assert run("example_b", "Hart").splitlines() == [
        "Replacing Hart: bank 0.0m, selling price 8.0m, 2 options",
        "  Wren, T1, 7.8m, six-week gain +13.4, starts, clears free bar 2: yes, worth a 4-point hit, bar 8: yes",
        "  Shaw, T6, 4.5m, six-week gain -2.9, bench, half gain, clears free bar 2: no, worth a 4-point hit, bar 8: no"]


def test_example_c_lowe_to_yates():
    assert run("example_c", "Lowe").splitlines()[:2] == [
        "Replacing Lowe: bank 0.5m, selling price 4.5m, 2 options",
        "  Yates, T1, 5.0m, six-week gain +10.8, starts, clears free bar 2: yes, worth a 4-point hit, bar 8: yes"]


def test_example_a_nothing_clears_a_bar():
    out = run("example_a", "Hart")
    assert "clears free bar 2: yes" not in out and "worth a 4-point hit, bar 8: yes" not in out


def test_snapshot_tops_are_the_briefs_choices():
    sz = run("snapshot", "Szoboszlai").splitlines()
    assert sz[0] == "Replacing Szoboszlai: bank 0.0m, selling price 6.9m, 5 options"
    assert len(sz) == 1 + fr.TOP_REPLACEMENTS
    assert sz[1].startswith("  Schade, BRE, 6.2m, six-week gain +14.7, starts")
    assert run("snapshot", "O'Shea").splitlines()[1].startswith("  Davis, IPS, 4.0m, six-week gain +11.4")


def test_replacements_agree_with_the_brief():
    f = feedmod.load(DATA / "snapshot")
    sz = next(e for e in f["bootstrap"]["elements"] if e["web_name"] == "Szoboszlai")
    best = transfers.replacements(f, sz)[0]
    t = transfers.build(f)["transfers"][0]
    assert (best[1]["web_name"], best[2]["web_name"], best[0]) == (t["out"], t["in"], t["gain"])


def test_not_in_squad_and_no_match_start_with_data_line():
    session.start(DATA / "example_b")
    for arg, tail in (("Wren", "Wren is not in your squad."), ("Nobody", 'No player matches "Nobody".')):
        out = fr.tool(arg)
        assert out.startswith("Data downloaded ") and out.endswith("\n\n" + tail)


def test_too_expensive_excluded(feed):
    assert rows(feed, star(20, cost=56)) == ["No legal replacement."]  # 56 > bank 5 + sell 50


def test_exactly_affordable_included(feed):
    assert rows(feed, star(20, cost=55))[0].startswith("  P20")


def test_fourth_player_from_one_club_excluded(feed):
    # club 2 holds P1, P7, P13; P13 going out frees a slot, but P14 going out does not
    assert rows(feed, star(20, team=2))[0].startswith("  P20")
    assert not any("P21" in r for r in rows(feed, star(21, team=2), name="P14"))


def test_bench_only_incoming_shows_half_gain(feed):
    # P2 is the spare keeper; a new keeper cannot start ahead of P1
    out = rows(feed, star(20, pos=1, base="4.0", cost=50), name="P2")
    assert out[0].startswith("  P20") and "bench, half gain" in out[0]


def test_bars_at_exactly_2_and_8(feed, monkeypatch):
    el = {e["id"]: e for e in feed["bootstrap"]["elements"]}
    swaps = [(2.0, el[13], el[1], True), (8.0, el[13], el[2], True), (1.9, el[13], el[3], True)]
    monkeypatch.setattr(transfers, "replacements", lambda f, o: swaps)
    out = fr._body("P13", feed).splitlines()
    assert "gain +2.0, starts, clears free bar 2: yes, worth a 4-point hit, bar 8: no" in out[1]
    assert "gain +8.0, starts, clears free bar 2: yes, worth a 4-point hit, bar 8: yes" in out[2]
    assert "clears free bar 2: no" in out[3]


def test_top_five_only(feed):
    cands = [star(20 + k, base=f"{6 + k / 10}") for k in range(8)]
    assert len(rows(feed, *cands)) == fr.TOP_REPLACEMENTS


def test_option_count_is_the_rows_returned(feed):
    """D267: the count printed is the rows shown (top five), not every legal player."""
    feed["bootstrap"]["elements"] += [star(20 + k, base=f"{6 + k / 10}") for k in range(8)]
    assert fr._body("P13", feed).splitlines()[0].endswith(", 5 options")


def test_one_option_is_singular(feed):
    feed["bootstrap"]["elements"].append(star(20))
    out = fr._body("P13", feed).splitlines()
    assert len(out) == 2 and out[0].endswith(", 1 option")


def test_numeric_id_through_server():
    session.start(DATA / "snapshot")
    f = feedmod.load(DATA / "snapshot")
    sid = next(e["id"] for e in f["bootstrap"]["elements"] if e["web_name"] == "Szoboszlai")

    async def go():
        async with Client(server.build()) as c:
            return await c.call_tool("find_replacements", {"name": sid})

    assert "Schade" in asyncio.run(go()).content[0].text
