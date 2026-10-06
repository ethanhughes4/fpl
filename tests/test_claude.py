import json

import pytest

from fpl import claude
from tests.fakeclaude import FakeClaude, ok_json

ARGS = ["-p", "--safe-mode", "--model", "haiku", "--system-prompt-file", None, "--tools", "",
        "--strict-mcp-config", "--no-session-persistence", "--max-turns", "1",
        "--output-format", "json", "--permission-prompts", "none"]


def go(monkeypatch, **kw):
    fake = FakeClaude(**kw).install(monkeypatch)
    return fake, lambda p="hi", s="sys": claude.ask(p, s, "haiku", 60)


def reason(fn):
    with pytest.raises(claude.AskError) as e:
        fn()
    return e.value.reason


def test_command_and_folder(monkeypatch):
    fake, ask = go(monkeypatch)
    ask("the prompt", "the system")
    c = fake.calls[0]
    cmd = c["cmd"]
    assert cmd[0] == "C:/fake/claude.exe"
    sysfile = cmd[cmd.index("--system-prompt-file") + 1]
    assert cmd[1:] == [sysfile if a is None else a for a in ARGS]
    assert not c["kw"].get("shell")
    assert c["input"] == "the prompt"
    assert c["system"] == "the system"
    assert c["files"] == ["system.txt"]
    assert c["kw"]["timeout"] == 60 and c["kw"]["encoding"] == "utf-8"
    assert not c["cwd"].exists()  # temp folder removed afterwards


def test_accents_both_ways(monkeypatch):
    fake, ask = go(monkeypatch, stdout=ok_json("João Pedro scored"))
    assert ask("Gabriel Magalhães", "Müller")[0] == "João Pedro scored"
    assert fake.calls[0]["input"] == "Gabriel Magalhães"
    assert fake.calls[0]["system"] == "Müller"


def test_tokens_and_model(monkeypatch):
    _, ask = go(monkeypatch)
    assert ask() == ("All good.", 668, "claude-haiku-4-5-20251001")


def test_tokens_none_without_usage(monkeypatch):
    d = json.loads(ok_json())
    del d["usage"]
    _, ask = go(monkeypatch, stdout=json.dumps(d))
    assert ask()[1] is None


def test_no_claude(monkeypatch):
    assert reason(lambda: claude.ask("p", "s", "haiku", 60)) == claude.NOT_INSTALLED


def test_nonzero_exit_not_logged_in(monkeypatch):
    fake, ask = go(monkeypatch, returncode=1, stdout=ok_json("Not logged in", is_error=True), auth=1)
    assert reason(ask) == claude.NOT_INSTALLED
    assert fake.auth_calls == 1


def test_nonzero_exit_logged_in(monkeypatch):
    _, ask = go(monkeypatch, returncode=1, stdout=ok_json("Rate limit hit\nmore", is_error=True), auth=0)
    assert reason(ask) == "the model call failed (Rate limit hit)"


def test_nonzero_exit_plain_text(monkeypatch):
    _, ask = go(monkeypatch, returncode=2, stdout="boom\n", auth=0)
    assert reason(ask) == "the model call failed (boom)"


def test_is_error(monkeypatch):
    _, ask = go(monkeypatch, stdout=ok_json("Overloaded", is_error=True))
    assert reason(ask) == "the model call failed (Overloaded)"


def test_tokens_none_with_partial_usage(monkeypatch):
    d = json.loads(ok_json())
    del d["usage"]["output_tokens"]
    _, ask = go(monkeypatch, stdout=json.dumps(d))
    assert ask()[1] is None


def test_missing_subtype_is_failure(monkeypatch):
    d = json.loads(ok_json("No subtype"))
    del d["subtype"]
    _, ask = go(monkeypatch, stdout=json.dumps(d))
    assert reason(ask) == "the model call failed (No subtype)"


def test_subtype_not_success(monkeypatch):
    _, ask = go(monkeypatch, stdout=ok_json("Too many turns", subtype="error_max_turns"))
    assert reason(ask) == "the model call failed (Too many turns)"


def test_timeout(monkeypatch):
    _, ask = go(monkeypatch, timeout=True)
    assert reason(ask) == "the model call failed (timed out after 60 s)"


def test_unreadable_json(monkeypatch):
    _, ask = go(monkeypatch, stdout="not json")
    assert reason(ask) == "the model call failed (unreadable output)"
