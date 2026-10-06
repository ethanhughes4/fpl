"""The two shared lists and the loop over replayed gameweeks."""
from fpl.eval import replay
from fpl.eval.formulas import current
from fpl.eval.measures import captain, eleven, ranking

FORMULAS = [current]
MEASURES = [captain, eleven, ranking]


def run(data):
    """Dict: gameweeks, notes, n_finished, columns, rows {gw: {label: value}}, totals."""
    boot = data["bootstrap"]
    todo, notes, n_finished = replay.gameweeks(boot)
    owners = {label: m for m in MEASURES for label in m.columns([f.NAME for f in FORMULAS])}
    rows = {}
    for gw in todo:
        picks = data["picks"].get(gw)
        if picks is None:
            notes.append(f"GW{gw} no picks")  # D104
            continue
        feed = replay.as_of(boot, data["fixtures"], data["lives"], gw)
        scores = {f.NAME: f.scores(feed) for f in FORMULAS}
        g = replay.Gameweek(gw, feed, replay.real_points(data["lives"][gw]), picks, scores)
        rows[gw] = {k: v for m in MEASURES for k, v in m.measure(g).items()}
    totals = {}
    for label, m in owners.items():
        vals = [r[label] for r in rows.values() if r.get(label) is not None]
        totals[label] = m.total(label, vals) if vals else None
    return {"gameweeks": list(rows), "notes": notes, "n_finished": n_finished,
            "columns": list(owners), "rows": rows, "totals": totals}
