"""Code checks as a scorer: one column per module in explain.check.CHECKS, live or not (D151)."""
from fpl.explain import check


def start(ctx):
    return []


def score(text, ctx):
    return {c.NAME: c.check(text, ctx) is None for c in check.CHECKS}


def summary(rows):
    """Share of explanations passing every check; passed only at 100% (D153)."""
    ok = [all(r["scores"][c.NAME] is True for c in check.CHECKS if c.NAME in r["scores"])
          for r in rows]
    rate = sum(ok) / len(ok) if ok else 0.0
    return [("code checks pass rate", f"{rate:.0%}", bool(ok) and rate == 1.0)]
