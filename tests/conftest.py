import socket

import pytest

from tests.fakefeed import make_feed


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refuse(*a, **k):
        raise RuntimeError("Network access in a test")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


@pytest.fixture(autouse=True)
def no_claude(monkeypatch):
    """No claude on the path unless a test installs tests.fakeclaude (D168)."""
    from fpl import claude

    monkeypatch.setattr(claude.shutil, "which", lambda name: None)


@pytest.fixture
def feed():
    return make_feed()
