import re

NAME = "numbers"
LIVE = True
# signs and a trailing m are not part of a match; "113,590" is one number (D264)
NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
LIST_MARKER = re.compile(r"^([ \t]*)\d+[.)](?=[ \t])", re.MULTILINE)  # "2. " or "3) " starting a line (D263)


def _value(n):
    return float(n.replace(",", ""))


def failures(text, ctx):
    """Every number quoted that is not in the block, in text order, each once."""
    allowed = {_value(n) for n in NUMBER.findall(ctx["block"])}
    text = LIST_MARKER.sub(r"\1", text)
    return list(dict.fromkeys(n for n in NUMBER.findall(text) if _value(n) not in allowed))


def check(text, ctx):
    bad = failures(text, ctx)
    return f"it quoted {bad[0]}, which is not in the brief" if bad else None
