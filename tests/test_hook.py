"""Which tests the Stop hook runs (D325). Runs nothing."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "run_tests", Path(__file__).parents[1] / ".claude" / "hooks" / "run_tests.py")
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def test_web_change_runs_npm_only():
    assert hook.commands(["web/src/App.tsx"], False) == [hook.NPM]


def test_python_change_runs_pytest_only():
    assert hook.commands(["fpl/page/__init__.py"], False) == [hook.PYTEST]


def test_both():
    assert hook.commands(["fpl/brief.py", "web/src/brief.ts"], False) == [hook.PYTEST, hook.NPM]


def test_neither_runs_nothing():
    assert hook.commands(["README.md", "docs/roadmap.md"], False) == []


def test_always_and_no_git_run_both():
    assert hook.commands([], True) == [hook.PYTEST, hook.NPM]
    assert hook.commands(None, False) == [hook.PYTEST, hook.NPM]


def test_warning_only_past_80_percent_of_the_limit():
    assert hook.warning(hook.WARN_SHARE * hook.LIMIT) is None
    assert f"{hook.LIMIT} s limit" in hook.warning(hook.WARN_SHARE * hook.LIMIT + 1)


def test_limit_matches_both_hook_timeouts():
    import json
    settings = json.loads((Path(__file__).parents[1] / ".claude" / "settings.json").read_text())
    timeouts = [h["timeout"] for event in ("Stop", "SubagentStop")
                for group in settings["hooks"][event] for h in group["hooks"]]
    assert timeouts == [hook.LIMIT, hook.LIMIT]
