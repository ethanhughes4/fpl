"""The explanation part of the data file (D291)."""
import json
from pathlib import Path

from fpl.page.parts import explanation
from fpl import brief, feed as feedmod, page
from fpl.__main__ import main
from tests.fakeclaude import FakeClaude, ok_json

SNAP = str(Path(__file__).parent / "data" / "snapshot")
NONE = {"text": None, "message": "No explanation for this run."}


def written(page_file):
    return json.loads(page_file.read_text(encoding="utf-8"))["explanation"]


def test_none_when_not_run():
    feed = feedmod.load(SNAP)
    assert explanation.build({"data": brief.build(feed), "feed": feed, "explanation": None}) == NONE


def test_text_and_skipped_lines():
    feed = feedmod.load(SNAP)
    data = brief.build(feed)
    got = explanation.build({"data": data, "feed": feed, "explanation": ["Explanation", "Groß is captain."]})
    assert got == {"text": "Groß is captain.", "message": None}
    got = explanation.build({"data": data, "feed": feed, "explanation": ["Explanation skipped: timed out."]})
    assert got == {"text": None, "message": "Explanation skipped: timed out."}


def test_main_from_and_no_explain(page_file):
    assert main(["--from", SNAP]) == 0
    assert written(page_file) == NONE
    assert main(["--from", SNAP, "--no-explain"]) == 0
    assert written(page_file) == NONE


def test_main_explained_with_fakeclaude(monkeypatch, page_file):
    FakeClaude(stdout=ok_json("Pick the captain for gameweek 6.")).install(monkeypatch)
    assert main(["--from", SNAP, "--explain"]) == 0
    assert written(page_file) == {"text": "Pick the captain for gameweek 6.", "message": None}


def test_main_skipped(monkeypatch, page_file):
    FakeClaude(timeout=True).install(monkeypatch)
    assert main(["--from", SNAP, "--explain"]) == 0
    assert written(page_file) == {
        "text": None,
        "message": "Explanation skipped: the model call failed (timed out after 120 s)."}
