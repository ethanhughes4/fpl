from datetime import datetime

from fpl import manual
from fpl.feed import upcoming

NOTE_NO_FILE = ("Shows your team at the last deadline. "
                "Transfers made since are not visible in the public feed.")  # D69


def build(feed):
    ev = upcoming(feed)
    st = manual.status(feed)
    return {"gameweek": ev["id"], "deadline": ev["deadline_time"], "this_week": st,
            "entered": len(manual.swaps(feed)),
            "file_gameweek": feed["this_week"]["gameweek"] if st == "ignored" else None}


def render(data):
    d = datetime.fromisoformat(data["deadline"].replace("Z", "+00:00")).astimezone()
    line = f"Gameweek {data['gameweek']} · deadline {d:%a} {d.day} {d:%b %H:%M}"
    if data["this_week"] == "used":
        n = data["entered"]
        if n:
            return [f"{line} · includes {n} transfer{'' if n == 1 else 's'} entered by hand"]
        return [f"{line} · bank entered by hand"]  # D68: file with no transfers
    out = [line]
    if data["this_week"] == "ignored":
        out.append(f"{manual.FILE} is for gameweek {data['file_gameweek']}, "
                   f"not {data['gameweek']}: ignored.")
    return out + [NOTE_NO_FILE]
