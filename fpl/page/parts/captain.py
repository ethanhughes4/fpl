from fpl.explain.parts.close import CAPTAIN_CLOSE, calls


def build(run):
    cap = run["data"]["captain"]
    c = next(c for c in calls(run["data"]) if c["kind"] == "captain")  # D290: numbers from close.calls()
    gap = f"Gap of {c['gap']:.1f} for next gameweek."
    sentence = (f"{gap} Anything at {CAPTAIN_CLOSE:.1f} or under counts as close." if c["close"]
                else f"{gap} Over {CAPTAIN_CLOSE:.1f}, so not close.")  # D334
    return {"captain": cap["captain"]["name"], "captain_score": f"{c['numbers'][0]:.1f}",
            "vice": cap["vice"]["name"], "vice_score": f"{c['numbers'][1]:.1f}",
            "close": c["close"], "sentence": sentence}
