from pathlib import Path

import pytest

from fpl import feed as feedmod, manual, score
from fpl.explain.parts import breakdown
from fpl.mcp import names, session
from fpl.mcp.tools import get_players

DATA = Path(__file__).parent / "data"


def run(folder, *args):
    session.start(DATA / folder)
    return get_players.tool(list(args)).partition("\n\n")[2]


def row(name, printed, pts, id):
    return (name, printed, {"id": id, "total_points": pts})


def test_one_player_example_a_worked_by_hand():
    # Hart: base 8.0, 12 games, typical 7.6, K 3 -> (12x8.0 + 3x7.6)/15 = 7.92; next 7.9; six 7.92x4.5 = 35.6
    out = run("example_a", "Hart")
    assert "next-GW score 7.9" in out and "base 8.0 before shrink and 7.9 after" in out
    assert "T3, 8.0m, six-week score 35.6, status a, news: none, in your squad" in out
    assert "leads" not in out


def test_breakdown_line_is_the_shared_line():
    f = feedmod.load(DATA / "example_a")
    els = f["bootstrap"]["elements"]
    hart = next(e for e in els if e["web_name"] == "Hart")
    want = breakdown.line("Hart", hart, f, score.shrunk_bases(els), score.typical_bases(els))
    assert run("example_a", "Hart").startswith(want + "\n")


def test_two_players_example_a():
    # Marsh: (12x7.4 + 3x7.0)/15 = 7.32 -> next 7.3, six 7.32x4.5 = 32.9; Hart 7.9 / 35.6
    out = run("example_a", "Marsh", "Hart")
    assert out.splitlines()[-2:] == ["Next-GW: Hart leads; Marsh 0.6 behind.",
                                     "Six-week: Hart leads; Marsh 2.7 behind."]


def test_three_players_example_a():
    # Joss: (15x6.0 + 3x6.6)/18 = 6.1 -> next 6.1, six 27.4
    out = run("example_a", "Joss", "Hart", "Marsh")
    assert out.splitlines()[-2:] == ["Next-GW: Hart leads; Marsh 0.6 behind; Joss 1.8 behind.",
                                     "Six-week: Hart leads; Marsh 2.7 behind; Joss 8.2 behind."]


def test_leaders_differ_between_the_two_scores():
    nxt = [row("A", 7.2, 50, 1), row("B", 7.0, 40, 2), row("C", 6.5, 40, 3)]
    six = [row("A", 30.0, 50, 1), row("B", 33.4, 40, 2), row("C", 31.0, 40, 3)]
    assert get_players._gaps("Next-GW", nxt) == "Next-GW: A leads; B 0.2 behind; C 0.7 behind."
    assert get_players._gaps("Six-week", six) == "Six-week: B leads; C 2.4 behind; A 3.4 behind."


def test_level_and_tie_ordered_by_d27():
    # same printed 7.3: higher total points first (D), then lower id (B before C); A is 0.1 behind
    rows = [row("A", 7.2, 50, 1), row("B", 7.3, 40, 2), row("C", 7.3, 40, 3), row("D", 7.3, 60, 4)]
    assert get_players._gaps("Next-GW", rows) == (
        "Next-GW: D leads; B level with D; C level with D; A 0.1 behind.")


def test_gap_is_from_printed_values():
    # 7.3 vs 7.2 printed is 0.1 even if the unrounded gap was 0.19
    assert get_players._gaps("X", [row("A", 7.3, 1, 1), row("B", 7.2, 1, 2)]) == "X: A leads; B 0.1 behind."


def test_not_in_squad_example_b_and_c():
    assert "not in your squad" in run("example_b", "Wren")
    assert "not in your squad" in run("example_c", "Yates")
    assert ", in your squad" in run("example_b", "Cole")


def test_palmer_is_ambiguous_and_ids_pick_one():
    assert run("snapshot", "Palmer").splitlines() == [
        '"Palmer" matches more than one player; call again with the id:',
        "  Palmer, CHE, MID, 9.7m, id 154", "  Palmer, IPS, GK, 4.0m, id 301"]
    assert "Palmer (MID)" in run("snapshot", "154")
    assert run("snapshot", "Nobody") == 'No player matches "Nobody".'


def test_same_player_twice_counts_once():
    assert "leads" not in run("example_a", "Hart", "hart")


@pytest.mark.parametrize("n", [0, 5])
def test_count_limits(n):
    session.start(DATA / "example_a")
    out = get_players.tool(["Hart"] * n)
    assert out.startswith("Data downloaded ")  # D227
    assert out.endswith("\n\nGive between 1 and 4 players.")


def test_resolve_ids_and_matches():
    f = feedmod.load(DATA / "snapshot")
    pool = f["bootstrap"]["elements"]
    teams = {t["id"]: t["short_name"] for t in f["bootstrap"]["teams"]}
    assert names.resolve(154, pool, teams)["id"] == 154
    assert names.resolve("154", pool, teams)["id"] == 154
    assert manual.matches("Haaland", pool)[0]["id"] == 411

