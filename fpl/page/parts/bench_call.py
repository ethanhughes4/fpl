from fpl.explain.parts import close


def sentence(c):
    """D334's four forms, from one close.calls() bench entry. No tag: the verdict is in the words."""
    start, bench = c["players"]
    a, b = c["numbers"]
    gap = c["gap"]
    ahead = (f"{start} is {gap:.1f} ahead" if gap > 0 else
             f"{bench} is {-gap:.1f} ahead" if gap < 0 else "They are level")
    verdict = "close" if c["close"] else "not close"
    return (f"{start} starts at {a:.1f}. {bench} is the best outfield player on the bench at {b:.1f}. "
            f"{ahead}, which is {verdict}.")


def build(run):
    c = next((c for c in close.calls(run["data"]) if c["kind"] == "bench"), None)
    return {"sentence": sentence(c) if c else None}
