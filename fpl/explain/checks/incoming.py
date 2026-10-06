"""D205: every suggested transfer's incoming player is named. Eval only."""
from fpl.explain.checks._mention import missing

NAME = "incoming"
LIVE = False


def check(text, ctx):
    name = missing(text, [t["in"] for t in ctx["data"]["transfers"]["transfers"]])
    return f"it did not name {name}, who comes in on a suggested transfer" if name else None
