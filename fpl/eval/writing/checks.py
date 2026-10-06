"""Code checks as a scorer: one column per module in explain.check.CHECKS, live or not (D151)."""
from fpl.explain import check


def start(ctx):
    return []


def score(text, ctx):
    return {c.NAME: c.check(text, ctx) is None for c in check.CHECKS}


def summary(rows):
    """Pass rate over every check cell; passed only at 100% (D153)."""
    cells = [v for r in rows for v in r["scores"].values() if isinstance(v, bool)]
    rate = sum(cells) / len(cells) if cells else 0.0
    return [("code checks pass rate", f"{rate:.0%}", bool(cells) and rate == 1.0)]
