from fpl.explain.checks._mention import missing
from fpl.explain.parts import close

NAME = "close"
LIVE = False


def check(text, ctx):
    for c in close.calls(ctx["data"]):
        if c["close"] and (name := missing(text, c["players"])):
            return f"it did not mention {name}, in a close {c['kind']} call"
    return None
