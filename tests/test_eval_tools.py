import json
from pathlib import Path

import pytest

from fpl import claude, feed as feedmod
from fpl.eval.tools import __main__ as cli, path, report, run
from fpl.eval.tools.questions import QUESTIONS
from tests.fakeclaude import FakeClaude, ok_json, stream_json

DATA = Path(__file__).parent / "data"
SNAP = DATA / "snapshot"
POOL = feedmod.load(SNAP)["bootstrap"]["elements"]
OUT = "Data downloaded Wed 7 Oct 00:09, gameweek 6\n\nCaptain: Groß (7.9)"
Q = {i: q for i, q in enumerate(QUESTIONS, 1)}
RIGHT = {1: [("get_brief", {})], 2: [("get_players", {"names": ["411"]})],
         3: [("get_players", {"names": [124, 229, 411]})],
         4: [("get_players", {"names": ["Groß", "Palmer"]})],
         5: [("find_replacements", {"name": "368"})], 6: [("find_replacements", {"name": "304"})],
         7: [("get_eval_results", {"kind": "writing"})],
         8: [("refresh", {}), ("get_brief", {})], 9: [], 10: []}


def stream(calls, text=None):
    text = text or ("It is 7.9." if calls else "No.")
    return stream_json([(t, a, OUT) for t, a in calls], text)


def reply_with(wrong=(), text=None):
    """A fake claude: the right calls for every question, except the question numbers in wrong."""
    def reply(prompt):
        i = next(i for i, q in Q.items() if q.text == prompt)
        calls = [("get_players", {"names": ["Nobody"]})] if i in wrong else RIGHT[i]
        return stream(calls, text)
    return reply


def made(i, calls):
    return path.check(Q[i], calls, POOL)


# --- claude.ask_tools

def test_ask_tools_command_and_parsing(monkeypatch):
    fake = FakeClaude(stdout=stream_json([("get_brief", {}, OUT)], "7.9", tokens=(4, 20),
                                         usage={"input_tokens": 4, "output_tokens": 20,
                                                "cache_creation_input_tokens": 100,
                                                "cache_read_input_tokens": 10})).install(monkeypatch)
    events, text, tokens, model = claude.ask_tools("hi", run.mcp_config(), "opus", 180, 6)
    c = fake.calls[0]
    cmd = c["cmd"]
    assert cmd[cmd.index("--setting-sources") + 1] == "" and cmd[cmd.index("--tools") + 1] == ""
    assert cmd[cmd.index("--allowedTools") + 1] == "mcp__fpl" and "--strict-mcp-config" in cmd
    assert cmd[cmd.index("--max-turns") + 1] == "6" and "--safe-mode" not in cmd
    assert cmd[cmd.index("--output-format") + 1] == "stream-json" and "--system-prompt-file" not in cmd
    assert c["files"] == [] and c["system"] is None and c["input"] == "hi"  # empty folder
    cfg = json.loads(c["mcp"])["mcpServers"]["fpl"]
    assert cfg["args"] == ["-m", "fpl.mcp", "--from", str(SNAP)] and "PYTHONPATH" in cfg["env"]
    assert (text, tokens, model) == ("7.9", 4 + 20 + 110, "claude-opus-5-5")
    assert path.calls(events) == [("get_brief", {})] and path.outputs(events) == [OUT]


def test_ask_tools_turn_limit_and_timeout_are_errors(monkeypatch):
    FakeClaude(stdout=stream_json(text="", is_error=True, subtype="error_max_turns"),
               returncode=1).install(monkeypatch)
    with pytest.raises(claude.AskError):
        claude.ask_tools("hi", {}, "opus", 180, 6)
    FakeClaude(timeout=True).install(monkeypatch)
    with pytest.raises(claude.AskError, match="timed out"):
        claude.ask_tools("hi", {}, "opus", 180, 6)


def test_ask_tools_unreadable_and_not_installed(monkeypatch):
    FakeClaude(stdout="garbage").install(monkeypatch)
    with pytest.raises(claude.AskError, match="unreadable"):
        claude.ask_tools("hi", {}, "opus", 180, 6)
    monkeypatch.setattr(claude.shutil, "which", lambda name: None)
    with pytest.raises(claude.AskError, match="not installed"):
        claude.ask_tools("hi", {}, "opus", 180, 6)


def test_ask_still_works_after_refactor(monkeypatch):
    FakeClaude(stdout=ok_json("fine")).install(monkeypatch)
    assert claude.ask("p", "s", "haiku", 5)[0] == "fine"


# --- the frozen stream files

def test_stream_files():
    events = [json.loads(x) for x in (DATA / "tools_stream_brief.jsonl").read_text("utf-8").splitlines()]
    assert path.calls(events) == [("get_brief", {})]
    assert path.outputs(events)[0].startswith("Data downloaded") and "Captain: Groß (7.9)" in path.outputs(events)[0]
    assert made(1, path.calls(events)) == (True, "")
    events = [json.loads(x) for x in (DATA / "tools_stream_refresh.jsonl").read_text("utf-8").splitlines()]
    assert made(1, path.calls(events))[0] is False  # refresh is not allowed for question 1


