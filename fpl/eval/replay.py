"""Rebuild the feed as it was before a deadline (D86-D89). Pure: data in, numbers out."""
from collections import defaultdict
from datetime import datetime, timedelta

FORM_DAYS = 30  # D87
FIRST_REPLAYED = 2  # D82: nothing is known before gameweek 1
KEEP = ("id", "first_name", "second_name", "web_name", "element_type", "team")


class Gameweek:
    """One replayed gameweek: rebuilt feed, real points, owner's picks, every formula's scores."""

    def __init__(self, gw, feed, real, picks, scores):
        self.gw, self.feed, self.real, self.picks, self.scores = gw, feed, real, picks, scores


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def checked(bootstrap):
    """Gameweeks whose points are final (D83)."""
    return [e["id"] for e in bootstrap["events"] if e["finished"] and e.get("data_checked")]


def gameweeks(bootstrap):
    """(gameweeks to replay, notes about skipped ones, number finished)."""
    done = checked(bootstrap)
    finished = [e["id"] for e in bootstrap["events"] if e["finished"]]
    notes = ["GW1 skipped"]
    notes += [f"GW{g} not data-checked" for g in finished if g not in done and g >= FIRST_REPLAYED]
    return [g for g in done if g >= FIRST_REPLAYED], notes, len(finished)


def real_points(live):
    """D92: {element id: total_points} from one live file."""
    return {e["id"]: e["stats"]["total_points"] for e in live["elements"]}


def as_of(bootstrap, fixtures, lives, gw, now=None):
    """A feed dict (shape of fpl.feed.load) as it stood at gameweek gw's deadline."""
    deadline = parse(next(e for e in bootstrap["events"] if e["id"] == gw)["deadline_time"])
    now = now or deadline
    kicked = {f["id"]: parse(f["kickoff_time"]) for f in fixtures if f.get("kickoff_time")}
    played = {fid for fid, k in kicked.items() if k < deadline}
    start = now - timedelta(days=FORM_DAYS)
    window = {fid for fid in played if start <= kicked[fid] < now}
    club_window = defaultdict(int)
    for f in fixtures:
        if f["id"] in window:
            club_window[f["team_h"]] += 1
            club_window[f["team_a"]] += 1

    acc = defaultdict(lambda: {"minutes": 0, "points": 0, "apps": 0, "window": 0})
    for g, live in lives.items():
        if g >= gw:
            continue
        for e in live["elements"]:
            a = acc[e["id"]]
            a["minutes"] += e["stats"]["minutes"]
            a["points"] += e["stats"]["total_points"]
            for row in e["explain"]:
                a["apps"] += any(s["identifier"] == "minutes" and s["value"] > 0
                                 for s in row["stats"])
                if row["fixture"] in window:
                    a["window"] += sum(s["points"] for s in row["stats"])

    elements = []
    for el in bootstrap["elements"]:
        a = acc[el["id"]]
        new = {k: el[k] for k in KEEP if k in el}
        n = club_window[el["team"]]
        new.update(
            now_cost=el["now_cost"] - el["cost_change_start"],  # start price, tenths
            minutes=a["minutes"], total_points=a["points"], appearances=a["apps"],
            points_per_game=round(a["points"] / a["apps"], 1) if a["apps"] else 0.0,
            form=round(a["window"] / n, 1) if n else 0.0,
            status="a", chance_of_playing_next_round=None, news="")
        elements.append(new)

    events = [{**e, "is_next": e["id"] == gw, "is_current": False} for e in bootstrap["events"]]
    # known simplification (D89): difficulty and club come from today's feed
    fx = [{**f, "finished": f["id"] in played} for f in fixtures]
    return {"bootstrap": {"events": events, "teams": bootstrap["teams"], "elements": elements},
            "fixtures": fx}
