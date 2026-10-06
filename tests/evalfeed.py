"""Small hand-made eval data: what fpl.eval.download.load gives. Each call gives a fresh copy.

Gameweeks 1-5 are finished and checked, 6 is next. Six clubs, three matches a
gameweek (1v2, 3v4, 5v6). Players 1-15 are the owner's squad in every gameweek.
Kick-off is 15:00 on 2026-08-15 + 7 days per gameweek; deadline the day before 11:00.
"""
import json
from datetime import datetime, timedelta, timezone

FIRST_KICKOFF = datetime(2026, 8, 15, 15, 0, tzinfo=timezone.utc)
POSITIONS = [1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4]  # element 1..15
PAIRS = [(1, 2), (3, 4), (5, 6)]


def kickoff(gw):
    return FIRST_KICKOFF + timedelta(days=7 * (gw - 1))


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def club(i):
    return 1 + i % 6


def default_points(i, gw):
    return (i * gw) % 6 + 2


def make_eval(points=default_points, gws=5):
    """points(element id, gw) -> real points for a player who plays 90 minutes."""
    events = [{"id": g, "deadline_time": iso(kickoff(g) - timedelta(hours=28)),
               "finished": g <= gws, "data_checked": g <= gws,
               "is_next": g == gws + 1, "is_current": g == gws} for g in range(1, 39)]
    elements = [{"id": i, "first_name": "F", "second_name": f"S{i}", "web_name": f"P{i}",
                 "element_type": pos, "team": club(i), "now_cost": 50 + i,
                 "cost_change_start": 3, "form": "9.9", "points_per_game": "9.9",
                 "total_points": 99, "minutes": 999, "status": "d",
                 "chance_of_playing_next_round": 25, "news": "knock"}
                for i, pos in enumerate(POSITIONS, 1)]
    fixtures = [{"id": g * 10 + k, "event": g, "team_h": h, "team_a": a,
                 "team_h_difficulty": 3, "team_a_difficulty": 3, "finished": g <= gws,
                 "kickoff_time": iso(kickoff(g))}
                for g in range(1, gws + 2) for k, (h, a) in enumerate(PAIRS)]
    fixture_of = {(g, t): g * 10 + k for g in range(1, gws + 2)
                  for k, pair in enumerate(PAIRS) for t in pair}
    lives = {}
    for g in range(1, gws + 1):
        rows = []
        for i in range(1, len(POSITIONS) + 1):
            p = points(i, g)
            rows.append({"id": i, "stats": {"minutes": 90, "total_points": p},
                         "explain": [{"fixture": fixture_of[(g, club(i))], "stats": [
                             {"identifier": "minutes", "points": 2, "value": 90},
                             {"identifier": "goals_scored", "points": p - 2, "value": 1}]}]})
        lives[g] = {"elements": rows}
    picks = {g: {"active_chip": None, "picks": [
        {"element": i, "position": i, "multiplier": 1, "is_captain": i == 1,
         "is_vice_captain": i == 2} for i in range(1, len(POSITIONS) + 1)]}
        for g in range(1, gws + 1)}
    return {"bootstrap": {"events": events, "teams": [{"id": t, "name": f"T{t}"} for t in range(1, 7)],
                          "elements": elements},
            "fixtures": fixtures, "lives": lives, "picks": picks}


def write_folder(data, folder):
    """Save as fpl.eval.download would. Returns the folder."""
    def put(name, obj):
        (folder / name).write_text(json.dumps(obj), encoding="utf-8")

    folder.mkdir(parents=True, exist_ok=True)
    put("bootstrap-static.json", data["bootstrap"])
    put("fixtures.json", data["fixtures"])
    for g, live in data["lives"].items():
        put(f"live-gw{g:02d}.json", live)
    for g, picks in data["picks"].items():
        put(f"picks-gw{g:02d}.json", picks)
    return folder
