NONE_MESSAGE = "No explanation for this run."  # --no-explain, or --from without --explain (D291)


def build(run):
    """{"text", "message"}, one of them null. Lines are what explain.explain returned, or None."""
    lines = run["explanation"]
    if lines is None:
        return {"text": None, "message": NONE_MESSAGE}
    if lines[0] == "Explanation":  # ["Explanation", text]
        return {"text": lines[1], "message": None}
    return {"text": None, "message": lines[0]}  # "Explanation skipped: <reason>."
