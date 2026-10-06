import json
import shutil
import socket
from pathlib import Path

import pytest

from fpl import feed as feedmod

SNAP = Path(__file__).parent / "data" / "snapshot"


def test_num():
    assert feedmod.num("6.0") == 6.0
    assert feedmod.num(3) == 3
    assert feedmod.num(None) == 0
    assert feedmod.num("") == 0


def test_upcoming(feed):
    assert feedmod.upcoming(feed)["id"] == 6
    for e in feed["bootstrap"]["events"]:
        e["is_next"] = False
    assert feedmod.upcoming(feed) is None


def test_load_snapshot():
    f = feedmod.load(SNAP)
    assert f["picks"] and feedmod.upcoming(f)


def test_missing_file_named(tmp_path):
    shutil.copytree(SNAP, tmp_path / "s")
    (tmp_path / "s" / "history.json").unlink()
    with pytest.raises(feedmod.MissingFile, match="history.json"):
        feedmod.load(tmp_path / "s")


def test_network_guard_trips():
    with pytest.raises(RuntimeError):
        socket.create_connection(("example.com", 80))