# --- path checker

def test_right_missing_extra_forbidden_split():
    assert made(3, [("get_players", {"names": [124, 229, 411]})]) == (True, "")
    ok, why = made(3, [("get_players", {"names": [124, 229]})])
    assert not ok and "411" in why
    assert made(3, [("get_brief", {}), ("get_players", {"names": [124, 229, 411, 154]})])[0]  # extras
    assert made(3, [("get_players", {"names": ["124"]}), ("get_players", {"names": ["Tarkowski"]}),
                    ("get_players", {"names": ["Haaland"]})])[0]  # split across calls
    ok, why = made(3, [("get_players", {"names": [124, 229, 411]}), ("refresh", {})])
    assert not ok and "refresh" in why
    assert made(1, [])[0] is False and "never called get_brief" in made(1, [])[1]
    assert made(8, [("get_brief", {}), ("refresh", {})])[0]  # any order
    assert made(8, [("refresh", {})])[0] is False
    assert made(7, [("get_eval_results", {"kind": "scoring"})])[0] is False
    assert made(5, [("find_replacements", {"name": "Szoboszlai"})])[0]  # a name resolves to the id
    assert made(6, [("find_replacements", {"name": "Haaland"})])[0] is False  # the wrong player


def test_palmer_by_name_or_either_id():
    for arg in ("Palmer", 154, "301"):
        assert made(4, [("get_players", {"names": [124, arg]})]) == (True, "")
    assert made(4, [("get_players", {"names": [124, 411]})])[0] is False
    assert made(4, [("get_players", {"names": ["Nobody", 124]})])[0] is False


def test_no_tool_questions():
    assert made(10, []) == (True, "")
    assert made(10, [("get_brief", {})])[0] is False  # a call where none is allowed
    assert made(9, []) == (True, "")
    assert made(9, [("find_replacements", {"name": "Szoboszlai"})])[0]  # D245
    assert made(9, [("get_players", {"names": ["Szoboszlai", "Schade"]})])[0]  # D261
    assert made(9, [("refresh", {})])[0] is False


def test_outputs_unwraps_and_keeps_plain_text():
    ev = [{"type": "user", "message": {"content": [
        {"type": "tool_result", "content": json.dumps({"result": "a\nb"})},
        {"type": "tool_result", "content": "plain"},
        {"type": "tool_result", "content": [{"type": "text", "text": "listed"}]}]}}]
    assert path.outputs(ev) == ["a\nb", "plain", "listed"]


# --- run and report

def go(monkeypatch, reply, **kw):
    fake = FakeClaude(reply=reply).install(monkeypatch)
    return run.run(**kw), fake


def test_all_right_passes_and_counts(monkeypatch):
    result, fake = go(monkeypatch, reply_with())
    assert result["calls"] == len(fake.calls) == 30 and len(result["rows"]) == 30
    assert [r["q"] for r in result["rows"]][:4] == [1, 1, 1, 2]
    assert all(r["path"] and r["numbers"] is not False and r["names"] for r in result["rows"])
    assert result["models"] == ["claude-opus-5-5"] and result["tokens"] == 30 * 24
    text = report.render(result, "abc1234")
    assert "Verdict: PASS" in text and "path right: 30 of 30" in text
    assert "get_players(124, 229, 411)" in text and "refresh(), get_brief()" in text
    assert fake.calls[0]["kw"]["timeout"] == run.TIMEOUT


def test_path_threshold_27_of_30(monkeypatch):
    result, _ = go(monkeypatch, reply_with(wrong={1}))  # 3 runs wrong
    assert result["summary"][0][1:] == ("27 of 30", True)
    text = report.render(result, "c")
    assert "Verdict: PASS" in text and "(path wrong: never called get_brief)" in text
    result, _ = go(monkeypatch, reply_with(wrong={1, 2}))
    assert result["summary"][0][1:] == ("24 of 30", False)
    assert "Verdict: FAIL" in report.render(result, "c")


def test_answer_checks_must_be_perfect(monkeypatch):
    def text_for(i):
        return {1: "It is 7.9, up 3.2.", 2: "Haaland and Saka.", 10: "It adds 7.9 points."}.get(i)

    def reply(prompt):
        i = next(i for i, q in Q.items() if q.text == prompt)
        return stream(RIGHT[i], text_for(i))

    result, _ = go(monkeypatch, reply)
    rows = {r["q"]: r for r in result["rows"] if r["run"] == 1}
    assert rows[1]["numbers"] is False and rows[1]["names"] is True  # 3.2 is in no tool output
    assert rows[2]["names"] is False
    assert rows[10]["numbers"] is None  # D265: no tool called, number check skipped
    assert rows[3]["numbers"] and rows[9]["numbers"] is None
    assert result["summary"][1][1:] == ("24 of 30", False)  # questions 1 and 2, three runs each
    assert "Verdict: FAIL" in report.render(result, "c")


