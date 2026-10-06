"""The brief's own formula (D100)."""
from fpl import score

NAME = "current"


def scores(feed):
    return {el["id"]: score.next_score(feed, el) for el in feed["bootstrap"]["elements"]}
