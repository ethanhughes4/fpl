"""Captain: real points of each formula's captain, the owner's, and the best in hindsight (D93)."""
from fpl import score
from fpl.sections import lineup


def columns(formula_names):
    return [f"captain {n}" for n in formula_names] + ["captain mine", "captain best"]


def measure(gw):
    by_id = {el["id"]: el for el in gw.feed["bootstrap"]["elements"]}
    squad = [p["element"] for p in gw.picks["picks"]]
    out = {}
    for name, scores in gw.scores.items():
        _, eleven, _ = lineup.best_eleven([(scores[i], by_id[i]) for i in squad])
        _, el = min(eleven, key=lambda x: score.sort_key(x[1], x[0]))
        out[f"captain {name}"] = gw.real.get(el["id"], 0)
    out["captain mine"] = next(
        (gw.real.get(p["element"], 0) for p in gw.picks["picks"] if p["is_captain"]), None)
    out["captain best"] = max(gw.real.get(i, 0) for i in squad)
    return out


def total(label, values):
    return sum(values)
