from fpl import money
from fpl.sections import transfers


def build(run):
    """Rows as the text brief prints them (D289, D296); the empty and hit lines are its exact words (D295, D335)."""
    data = run["data"]["transfers"]
    lines = transfers.render(data)
    rows = []
    for t in data["transfers"]:
        tags = ([f"−{transfers.HIT_COST} hit"] if t["hit"] else []) + ([] if t["starts"] else ["bench, half gain"])
        rows.append({"out": t["out"], "in": t["in"],
                     "prices": f"{money.price(t['out_price'])} → {money.price(t['in_price'])}",
                     "gain": f"{t['gain']:+.1f}", "tags": tags})
    return {"rows": rows,
            "hit_line": lines[-1].strip() if data["hit_points"] else None,
            "empty": None if rows else lines[0]}
