import _socket
import asyncio
import socket
from pathlib import Path

import pytest
from mcp import Client

from fpl.mcp import server, session
from fpl.mcp.tools import get_brief

SNAP = Path(__file__).parent / "data" / "snapshot"


@pytest.fixture(autouse=True)
def loopback_only(monkeypatch):
    """asyncio's socketpair on Windows connects to 127.0.0.1; everything else stays refused."""
    def connect(self, addr):
        if addr[0] != "127.0.0.1":
            raise RuntimeError("Network access in a test")
        return _socket.socket.connect(self, addr)

    monkeypatch.setattr(socket.socket, "connect", connect)


async def _list_and_call():
    async with Client(server.build()) as c:
        return (await c.list_tools()).tools, await c.call_tool("get_brief", {})


def test_tools_listed_read_only_with_limits_and_call_matches():
    session.start(SNAP)
    tools, res = asyncio.run(_list_and_call())
    assert [t.name for t in tools] == [m.__name__.rsplit(".", 1)[-1] for m in server.TOOLS]
    for t in tools:
        assert t.annotations.read_only_hint is True
        assert t.description.endswith(server.LIMITS)
    assert res.content[0].text == get_brief.tool()


def test_numeric_id_accepted():
    """D229: a client may send an id as a JSON number; the SDK must not refuse it."""
    session.start(SNAP)

    async def go():
        async with Client(server.build()) as c:
            return await c.call_tool("get_players", {"names": [154]})

    out = asyncio.run(go()).content[0].text
    assert "Palmer" in out and "more than one" not in out
