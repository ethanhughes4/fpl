"""Current formula with each base pulled toward the typical base for position and price (D99)."""
import statistics
from fpl import score
from fpl.feed import num

NAME = "shrink"
K = 3  # pull strength, in matches


def shrunk_bases(elements):
    """{id: shrunk base}. A position with under 2 players or one price is left alone (D116)."""
    out = {el["id"]: score.base(el) for el in elements}
    for pos in {el["element_type"] for el in elements}:
        group = [el for el in elements if el["element_type"] == pos and num(el["minutes"]) > 0]
        prices = [el["now_cost"] for el in group]
        if len(group) < 2 or len(set(prices)) < 2:
            continue
        slope, icpt = statistics.linear_regression(prices, [score.base(el) for el in group])
        for el in group:
            n = el["appearances"]
            typical = slope * el["now_cost"] + icpt
            out[el["id"]] = (n * score.base(el) + K * typical) / (n + K)
    return out


def scores(feed):
    els = feed["bootstrap"]["elements"]
    bases = shrunk_bases(els)
    return {el["id"]: score.next_score(feed, el, bases[el["id"]]) for el in els}
