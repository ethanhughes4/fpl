from datetime import datetime


def when(iso):
    """'2026-10-10T10:00:00Z' -> 'Sat 10 Oct 12:00' in the PC's local time, as the text brief."""
    d = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()
    return f"{d:%a} {d.day} {d:%b %H:%M}"


def build(run):
    h = run["data"]["header"]
    return {"team": run["feed"]["entry"]["name"],  # D337, as is
            "gameweek": f"Gameweek {h['gameweek']}",
            "deadline": f"Deadline {when(h['deadline'])}"}
