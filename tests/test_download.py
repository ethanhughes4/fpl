from datetime import date

import pytest
import requests

from fpl import download as dl
from tests.fakefeed import make_feed


class Resp:
    def __init__(self, data, code=200):
        self.data, self.status_code = data, code

    def json(self):
        return self.data


def fake_get(calls, freehit=False, code=None):
    f = make_feed()
    pk = {"active_chip": "freehit" if freehit else None, "picks": []}

    def get(url, headers=None, timeout=None):
        calls.append((url, headers, timeout))
        if code:
            return Resp({}, code)
        p = url.replace(dl.BASE, "")
        if p == "bootstrap-static/":
            return Resp(f["bootstrap"])
        if "picks" in p:
            return Resp(pk)
        return Resp({})
    return get


def run(monkeypatch, tmp_path, **kw):
    calls = []
    monkeypatch.setattr(requests, "get", fake_get(calls, **kw))
    # this-week.json path inside tmp_path, so an owner's real file in the repo root is never read
    return calls, lambda: dl.download(1, tmp_path / "raw", date(2026, 10, 6),
                                      this_week=tmp_path / "this-week.json")


def test_files_and_request_options(monkeypatch, tmp_path):
    calls, go = run(monkeypatch, tmp_path)
    folder = go()
    assert folder.name == "2026-10-06-gw06"
    assert sorted(p.name for p in folder.iterdir()) == sorted(
        f"{n}.json" for n in ["bootstrap-static", "fixtures", "entry", "history", "transfers", "picks-gw05"])
    assert all(c[2] == 30 and "Mozilla" in c[1]["User-Agent"] for c in calls)
    assert go() == folder  # same day overwrites


def test_free_hit_fetches_earlier_picks(monkeypatch, tmp_path):
    _, go = run(monkeypatch, tmp_path, freehit=True)
    assert (go() / "picks-gw04.json").is_file()


def test_http_500_and_404(monkeypatch, tmp_path):
    _, go = run(monkeypatch, tmp_path, code=500)
    with pytest.raises(dl.FeedError) as e:
        go()
    assert e.value.code == 500
    _, go = run(monkeypatch, tmp_path, code=404)
    with pytest.raises(dl.FeedError):  # bootstrap 404 is a feed problem
        go()


def test_team_404(monkeypatch, tmp_path):
    f = make_feed()
    monkeypatch.setattr(requests, "get", lambda url, **k: Resp(f["bootstrap"]) if "bootstrap" in url
                        else Resp({}, 200 if "fixtures" in url else 404))
    with pytest.raises(dl.TeamNotFound):
        dl.download(1, tmp_path)


def test_this_week_file_copied_beside_feed(monkeypatch, tmp_path):
    _, go = run(monkeypatch, tmp_path)
    (tmp_path / "this-week.json").write_text('{"gameweek": 6}', encoding="utf-8")
    folder = go()
    assert (folder / "this-week.json").read_text(encoding="utf-8") == '{"gameweek": 6}'
    (tmp_path / "this-week.json").unlink()  # owner deletes it, reruns the same day
    assert not (go() / "this-week.json").exists()
