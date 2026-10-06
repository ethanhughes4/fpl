"""Close calls (D139, D140, D181). Takes the brief's data in, gives lines out. No network."""
from fpl.sections.transfers import MIN_FREE_GAIN, MIN_HIT_GAIN

CAPTAIN_CLOSE = 1.0
BENCH_CLOSE = 0.5
TRANSFER_CLOSE = 2.0


def _r(x):
    return round(x, 1)


def calls(data):
    """[{kind, players, numbers, gap (or margin), close}], every number rounded to 1 decimal first."""
    out = []
    cap, vice = data["captain"]["captain"], data["captain"]["vice"]
    a, b = _r(cap["score"]), _r(vice["score"])
    gap = _r(a - b)
    out.append({"kind": "captain", "players": [cap["name"], vice["name"]],
                "numbers": [a, b], "gap": gap, "close": gap <= CAPTAIN_CLOSE})

    outfield = lambda rows: [r for r in rows if r["position"] != "GK"]
    starters, bench = outfield(data["lineup"]["starters"]), outfield(data["lineup"]["bench"])
    if starters and bench:
        lo = min(starters, key=lambda r: _r(r["next"]))
        hi = max(bench, key=lambda r: _r(r["next"]))
        a, b = _r(lo["next"]), _r(hi["next"])
        gap = _r(a - b)
        out.append({"kind": "bench", "players": [lo["name"], hi["name"]],
                    "numbers": [a, b], "gap": gap, "close": gap <= BENCH_CLOSE})

    for t in data["transfers"]["transfers"]:
        gain, bar = _r(t["gain"]), (MIN_HIT_GAIN if t["hit"] else MIN_FREE_GAIN)
        margin = _r(gain - bar)
        out.append({"kind": "transfer", "players": [t["out"], t["in"]],
                    "numbers": [gain, bar], "gap": margin, "close": margin <= TRANSFER_CLOSE})
    return out


def _line(c):
    p, n = c["players"], c["numbers"]
    verdict = "close" if c["close"] else "not close"
    if c["kind"] == "captain":
        s = f"captain {p[0]} {n[0]:.1f} vs vice {p[1]} {n[1]:.1f}, gap {c['gap']:.1f}"
    elif c["kind"] == "bench":  # D199: who starts, who sits, and who is ahead, in full
        gap = c["gap"]
        ahead = (f"{p[0]} (starting) is ahead by {gap:.1f}" if gap > 0 else
                 f"{p[1]} (bench) is ahead by {-gap:.1f}" if gap < 0 else
                 f"they are level, gap {gap:.1f}")
        s = (f"bench call: {p[0]} starts as the lowest outfield starter with {n[0]:.1f}; "
             f"{p[1]} is the best outfield player on the bench with {n[1]:.1f}; {ahead}")
    else:
        s = (f"transfer {p[0]} -> {p[1]} gain {n[0]:+.1f} against a bar of {n[1]}, "
             f"margin {c['gap']:.1f}")
    return f"  {s}: {verdict}"


def lines(data, feed):
    return ["", "Close calls"] + [_line(c) for c in calls(data)]
