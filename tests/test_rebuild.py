"""D90 rebuild and leak checks on a real download (tests/data/eval_real)."""
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from fpl.eval import download, replay
from fpl.eval.formulas import current

REAL = Path(__file__).parent / "data" / "eval_real"
SNAPSHOT_TIME = datetime(2026, 10, 6, 12, 55, tzinfo=timezone.utc)  # D119: when gw06 file was downloaded
PASS_SHARE = 0.95  # D90
TOLERANCE = 0.1  # D90
BUMP = 7  # added to every number in the "future" live files


@pytest.fixture(scope="module")
def real():
    return download.load(REAL)


def test_rebuild_matches_gw06_snapshot(real):
    snap = json.loads((REAL / "gw06-bootstrap-static.json").read_text(encoding="utf-8"))
    feed = replay.as_of(real["bootstrap"], real["fixtures"], real["lives"], 6, now=SNAPSHOT_TIME)
    rebuilt = {e["id"]: e for e in feed["bootstrap"]["elements"]}
    assert len(rebuilt) == len(snap["elements"])
    for s in snap["elements"]:
        r = rebuilt[s["id"]]
        assert (r["minutes"], r["total_points"]) == (s["minutes"], s["total_points"]), s["web_name"]
    for field in ("form", "points_per_game"):
        close = sum(abs(rebuilt[s["id"]][field] - float(s[field])) <= TOLERANCE + 1e-9
                    for s in snap["elements"])
        assert close / len(snap["elements"]) >= PASS_SHARE, (field, close, len(snap["elements"]))


def bump(x):
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        return x + BUMP
    if isinstance(x, list):
        return [bump(v) for v in x]
    if isinstance(x, dict):
        return {k: bump(v) for k, v in x.items()}
    return x


def test_future_live_files_do_not_change_scores(real):
    for g in real["lives"]:
        if g < replay.FIRST_REPLAYED:
            continue
        before = replay.as_of(real["bootstrap"], real["fixtures"], real["lives"], g)
        lives = {k: (bump(v) if k >= g else copy.deepcopy(v)) for k, v in real["lives"].items()}
        after = replay.as_of(real["bootstrap"], real["fixtures"], lives, g)
        assert current.scores(after) == current.scores(before), g
