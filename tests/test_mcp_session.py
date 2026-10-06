import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from fpl import download as dl
from fpl.mcp import session

SNAP = Path(__file__).parent / "data" / "snapshot"
NOW = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)  # deadline is 2026-10-10 10:00Z
AFTER = datetime(2026, 10, 11, 12, 0, tzinfo=timezone.utc)
STAMP = datetime(2026, 10, 6, 9, 14).timestamp()  # local time, as the header prints it


def BODY(feed):
    return "body"


class Fake:
    """Stands in for download.download: copies the snapshot to the first free folder name."""

    def __init__(self, error=None):
        self.calls, self.error = [], error

    def __call__(self, team, root, today, this_week):
        self.calls.append(team)
        if self.error:
            raise self.error
        name = f"{today:%Y-%m-%d}-gw06"
        folder, k = Path(root) / name, 1
        while folder.exists():
            k += 1
            folder = Path(root) / f"{name}-{k}"
        shutil.copytree(SNAP, folder)
        os.utime(folder / "bootstrap-static.json", (STAMP, STAMP))
        return folder


@pytest.fixture
def raw(tmp_path, monkeypatch):
    monkeypatch.setattr(session, "RAW", tmp_path)
    return tmp_path


def old_folder(raw, name):
    shutil.copytree(SNAP, raw / name)
    os.utime(raw / name / "bootstrap-static.json", (STAMP, STAMP))


def test_reuses_newest_of_today_with_future_deadline(raw):
    for n in ("2026-10-06-gw06", "2026-10-06-gw06-2", "2026-10-05-gw06", "2026-10-06-gw06-team9-2"):
        old_folder(raw, n)
    fake = Fake()
    session.start(download=fake, now=NOW)
    session.reply(BODY)
    assert fake.calls == []
    assert session._s["folder"].name == "2026-10-06-gw06-2"


def test_k_ten_beats_k_nine(raw):
    old_folder(raw, "2026-10-06-gw06-9")
    old_folder(raw, "2026-10-06-gw06-10")
    session.start(download=Fake(), now=NOW)
    session.reply(BODY)
    assert session._s["folder"].name == "2026-10-06-gw06-10"


def test_deadline_passed_downloads(raw):
    old_folder(raw, "2026-10-11-gw06")
    fake = Fake()
    session.start(download=fake, now=AFTER)
    session.reply(BODY)
    assert fake.calls == [dl.OWNER_TEAM]


def test_current_folder_dropped_after_deadline(raw):
    fake = Fake()
    session.start(download=fake, now=NOW)
    session.reply(BODY)
    session._s["now"] = AFTER
    session.reply(BODY)
    assert len(fake.calls) == 2


def test_no_folder_first_call_downloads_second_reuses(raw):
    fake = Fake()
    session.start(download=fake, now=NOW)
    session.reply(BODY)
    session.reply(BODY)
    assert len(fake.calls) == 1


def test_fresh_makes_new_folder(raw):
    fake = Fake()
    session.start(download=fake, now=NOW)
    session.reply(BODY)
    session.reply(BODY, fresh=True)
    assert sorted(p.name for p in raw.iterdir()) == ["2026-10-06-gw06", "2026-10-06-gw06-2"]
    assert session._s["folder"].name == "2026-10-06-gw06-2"


def test_from_never_downloads(raw):
    fake = Fake()
    session.start(SNAP, download=fake, now=AFTER)
    assert session.reply(BODY, fresh=True).endswith("\n\nbody")
    assert fake.calls == []


def test_header_text(raw):
    session.start(download=Fake(), now=NOW)
    assert session.reply(BODY) == "Data downloaded Tue 6 Oct 09:14, gameweek 6\n\nbody"


@pytest.mark.parametrize("error, text", [
    (dl.FeedError(503), "Could not reach FPL (HTTP 503). Try again later or use --from <folder>"),
    (dl.TeamNotFound(dl.OWNER_TEAM), f"Team {dl.OWNER_TEAM} not found."),
])
def test_feed_trouble_is_a_message_and_next_call_works(raw, error, text):
    fake = Fake(error)
    session.start(download=fake, now=NOW)
    assert session.reply(BODY) == text
    fake.error = None
    assert session.reply(BODY).endswith("body")


def test_failed_refresh_keeps_current_folder(raw):
    fake = Fake()
    session.start(download=fake, now=NOW)
    session.reply(BODY)
    fake.error = dl.FeedError(500)
    assert session.reply(BODY, fresh=True).startswith("Could not reach FPL")
    fake.error = None
    assert session.reply(BODY).endswith("body")
    assert len(fake.calls) == 2


def test_bad_this_week_gives_its_message(raw):
    from fpl import brief
    old_folder(raw, "2026-10-06-gw06")
    (raw / "2026-10-06-gw06" / "this-week.json").write_text("[]", encoding="utf-8")
    session.start(download=Fake(), now=NOW)
    out = session.reply(lambda feed: brief.build(feed))
    assert out == 'this-week.json needs "gameweek", "transfers" and "bank".'
