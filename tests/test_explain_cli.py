import json
from pathlib import Path

import pytest

from fpl import brief, feed as feedmod
from fpl.__main__ import main
from tests.fakeclaude import FakeClaude, ok_json

DATA = Path(__file__).parent / "data"
SNAP = str(DATA / "snapshot")
TEXT = "Pick the captain for gameweek 6."


def run(monkeypatch, capsys, args, **kw):
    fake = FakeClaude(**kw).install(monkeypatch)
    assert main(args) == 0
    return fake, capsys.readouterr().out


def plain(capsys, args):
    assert main(args) == 0
    return capsys.readouterr().out


@pytest.fixture
def brief_text():
    return brief.render(brief.build(feedmod.load(SNAP)))


def test_success(monkeypatch, capsys, brief_text):
    fake, out = run(monkeypatch, capsys, ["--from", SNAP, "--explain"], stdout=ok_json(TEXT))
    assert out.startswith(brief_text + "\nExplanation\n" + TEXT)
    assert len(fake.calls) == 1
    assert fake.calls[0]["input"] .startswith(brief_text)
    assert "150" in fake.calls[0]["system"] and "{max_words}" not in fake.calls[0]["system"]
    assert "--model" in fake.calls[0]["cmd"] and "haiku" in fake.calls[0]["cmd"]


def test_missing(monkeypatch, capsys):
    out = plain(capsys, ["--from", SNAP, "--explain"])  # guard: no claude on the path
    assert out.endswith("Explanation skipped: Claude Code is not installed or not logged in.\n")


def test_call_failed(monkeypatch, capsys):
    _, out = run(monkeypatch, capsys, ["--from", SNAP, "--explain"],
                 returncode=1, stdout=ok_json("Overloaded", is_error=True))
    assert out.endswith("Explanation skipped: the model call failed (Overloaded).\n")
    assert "Explanation\n" not in out


def test_timeout(monkeypatch, capsys):
    _, out = run(monkeypatch, capsys, ["--from", SNAP, "--explain"], timeout=True)
    assert out.endswith("Explanation skipped: the model call failed (timed out after 60 s).\n")


def test_checker_failure(monkeypatch, capsys):
    _, out = run(monkeypatch, capsys, ["--from", SNAP, "--explain"],
                 stdout=ok_json("Captain scores 7.4."))
    assert out.endswith("Explanation skipped: it quoted 7.4, which is not in the brief.\n")
    assert "Captain scores" not in out


def test_from_makes_no_call(monkeypatch, capsys, brief_text):
    fake, out = run(monkeypatch, capsys, ["--from", SNAP])
    assert fake.calls == [] and out == brief_text + "\n"


def test_no_explain_makes_no_call(monkeypatch, capsys, brief_text):
    fake = FakeClaude().install(monkeypatch)
    import fpl.__main__ as m
    monkeypatch.setattr(m, "download", lambda team: SNAP)
    assert main(["--no-explain"]) == 0
    assert fake.calls == []
    assert capsys.readouterr().out == brief_text + "\n"


def test_default_without_from_explains(monkeypatch, capsys):
    import fpl.__main__ as m
    fake = FakeClaude(stdout=ok_json(TEXT)).install(monkeypatch)
    monkeypatch.setattr(m, "download", lambda team: SNAP)
    assert main([]) == 0
    assert len(fake.calls) == 1
    assert capsys.readouterr().out.endswith("Explanation\n" + TEXT + "\n")


def test_last_flag_wins(monkeypatch, capsys):
    fake, out = run(monkeypatch, capsys, ["--from", SNAP, "--explain", "--no-explain"])
    assert fake.calls == []
    fake, out = run(monkeypatch, capsys, ["--from", SNAP, "--no-explain", "--explain"],
                    stdout=ok_json(TEXT))
    assert len(fake.calls) == 1 and "Explanation" in out


def test_json_unchanged_and_no_call(monkeypatch, capsys):
    expected = json.dumps(brief.build(feedmod.load(SNAP)), indent=2) + "\n"
    for flags in ([], ["--explain"]):
        fake, out = run(monkeypatch, capsys, ["--from", SNAP, "--json"] + flags)
        assert fake.calls == [] and out == expected
