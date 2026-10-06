import re
import unicodedata

NAME = "names"
LIVE = True


def _plain(s):
    """Accents removed, case kept."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def _norm(s):
    return _plain(s).casefold()


def _word(name):
    return re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)", re.IGNORECASE)


def _named(word, original):
    """D190: a name counts only with a capital first letter; a club code (NEW) only in capitals."""
    if original.isupper():
        return word.isupper()
    return word[0].isupper()


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
    rest = _plain(text)
    for n in sorted(allowed, key=len, reverse=True):
        rest = _word(n).sub(" ", rest)
    for n, original in banned.items():
        if n in allowed:
            continue
        if any(_named(m.group(), original) for m in _word(n).finditer(rest)):
            return f"it named {original}, who is not in the brief"
    return None
