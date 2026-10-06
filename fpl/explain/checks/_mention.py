from fpl.explain.checks.names import _plain, _word


def missing(text, players):
    """First player name not in the text (accents and case ignored, whole word), or None."""
    plain = _plain(text)
    return next((p for p in players if not _word(_plain(p)).search(plain)), None)
