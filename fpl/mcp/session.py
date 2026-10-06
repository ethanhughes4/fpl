"""The one data folder the server serves (D227, D240, D241, D228). Only this file downloads."""
import re
from datetime import datetime, timezone
from pathlib import Path

from fpl import download as dl, feed as feedmod
from fpl.manual import ManualError

ROOT = Path(__file__).parents[2]  # repo root, so the eval can run claude elsewhere
RAW = ROOT / "data" / "raw"
THIS_WEEK = ROOT / "this-week.json"
BOOTSTRAP = "bootstrap-static.json"
FOLDER = re.compile(r"(\d{4}-\d\d-\d\d)-gw(\d\d)(?:-(\d+))?")  # not -team / -eval folders

_s = {}


def start(folder=None, download=dl.download, now=None):
    """Reset the session. folder: serve it always, never download. now: clock, for tests."""
    _s.clear()
    _s.update(fixed=folder is not None, folder=Path(folder) if folder else None,
              download=download, now=now)


def _now():
    return _s["now"] or datetime.now(timezone.utc)


def _live(folder):
    """True while the folder's upcoming gameweek still has a deadline in the future (D240)."""
    try:
        ev = feedmod.upcoming(feedmod.load(folder))
    except feedmod.MissingFile:
        return False
    return ev is not None and datetime.fromisoformat(ev["deadline_time"].replace("Z", "+00:00")) > _now()


def _today_newest():
    today = f"{_now().astimezone():%Y-%m-%d}"
    found = [(int(m[2]), int(m[3] or 1), p) for p in RAW.glob(f"{today}-gw*")
             if (m := FOLDER.fullmatch(p.name)) and m[1] == today]
    return max(found)[2] if found else None


def _pick(fresh):
    if _s["fixed"]:
        return _s["folder"]
    if not fresh:
        for f in (_s["folder"], _today_newest()):
            if f is not None and _live(f):
                return f
    return _s["download"](dl.OWNER_TEAM, root=RAW, today=_now().astimezone().date(),
                          this_week=THIS_WEEK)


def reply(body, fresh=False):
    """Header + body(feed), or one message. Never raises for feed trouble (D228)."""
    try:
        folder = _pick(fresh)
        feed = feedmod.load(folder)
        ev = feedmod.upcoming(feed)
        if ev is None:
            return "No upcoming gameweek."
        _s["folder"] = folder
        text = body(feed)
    except dl.FeedError as e:
        return f"Could not reach FPL (HTTP {e.code}). Try again later or use --from <folder>"
    except dl.TeamNotFound:
        return f"Team {dl.OWNER_TEAM} not found."
    except feedmod.MissingFile as e:
        return f"Missing file: {e}"
    except dl.NoUpcomingGameweek:
        return "No upcoming gameweek."
    except ManualError as e:
        return str(e)
    when = datetime.fromtimestamp((folder / BOOTSTRAP).stat().st_mtime)
    return f"Data downloaded {when:%a} {when.day} {when:%b %H:%M}, gameweek {ev['id']}\n\n{text}"


def folder_name():
    """Name of the folder being served, or None before the first reply."""
    return _s["folder"].name if _s.get("folder") else None
