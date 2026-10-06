from fpl import brief
from fpl.explain import block
from fpl.mcp import session

DESCRIPTION = (
    "This week's FPL brief for the owner's team: captain, starting eleven, transfers, "
    "injury warnings, close calls and each player's score breakdown. Upcoming gameweek only. "
    "Takes no arguments."
)


def tool() -> str:
    return session.reply(lambda feed: block.build(brief.build(feed), feed))
