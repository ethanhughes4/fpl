"""Download for the eval into data/raw/YYYY-MM-DD-eval/ and read it back (D84, D85)."""
import json
from datetime import date
from pathlib import Path

from fpl.download import RAW_DIR, TeamNotFound, _get
from fpl.eval import replay
from fpl.feed import MissingFile


def _name(kind, gw):
    return f"{kind}-gw{gw:02d}.json"


def download(team, root=RAW_DIR, today=None):
    """Returns the folder. Files already there are reused, never rewritten (D85, D111)."""
    _get(f"entry/{team}/", team)  # team check only; not saved
    folder = Path(root) / f"{today or date.today():%Y-%m-%d}-eval"
    folder.mkdir(parents=True, exist_ok=True)

    def get(name, path, team=None):
        file = folder / name
        if file.is_file():
            return json.loads(file.read_text(encoding="utf-8"))
        try:
            data = _get(path, team)
        except TeamNotFound:
            return None  # no picks: the team did not exist yet
        file.write_text(json.dumps(data), encoding="utf-8")
        return data

    boot = get("bootstrap-static.json", "bootstrap-static/")
    get("fixtures.json", "fixtures/")
    for gw in replay.checked(boot):
        get(_name("live", gw), f"event/{gw}/live/")
        get(_name("picks", gw), f"entry/{team}/event/{gw}/picks/", team)
    return folder


def load(folder):
    """Dict: bootstrap, fixtures, lives {gw: data}, picks {gw: data} (picks optional)."""
    folder = Path(folder)

    def read(name, required=True):
        path = folder / name
        if not path.is_file():
            if required:
                raise MissingFile(name)
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    boot = read("bootstrap-static.json")
    data = {"bootstrap": boot, "fixtures": read("fixtures.json"), "lives": {}, "picks": {}}
    for gw in replay.checked(boot):
        data["lives"][gw] = read(_name("live", gw))
        picks = read(_name("picks", gw), required=False)
        if picks is not None:
            data["picks"][gw] = picks
    return data
