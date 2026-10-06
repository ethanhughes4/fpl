"""Small hand-made feed, same shape as fpl.feed.load(). Each call gives a fresh copy."""

UPCOMING = 6  # picks are from gameweek 5


def player(id, pos, team, cost=50, **kw):
    p = {
        "id": id, "web_name": f"P{id}", "element_type": pos, "team": team,
        "now_cost": cost, "cost_change_start": 0, "form": "5.0",
        "points_per_game": "5.0", "total_points": 30, "minutes": 450,
        "status": "a", "chance_of_playing_next_round": None, "news": "",
    }
    p.update(kw)
    return p


def fixture(id, event, home, away, hd=3, ad=3, finished=False):
    return {"id": id, "event": event, "team_h": home, "team_a": away,
            "team_h_difficulty": hd, "team_a_difficulty": ad, "finished": finished}


def transfer(element_in, element_out, event, in_cost=50, out_cost=50):
    return {"element_in": element_in, "element_out": element_out, "event": event,
            "element_in_cost": in_cost, "element_out_cost": out_cost,
            "time": "2026-09-20T10:00:00Z"}


def make_feed():
    # positions: 1 GK, 2 DEF, 3 MID, 4 FWD; 15-man squad ids 1-15 over 6 clubs
    squad = [(1, 1), (2, 1), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 3), (9, 3),
             (10, 3), (11, 3), (12, 3), (13, 4), (14, 4), (15, 4)]
    elements = [player(i, pos, 1 + i % 6) for i, pos in squad]
    events = [{"id": g, "is_next": g == UPCOMING, "is_current": g == UPCOMING - 1,
               "finished": g < UPCOMING, "deadline_time": f"2026-10-{g + 5:02d}T11:00:00Z"}
              for g in range(1, 39)]
    fixtures = []
    for gw in range(1, UPCOMING + 6):
        for k, (h, a) in enumerate([(1, 2), (3, 4), (5, 6)]):
            fixtures.append(fixture(gw * 10 + k, gw, h, a, finished=gw < UPCOMING))
    return {
        "bootstrap": {
            "events": events,
            "teams": [{"id": t, "name": f"Team{t}", "short_name": f"T{t}"} for t in range(1, 7)],
            "elements": elements,
            "game_settings": {"transfers_sell_on_fee": 0.5, "max_extra_free_transfers": 4},
        },
        "fixtures": fixtures,
        "entry": {"id": 1, "name": "Test FC"},
        "picks": {UPCOMING - 1: {
            "active_chip": None,
            "entry_history": {"event": UPCOMING - 1, "bank": 5, "value": 1000},
            "picks": [{"element": i, "position": n + 1, "multiplier": 1,
                       "is_captain": n == 0, "is_vice_captain": n == 1}
                      for n, (i, _) in enumerate(squad)],
        }},
        "history": {"current": [{"event": g, "event_transfers": 0, "event_transfers_cost": 0}
                                for g in range(1, UPCOMING)], "chips": []},
        "transfers": [],
    }
