from fpl import score
from fpl.sections import lineup


def build(feed):
    els = {e["id"]: e for e in feed["bootstrap"]["elements"]}
    ranked = sorted(lineup.build(feed)["starters"],
                    key=lambda r: score.sort_key(els[r["id"]], r["next"]))
    pick = lambda r: {"id": r["id"], "name": r["name"], "score": r["next"]}
    return {"captain": pick(ranked[0]), "vice": pick(ranked[1])}


def render(data):
    c, v = data["captain"], data["vice"]
    return [f"Captain: {c['name']} ({c['score']:.1f})", f"Vice: {v['name']} ({v['score']:.1f})"]