def test_failing_numbers_and_names_are_listed_with_their_sentence(monkeypatch):
    """D262: every failure, in the table cell and under the answer."""
    def reply(prompt):
        i = next(i for i, q in Q.items() if q.text == prompt)
        text = {1: "Captain Groß on 7.9 this week. He leads by 4.3.\n2. Saka and Palmer trail by 16.6 and 4.3."}.get(i)
        return stream(RIGHT[i], text)

    result, _ = go(monkeypatch, reply, runs=1)
    row = result["rows"][0]
    assert row["bad_numbers"] == [("4.3", "He leads by 4.3."),   # "2." numbers the line (D263)
                                  ("16.6", "2. Saka and Palmer trail by 16.6 and 4.3.")]
    assert sorted(n for n, _ in row["bad_names"]) == ["Palmer", "Saka"]
    assert all(s == "2. Saka and Palmer trail by 16.6 and 4.3." for _, s in row["bad_names"])
    assert row["numbers"] is False and row["names"] is False
    text = report.render(result, "c")
    assert "FAIL (4.3, 16.6)" in text
    assert '(number not in any tool output: 4.3 in "He leads by 4.3.")' in text
    assert '(name not in the question or any tool output: Saka in "2. Saka and Palmer' in text


def test_no_tool_answer_skips_numbers_only(monkeypatch):
    """D265: a no-tool answer's digits are not checked (shown "-"); its names still are."""
    def reply(prompt):
        i = next(i for i, q in Q.items() if q.text == prompt)
        return stream(RIGHT[i], {10: "All 15 players score, not just 11.", 9: "Saka, 15 players."}.get(i))

    result, _ = go(monkeypatch, reply, runs=1)
    rows = {r["q"]: r for r in result["rows"]}
    assert rows[10]["numbers"] is None and rows[10]["bad_numbers"] == [] and rows[10]["names"]
    assert rows[9]["numbers"] is None and rows[9]["names"] is False
    assert result["summary"][1][1:] == ("9 of 10", False)
    line = next(x for x in report.render(result, "c").splitlines() if x.startswith("10 "))
    assert line.split()[-4:] == ["pass", "-", "pass", "24"]


def test_sentence_split():
    t = "It costs 6.9m. Gain 0.4.\n1. **Form.** Up 3.2!"
    assert run.sentence(t, "6.9", run._has_number) == "It costs 6.9m."
    assert run.sentence(t, "1", run._has_number) == "1. **Form.**"
    assert run.sentence(t, "3.2", run._has_number) == "Up 3.2!"
    assert run.sentence(t, "9", run._has_number) == ""


def test_names_from_the_question_pass_numbers_do_not(monkeypatch):
    """D260: Q9's refusal may name the players the owner named; a name in neither fails."""
    def reply(prompt):
        i = next(i for i, q in Q.items() if q.text == prompt)
        text = {9: "I can't make transfers; do Szoboszlai to Schade in the FPL app.",
                10: "Saka is not in the question."}.get(i)
        return stream(RIGHT[i], text)

    result, _ = go(monkeypatch, reply)
    rows = {r["q"]: r for r in result["rows"] if r["run"] == 1}
    assert rows[9]["names"] and rows[9]["numbers"] is None  # D265
    assert rows[10]["names"] is False


def test_failed_call_is_a_wrong_path(monkeypatch):
    FakeClaude(timeout=True).install(monkeypatch)
    result = run.run(runs=1)
    assert result["summary"][0][1:] == ("0 of 10", False)
    text = report.render(result, "c")
    assert "(path wrong: no answer: the model call failed (timed out after 180 s))" in text
    assert "(call failed:" in text


def test_cap_stops_before_calling(monkeypatch):
    result, fake = go(monkeypatch, reply_with(), runs=5)  # 50 rows, cap 40
    assert result["calls"] == len(fake.calls) == run.MAX_CALLS == len(result["rows"])
    text = report.render(result, "c")
    assert "stopped at the 40-call cap" in text and "Verdict: FAIL" in text


def test_quick_threshold_9_of_10(monkeypatch):
    result, _ = go(monkeypatch, reply_with(wrong={3}), runs=1)
    assert result["summary"][0][1:] == ("9 of 10", True)
    result, _ = go(monkeypatch, reply_with(wrong={3, 4}), runs=1)
    assert result["summary"][0][1:] == ("8 of 10", False)


def test_main_file_names(monkeypatch, tmp_path, capsys):
    FakeClaude(reply=reply_with()).install(monkeypatch)
    monkeypatch.setattr(cli.base, "commit", lambda: "abc1234")
    assert cli.main(["--quick"], results=tmp_path) == 0
    assert [p.name[11:] for p in tmp_path.iterdir()] == ["abc1234-tools-quick.txt"]
    assert "Saved to" in capsys.readouterr().out
    assert cli.main([], results=tmp_path) == 0
    assert sorted(p.name[11:] for p in tmp_path.iterdir()) == ["abc1234-tools-quick.txt", "abc1234-tools.txt"]
    assert "Verdict: PASS" in (tmp_path / [p.name for p in tmp_path.iterdir() if p.name.endswith("-tools.txt")][0]).read_text("utf-8")
