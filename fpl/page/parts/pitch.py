"""The pitch and bench: players as ready-to-show text (D289, D292, D293)."""
from fpl.sections.lineup import POS_NAME

BENCH_LABELS = ["GK", "1st", "2nd", "3rd"]  # spare keeper first, then outfielders best first


def _player(r, roles, doubts):
    d = doubts.get(r["id"])
    return {"name": r["name"], "next": f"{r['next']:.1f}", "six": f"{r['six']:.1f}",
            "role": roles.get(r["id"]),
            "doubt": None if d is None else "No match" if d["blank"] else f"{d['chance']}% to play"}


def build(run):
    d = run["data"]
    roles = {d["captain"]["captain"]["id"]: "CAPTAIN", d["captain"]["vice"]["id"]: "VICE"}
    doubts = {w["id"]: w for w in d["warnings"]}
    rows = [[_player(r, roles, doubts) for r in d["lineup"]["starters"] if r["position"] == pos]
            for pos in POS_NAME.values()]  # goalkeeper row first
    bench = [{"label": label, **_player(r, roles, doubts)}
             for label, r in zip(BENCH_LABELS, d["lineup"]["bench"])]
    return {"rows": [{"players": r} for r in rows if r], "bench": bench}
