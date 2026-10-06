"""The brief as the model reads it (D138, D199): the printed brief, with transfers labelled as
suggestions, the net gain after a hit, and playing chance in words. No network."""
from fpl import brief
from fpl.sections import transfers, warnings

TRANSFERS_LABEL = "Suggested transfers (not made yet)"
# (highest chance %, words), first match wins; chance comes from the feed, never a guess
CHANCE_WORDS = [(0, "ruled out"), (49, "likely to miss"), (99, "doubtful"), (100, "expected to play")]


def chance_text(pct):
    """'chance of playing: 25% (likely to miss)': cannot be read as injury risk (D199)."""
    words = next(w for top, w in CHANCE_WORDS if pct <= top)
    return f"chance of playing: {pct}% ({words})"


def _transfers(d):
    out = transfers.render(d)
    if not d["transfers"]:
        return out
    out[0] = TRANSFERS_LABEL
    rows = iter(d["transfers"])
    labelled = []
    for line in out:
        labelled.append(line)
        if line.startswith("  ") and "->" in line:
            t = next(rows)
            if t["hit"]:  # from the printed gain, as the owner would subtract it (D140)
                net = round(round(t["gain"], 1) - transfers.HIT_COST, 1)
                labelled.append(f"    net gain after the {transfers.HIT_COST}-point hit {net:+.1f}")
    return labelled


def _warnings(d):
    if not d:
        return warnings.render(d)
    out = ["Warnings"]
    for w in d:
        news = "no fixture next gameweek" if w["blank"] and not w["news"] else w["news"]
        out.append(f"  {w['name']:<16} {chance_text(w['chance'])}  {news}")
    return out


OWN = {transfers: _transfers, warnings: _warnings}


def lines(data, feed):
    return [line for s in brief.SECTIONS
            for line in OWN.get(s, s.render)(data[brief._name(s)])]
