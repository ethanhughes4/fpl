from fpl.explain.checks._mention import missing

NAME = "warnings"
LIVE = False


def check(text, ctx):
    name = missing(text, [w["name"] for w in ctx["data"]["warnings"]])
    return f"it did not mention {name}, who has a warning" if name else None
