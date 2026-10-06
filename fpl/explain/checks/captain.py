from fpl.explain.checks._mention import missing

NAME = "captain"
LIVE = False


def check(text, ctx):
    name = ctx["data"]["captain"]["captain"]["name"]
    return f"it did not name the captain, {name}" if missing(text, [name]) else None
