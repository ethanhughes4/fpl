import asyncio

from mcp import Client

from fpl.mcp import server, session
from tests.test_mcp_server import SNAP, loopback_only  # noqa: F401  (autouse fixture, D252)

NAMES = {"get_brief", "get_players", "find_replacements", "get_eval_results", "refresh"}


def test_exactly_five_read_only_tools():
    """D237: no sixth tool, no write tool."""
    session.start(SNAP)

    async def go():
        async with Client(server.build()) as c:
            return (await c.list_tools()).tools

    tools = asyncio.run(go())
    assert len(tools) == 5 and {t.name for t in tools} == NAMES
    assert all(t.annotations.read_only_hint is True for t in tools)
