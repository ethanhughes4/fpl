"""The five-tool server. To switch a tool on: add its file, add one line to TOOLS."""
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from fpl.mcp.tools import get_brief, get_players

TOOLS = [get_brief, get_players]

LIMITS = (
    "This server cannot see how long an injury will last, price rises or falls, other "
    "teams or rivals, and it cannot make transfers. If asked, say so; do not guess. "
    "Quote numbers exactly as given and do not compute new ones."
)


def build():
    server = MCPServer("fpl")
    for m in TOOLS:
        server.tool(name=m.__name__.rsplit(".", 1)[-1], description=f"{m.DESCRIPTION}\n\n{LIMITS}",
                    annotations=ToolAnnotations(readOnlyHint=True))(m.tool)
    return server
