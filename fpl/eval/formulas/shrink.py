"""Base pulled toward the typical base for position and price (D99); the brief's formula since D121."""
from fpl import score

NAME = "shrink"


def scores(feed):
    bases = score.shrunk_bases(feed["bootstrap"]["elements"])
    return {el["id"]: score.next_score(feed, el, bases[el["id"]]) for el in feed["bootstrap"]["elements"]}
