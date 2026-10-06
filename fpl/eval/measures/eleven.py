"""Eleven: real points of each formula's eleven, the owner's, and the best in hindsight (D94)."""
from fpl.sections import lineup


def columns(formula_names):
    return [f"eleven {n}" for n in formula_names] + ["eleven mine", "eleven best"]


def measure(gw):
    by_id = {el["id"]: el for el in gw.feed["bootstrap"]["elements"]}
    squad = [p["element"] for p in gw.picks["picks"]]
    out = {}
    for name, scores in gw.scores.items():
        _, eleven, _ = lineup.best_eleven([(scores[i], by_id[i]) for i in squad])
        out[f"eleven {name}"] = sum(gw.real.get(el["id"], 0) for _, el in eleven)
    out["eleven mine"] = sum(
        gw.real.get(p["element"], 0) for p in gw.picks["picks"] if p["position"] <= 11)
    scored = sorted(((gw.real.get(i, 0), by_id[i]) for i in squad), key=lambda x: -x[0])
    by_pos = {p: [x for x in scored if x[1]["element_type"] == p] for p in (1, 2, 3, 4)}
    _, best = lineup.pick_eleven(by_pos)
    out["eleven best"] = sum(s for s, _ in best)
    return out


def total(label, values):
    return sum(values)
