import json
from datetime import date

import pytest

from fpl.download import FeedError, TeamNotFound
from fpl.eval import download as dl
from fpl.feed import MissingFile
from tests.evalfeed import make_eval, write_folder

TODAY = date(2026, 10, 6)


class Resp:
    def __init__(self, code, data=None):
        self.status_code, self._data = code, data

    def json(self):
        return self._data


@pytest.fixture
def feed(monkeypatch):
    """Fake requests.get. Returns (calls, status overrides by path)."""
    d = make_eval()
    routes = {"bootstrap-static/": d["bootstrap"], "fixtures/": d["fixtures"], "entry/7/": {"id": 7}}
    for g in range(1, 6):
        routes[f"event/{g}/live/"] = d["lives"][g]
        routes[f"entry/7/event/{g}/picks/"] = d["picks"][g]
    calls, status = [], {}

    def get(url, headers=None, timeout=None):
        path = url.split("/api/")[1]
        calls.append(path)
        return Resp(status.get(path, 200), routes[path])

    monkeypatch.setattr("fpl.download.requests.get", get)
    return calls, status


def test_folder_and_file_names(feed, tmp_path):
    folder = dl.download(7, tmp_path, TODAY)
    assert folder == tmp_path / "2026-10-06-eval"
    names = sorted(p.name for p in folder.iterdir())
    want = ["bootstrap-static.json", "fixtures.json"]
    want += [f"{k}-gw{g:02d}.json" for k in ("live", "picks") for g in range(1, 6)]
    assert names == sorted(want)  # the team check is not saved
    assert dl.load(folder)["lives"].keys() == {1, 2, 3, 4, 5}


def test_existing_files_are_reused(feed, tmp_path):
    calls, _ = feed
    folder = dl.download(7, tmp_path, TODAY)
    (folder / "live-gw02.json").write_text('{"mine": 1}')
    (folder / "bootstrap-static.json").unlink()
    calls.clear()
    dl.download(7, tmp_path, TODAY)
    assert sorted(calls) == ["bootstrap-static/", "entry/7/"]
    assert json.loads((folder / "live-gw02.json").read_text()) == {"mine": 1}


def test_picks_404_saves_nothing(feed, tmp_path):
    _, status = feed
    status["entry/7/event/1/picks/"] = 404
    folder = dl.download(7, tmp_path, TODAY)
    assert not (folder / "picks-gw01.json").exists()
    assert (folder / "picks-gw02.json").exists()
    assert 1 not in dl.load(folder)["picks"]


def test_team_404(feed, tmp_path):
    feed[1]["entry/7/"] = 404
    with pytest.raises(TeamNotFound):
        dl.download(7, tmp_path, TODAY)


def test_http_500(feed, tmp_path):
    feed[1]["bootstrap-static/"] = 500
    with pytest.raises(FeedError) as e:
        dl.download(7, tmp_path, TODAY)
    assert e.value.code == 500


def test_load_missing_live_file_is_named(tmp_path):
    folder = write_folder(make_eval(), tmp_path / "f")
    (folder / "live-gw04.json").unlink()
    with pytest.raises(MissingFile, match="live-gw04.json"):
        dl.load(folder)


def test_load_missing_picks_is_fine(tmp_path):
    folder = write_folder(make_eval(), tmp_path / "f")
    (folder / "picks-gw04.json").unlink()
    assert 4 not in dl.load(folder)["picks"]
