"""python -m tests.make_sample: writes tests/data/brief-sample.json, the page tests' data (D309, D329).

Made from the snapshot as a --from run makes it (no explanation), with the download time fixed
to D119's constant so file copies do not change it (D339), and the eval lines read from a fixed
folder (tests/data/sample_results) so a new results file does not make the sample stale.
"""
from contextlib import contextmanager
from pathlib import Path

from fpl import brief, feed as feedmod, page
from fpl.mcp.tools import get_eval_results
from tests.test_rebuild import SNAPSHOT_TIME

DATA = Path(__file__).parent / "data"
SAMPLE = DATA / "brief-sample.json"
RESULTS = DATA / "sample_results"  # one line from each newest results file at stage 5


@contextmanager
def fixed_results():
    old = get_eval_results.RESULTS
    get_eval_results.RESULTS = RESULTS
    try:
        yield
    finally:
        get_eval_results.RESULTS = old


def build():
    feed = feedmod.load(DATA / "snapshot")
    with fixed_results():
        return page.build(brief.build(feed), feed, SNAPSHOT_TIME, None)


def main():
    feed = feedmod.load(DATA / "snapshot")
    with fixed_results():
        page.write(brief.build(feed), feed, SNAPSHOT_TIME, None, SAMPLE)


if __name__ == "__main__":
    main()
