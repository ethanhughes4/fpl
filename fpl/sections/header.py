from datetime import datetime

from fpl.feed import upcoming


def build(feed):
    ev = upcoming(feed)
    return {"gameweek": ev["id"], "deadline": ev["deadline_time"]}


def render(data):
    d = datetime.fromisoformat(data["deadline"].replace("Z", "+00:00")).astimezone()
    return [f"Gameweek {data['gameweek']} · deadline {d:%a} {d.day} {d:%b %H:%M}"]
