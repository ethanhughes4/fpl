import argparse
import sys

from fpl.download import FeedError, TeamNotFound
from fpl.eval import download as dl, report, run
from fpl.feed import MissingFile

DEFAULT_TEAM = 8027067


def main(argv=None, results=report.RESULTS_DIR):
    ap = argparse.ArgumentParser(prog="fpl.eval")
    ap.add_argument("--team", type=int, default=DEFAULT_TEAM)
    ap.add_argument("--from", dest="folder")
    a = ap.parse_args(argv)
    try:
        folder = a.folder or dl.download(a.team)
        data = dl.load(folder)
    except FeedError as e:
        print(f"Could not reach FPL (HTTP {e.code}). Try again later or use --from <folder>")
        return 1
    except TeamNotFound:
        print(f"Team {a.team} not found.")
        return 1
    except MissingFile as e:
        print(f"Missing file: {e}")
        return 1
    result = run.run(data)
    if not result["rows"]:
        print("No finished gameweeks to replay.")
        return 0
    c = report.commit()
    text = report.render(result, a.team, folder, c)
    print(text)
    print(f"Saved to {report.save(text, c, results)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
