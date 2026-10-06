"""The player pool for ranking and top 20 (D95)."""


def pool(feed, gw):
    """Elements with minutes > 0 in the rebuilt feed whose club has a fixture in gameweek gw."""
    clubs = {t for f in feed["fixtures"] if f["event"] == gw for t in (f["team_h"], f["team_a"])}
    return [el for el in feed["bootstrap"]["elements"] if el["minutes"] > 0 and el["team"] in clubs]
