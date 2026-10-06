from fpl.explain.checks import numbers

CHECKS = [numbers]


def run(text, ctx, live_only=False):
    """First failure reason, or None."""
    for c in CHECKS:
        if c.LIVE or not live_only:
            reason = c.check(text, ctx)
            if reason:
                return reason
    return None
