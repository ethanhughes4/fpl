"""python -m tests.make_sample: writes tests/data/brief-sample.json, the page tests' data (D309, D329).

Made from the snapshot as a --from run makes it (no explanation), with the download time fixed
to D119's constant so file copies do not change it (D339).
"""
from pathlib import Path

from fpl import brief, feed as feedmod, page
from tests.test_rebuild import SNAPSHOT_TIME

DATA = Path(__file__).parent / "data"
SAMPLE = DATA / "brief-sample.json"


def build():
    feed = feedmod.load(DATA / "snapshot")
    return page.build(brief.build(feed), feed, SNAPSHOT_TIME, None)


def main():
    feed = feedmod.load(DATA / "snapshot")
    page.write(brief.build(feed), feed, SNAPSHOT_TIME, None, SAMPLE)


if __name__ == "__main__":
    main()
