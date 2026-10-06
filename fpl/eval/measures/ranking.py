"""Ranking: Spearman correlation of projected order with real points over the pool (D96, D97)."""
import statistics

from fpl.eval.pool import pool


def columns(formula_names):
    return [f"ranking {n}" for n in formula_names] + ["ranking price"]


def spearman(projected, real):
    try:
        return statistics.correlation(projected, real, method="ranked")
    except statistics.StatisticsError:  # D117: e.g. all projections equal
        return None


def measure(gw):
    players = pool(gw.feed, gw.gw)
    real = [gw.real.get(el["id"], 0) for el in players]
    out = {f"ranking {n}": spearman([s[el["id"]] for el in players], real)
           for n, s in gw.scores.items()}
    # D113: price ties broken by rebuilt total points, then lower id
    order = sorted(players, key=lambda el: (-el["now_cost"], -el["total_points"], el["id"]))
    place = {el["id"]: -i for i, el in enumerate(order)}
    out["ranking price"] = spearman([place[el["id"]] for el in players], real)
    return out


def total(label, values):
    return sum(values) / len(values)  # mean
