import re

NAME = "numbers"
LIVE = True
NUMBER = re.compile(r"\d+(?:\.\d+)?")  # signs and a trailing m are not part of a match


def check(text, ctx):
    allowed = {float(n) for n in NUMBER.findall(ctx["block"])}
    for n in NUMBER.findall(text):
        if float(n) not in allowed:
            return f"it quoted {n}, which is not in the brief"
    return None
