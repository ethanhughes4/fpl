import re
import unicodedata

NAME = "names"
LIVE = True


def _norm(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).casefold()


def _word(name):
    return re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)")


def check(text, ctx):
    boot = ctx["feed"]["bootstrap"]
    block = _norm(ctx["block"])
    # each entity is (the name that shows it is in the brief, all its names)
    ents = [(p["web_name"], [p.get("web_name"), p.get("first_name"), p.get("second_name")])
            for p in boot["elements"]]
    ents += [(t["name"], [t.get("name"), t.get("short_name")]) for t in boot["teams"]]
    allowed, banned = set(), {}
    for key, names in ents:
        in_block = _word(_norm(key)).search(block)
        for n in filter(None, names):
            if in_block:
                allowed.add(_norm(n))
            else:
                banned.setdefault(_norm(n), n)
    rest = _norm(text)
    for n in sorted(allowed, key=len, reverse=True):
        rest = _word(n).sub(" ", rest)
    for n, original in banned.items():
        if n not in allowed and _word(n).search(rest):
            return f"it named {original}, who is not in the brief"
    return None
