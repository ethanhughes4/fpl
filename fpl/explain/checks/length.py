NAME = "length"
LIVE = False


def check(text, ctx):
    from fpl.explain import MAX_WORDS  # late: fpl.explain imports the checks
    n = len(text.split())
    return f"it used {n} words, over the limit of {MAX_WORDS}" if n > MAX_WORDS else None
