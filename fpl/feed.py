"""Load a saved download folder into one dict. No network here."""
import json
import re
from pathlib import Path

FILES = ["bootstrap-static", "fixtures", "entry", "history", "transfers"]


class MissingFile(Exception):
    pass


def num(x):
    """Text, number or None to a number. Null, missing or '' = 0."""
    if x is None or x == "":
        return 0
    return float(x)


def load(folder):
    """Dict: bootstrap, fixtures, entry, history, transfers, picks {gw: data}."""
    folder = Path(folder)

    def read(path):
        if not path.is_file():
            raise MissingFile(path.name)
        return json.loads(path.read_text(encoding="utf-8"))

    feed = {f.replace("-static", ""): read(folder / f"{f}.json") for f in FILES}
    feed["picks"] = {
        int(re.search(r"(\d+)", p.stem).group(1)): read(p)
        for p in folder.glob("picks-gw*.json")
    }
    if not feed["picks"]:
        raise MissingFile("picks-gwNN.json")
    return feed


def upcoming(feed):
    """The event with is_next, or None."""
    return next((e for e in feed["bootstrap"]["events"] if e.get("is_next")), None)
