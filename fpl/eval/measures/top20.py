"""Top 20: average real points of the TOP_N highest projected (or dearest) players in the pool (D98)."""
from fpl.eval.pool import pool

TOP_N = 20


def columns(formula_names):
    return [f"top20 {n}" for n in formula_names] + ["top20 price"]


def average(players, key, real):
    # D113: ties by higher rebuilt total points, then lower id
    best = sorted(players, key=lambda el: (-key(el), -el["total_points"], el["id"]))[:TOP_N]
    return sum(real.get(el["id"], 0) for el in best) / len(best) if best else None


def measure(gw):
    players = pool(gw.feed, gw.gw)
    out = {f"top20 {n}": average(players, lambda el, s=s: s[el["id"]], gw.real)
           for n, s in gw.scores.items()}
    out["top20 price"] = average(players, lambda el: el["now_cost"], gw.real)
    return out


def total(label, values):
    return sum(values)  # D102: sum
