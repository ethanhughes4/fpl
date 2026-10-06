import argparse
import json
import sys

from fpl import brief, claude, explain, feed as feedmod
from fpl.manual import ManualError
from fpl.download import OWNER_TEAM, FeedError,NoUpcomingGameweek, TeamNotFound, download

DEFAULT_TEAM = OWNER_TEAM


def main(argv=None):
    ap = argparse.ArgumentParser(prog="fpl")
    ap.add_argument("--team", type=int, default=DEFAULT_TEAM)
    ap.add_argument("--from", dest="folder")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--explain", dest="explain", action="store_true", default=None)
    ap.add_argument("--no-explain", dest="explain", action="store_false")
    a = ap.parse_args(argv)
    try:
        feed = feedmod.load(a.folder or download(a.team))
    except FeedError as e:
        print(f"Could not reach FPL (HTTP {e.code}). Try again later or use --from <folder>")
        return 1
    except TeamNotFound:
        print(f"Team {a.team} not found.")
        return 1
    except feedmod.MissingFile as e:
        print(f"Missing file: {e}")
        return 1
    except NoUpcomingGameweek:
        print("No upcoming gameweek.")
        return 0
    if feedmod.upcoming(feed) is None:
        print("No upcoming gameweek.")
        return 0
    try:
        data = brief.build(feed)
    except ManualError as e:
        print(e)
        return 1
    print(json.dumps(data, indent=2) if a.json else brief.render(data))
    if not a.json and (a.explain if a.explain is not None else not a.folder):
        print("\n".join(explain.explain(data, feed, claude.ask)))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
