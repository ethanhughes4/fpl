def build(run):
    h = run["data"]["header"]
    return {"utc": h["deadline"],  # as the feed gives it; the page compares it with the clock (D300)
            "passed": f"Gameweek {h['gameweek']}'s deadline has passed. Run python -m fpl."}
