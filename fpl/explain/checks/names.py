import re
import unicodedata
from functools import cache

NAME = "names"
LIVE = True


def _plain(s):
    """Accents removed, case kept."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def _norm(s):
    return _plain(s).casefold()


@cache  # about 2,400 feed names, more than re's own cache of 512 holds
def _word(name):
    return re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)", re.IGNORECASE)


def _named(word, original):
    """D190: a name counts only with a capital first letter; a club code (NEW) only in capitals."""
    if original.isupper():
        return word.isupper()
    return word[0].isupper()


def failures(text, ctx):
    """Every name used that is not in the block, as the feed spells it."""
    boot = ctx["feed"]["bootstrap"]
    block = _norm(ctx["block"])
    # each entity is (the name that shows it is in the brief, all its names)
    ents = [(p["web_name"], [p.get("web_name"), p.get("first_name"), p.get("second_name")])
            for p in boot["elements"]]
    ents += [(t["name"], [t.get("name"), t.get("short_name")]) for t in boot["teams"]]
    # a club whose code the block prints (opponent "SUN") is in the brief too
    codes = {t["name"] for t in boot["teams"] if t.get("short_name")
             and re.search(r"(?<!\w)" + re.escape(t["short_name"]) + r"(?!\w)", ctx["block"])}
    allowed, banned = set(), {}
    for key, names in ents:
        in_block = key in codes or _word(_norm(key)).search(block)
        for n in filter(None, names):
            if in_block:
                allowed.add(_norm(n))
            else:
                banned.setdefault(_norm(n), n)
    rest = _plain(text)
    for n in sorted(allowed, key=len, reverse=True):
        rest = _word(n).sub(" ", rest)
    return [original for n, original in banned.items()
            if n not in allowed and any(_named(m.group(), original) for m in _word(n).finditer(rest))]


def check(text, ctx):
    bad = failures(text, ctx)
    return f"it named {bad[0]}, who is not in the brief" if bad else None
