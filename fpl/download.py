"""Fetch the feed and save it to data/raw/YYYY-MM-DD-gwNN/."""
import json
import shutil
from datetime import date
from pathlib import Path

import requests

BASE = "https://fantasy.premierleague.com/api/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
TIMEOUT = 30
RAW_DIR = Path("data/raw")
OWNER_TEAM = 8027067
THIS_WEEK =Path("this-week.json")  # owner's hand-entered transfers, repo root (D65)


class FeedError(Exception):
    def __init__(self, code):
        self.code = code


class TeamNotFound(Exception):
    pass


class NoUpcomingGameweek(Exception):
    pass


def _get(path, team=None):
    try:
        r = requests.get(BASE + path, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    except requests.RequestException:
        raise FeedError("no response")
    if r.status_code == 404 and team is not None:
        raise TeamNotFound(team)
    if r.status_code != 200:
        raise FeedError(r.status_code)
    return r.json()


def download(team, root=RAW_DIR, today=None, this_week=THIS_WEEK):
    """Returns the folder written. Copies this_week beside the feed if it exists, so --from replays it."""
    boot = _get("bootstrap-static/")
    nxt = next((e["id"] for e in boot["events"] if e["is_next"]), None)
    if nxt is None:
        raise NoUpcomingGameweek()
    files = {"bootstrap-static": boot, "fixtures": _get("fixtures/")}
    for name, path in [("entry", ""), ("history", "history/"), ("transfers", "transfers/")]:
        files[name] = _get(f"entry/{team}/{path}", team)
    last = nxt - 1
    files[f"picks-gw{last:02d}"] = picks = _get(f"entry/{team}/event/{last}/picks/", team)
    if picks.get("active_chip") == "freehit":
        files[f"picks-gw{last - 1:02d}"] = _get(f"entry/{team}/event/{last - 1}/picks/", team)
    name = f"{today or date.today():%Y-%m-%d}-gw{nxt:02d}" + ("" if team == OWNER_TEAM else f"-team{team}")
    Path(root).mkdir(parents=True, exist_ok=True)
    folder, k = Path(root) / name, 1
    while True:  # never overwrite: first free name (D218)
        try:
            folder.mkdir(exist_ok=False)
            break
        except FileExistsError:
            k += 1
            folder = Path(root) / f"{name}-{k}"
    for name, data in files.items():
        (folder / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
    if Path(this_week).is_file():
        shutil.copyfile(this_week, folder / Path(this_week).name)
    return folder
