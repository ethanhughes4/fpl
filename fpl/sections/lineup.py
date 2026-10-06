from fpl import score, squad

GK, DEF, MID, FWD = 1, 2, 3, 4
POS_NAME = {GK: "GK", DEF: "DEF", MID: "MID", FWD: "FWD"}
DEF_RANGE = range(3, 6)
MID_RANGE = range(2, 6)
FWD_RANGE = range(1, 4)
OUTFIELD = 10


def _row(feed, el, s):
    return {"id": el["id"], "name": el["web_name"], "position": POS_NAME[el["element_type"]],
            "next": s, "six": score.six_week_score(feed, el)}


def pick_eleven(by_pos):
    """by_pos: {pos: [(score, el)]} each best first. Returns (formation, eleven)."""
    best = None
    for d in DEF_RANGE:
        for m in MID_RANGE:
            f = OUTFIELD - d - m
            need = {GK: 1, DEF: d, MID: m, FWD: f}
            if f not in FWD_RANGE or any(len(by_pos[p]) < n for p, n in need.items()):
                continue
            chosen = [x for p, n in need.items() for x in by_pos[p][:n]]
            total = sum(s for s, _ in chosen)
            if best is None or total > best[0]:
                best = (total, (d, m, f), chosen)
    return best[1], best[2]


def best_eleven(scored):
    """scored: [(next-GW score, el)] for a squad. Returns (formation, eleven, scored best first)."""
    scored = sorted(scored, key=lambda x: score.sort_key(x[1], x[0]))
    by_pos = {p: [x for x in scored if x[1]["element_type"] == p] for p in POS_NAME}
    formation, eleven = pick_eleven(by_pos)
    return formation, eleven, scored


def build(feed):
    formation, eleven, scored = best_eleven(
        [(score.next_score(feed, el), el) for el in squad.squad(feed)])
    ids = {el["id"] for _, el in eleven}
    # bench: spare keeper first, then outfielders best first
    rest = [x for x in scored if x[1]["id"] not in ids]
    rest.sort(key=lambda x: x[1]["element_type"] != GK)
    return {
        "formation": "-".join(map(str, formation)),
        "starters": [_row(feed, el, s) for s, el in eleven],
        "bench": [_row(feed, el, s) for s, el in rest],
    }


def render(data):
    def line(r):
        return f"  {r['position']:<3} {r['name']:<16} {r['next']:5.1f}  {r['six']:5.1f}"
    out = [f"Starting XI ({data['formation']})   next GW  6 GW"]
    out += [line(r) for r in data["starters"]]
    out.append("Bench")
    out += [line(r) for r in data["bench"]]
    return out
