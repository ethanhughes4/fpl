"""The brief's formula before D121: unshrunk base, kept so every run compares (D100)."""
from fpl import score

NAME = "current"


def scores(feed):
    return {el["id"]: score.next_score(feed, el, score.base(el)) for el in feed["bootstrap"]["elements"]}
