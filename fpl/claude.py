"""The one file that runs Claude Code (D165). Everything else takes `ask` as an argument."""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

AUTH_TIMEOUT = 10
# D194: thinking off for these models (MAX_THINKING_TOKENS=0, env-vars docs); a real writer
# call spent 62 s mostly thinking. Opus 5.5, Sonnet 5.5 and Fable can't turn it off.
THINKING_OFF = {"haiku"}
CACHE_FIELDS = ("cache_creation_input_tokens", "cache_read_input_tokens")  # D197
MAX_REASON = 200  # D189: characters of the failure reason shown
NOT_INSTALLED = "Claude Code is not installed or not logged in"
# D200: a failure counts as a plan limit on HTTP 429 or these words in the reason.
# ponytail: word match on Claude Code's message; exact wording not documented, widen if missed
PLAN_LIMIT_STATUS = 429
PLAN_LIMIT_WORDS = re.compile(r"usage limit|rate limit|plan limit|limit reached|too many requests",
                              re.IGNORECASE)


class AskError(Exception):
    def __init__(self, reason, plan_limit=False):
        super().__init__(reason)
        self.reason, self.plan_limit = reason, plan_limit


def _first_line(text):
    lines = str(text or "").strip().splitlines()
    return lines[0].strip() if lines else ""


def _reason(out, r):
    """D189: first text found in result, errors[0], stderr, then stdout when it was not JSON;
    one line, cut to MAX_REASON."""
    errors = out.get("errors") or [""]
    for text in (out.get("result"), errors[0], r.stderr, out.get("_stdout")):
        line = _first_line(text)
        if line:
            return line[:MAX_REASON]
    return "unreadable output"


def _not_logged_in(exe):
    try:
        r = subprocess.run([exe, "auth", "status"], capture_output=True, text=True,
                           encoding="utf-8", timeout=AUTH_TIMEOUT)
    except (subprocess.TimeoutExpired, OSError):
        return False
    return r.returncode == 1


def ask(prompt, system, model, timeout, schema=None):
    """Returns (text, tokens, model_id). tokens is None when usage is missing.
    With a JSON schema (D198) the text is the structured answer as JSON."""
    exe = shutil.which("claude")
    if exe is None:
        raise AskError(NOT_INSTALLED)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        sysfile = Path(tmp) / "system.txt"
        sysfile.write_text(system, encoding="utf-8")
        cmd = [exe, "-p", "--safe-mode", "--model", model, "--system-prompt-file", str(sysfile),
               "--tools", "", "--strict-mcp-config", "--no-session-persistence",
               "--max-turns", "1", "--output-format", "json", "--permission-prompts", "none"]
        if schema is not None:
            cmd += ["--json-schema", json.dumps(schema)]
        try:
            env = {**os.environ, "MAX_THINKING_TOKENS": "0"} if model in THINKING_OFF else None
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                               encoding="utf-8", cwd=tmp, timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            raise AskError(f"the model call failed (timed out after {timeout} s)")
        except OSError as e:
            raise AskError(f"the model call failed ({e})")
    try:
        out = json.loads(r.stdout)
        if not isinstance(out, dict):
            raise ValueError
    except ValueError:
        if r.returncode == 0:
            raise AskError("the model call failed (unreadable output)")
        out = {"_stdout": r.stdout}
    _raise_if_failed(out, r, exe)
    tokens, model_id = _usage(out)
    if schema is not None and isinstance(out.get("structured_output"), dict):
        return json.dumps(out["structured_output"], ensure_ascii=False), tokens, model_id
    return out.get("result") or "", tokens, model_id


def _raise_if_failed(out, r, exe):
    if r.returncode != 0 or out.get("is_error") or out.get("subtype") != "success":
        if _not_logged_in(exe):
            raise AskError(NOT_INSTALLED)
        why = _reason(out, r)
        limit = out.get("api_error_status") == PLAN_LIMIT_STATUS or bool(PLAN_LIMIT_WORDS.search(why))
        raise AskError(f"the model call failed ({why})", plan_limit=limit)


def _usage(out):
    usage = out.get("usage") or {}
    parts = (usage.get("input_tokens"), usage.get("output_tokens"))
    # D197: cached input is reported apart from input_tokens; missing cache fields count 0
    cached = sum(usage.get(k) or 0 for k in CACHE_FIELDS)
    tokens = None if None in parts else sum(parts) + cached
    return tokens, next(iter(out.get("modelUsage") or {}), None)


def ask_tools(prompt, mcp_config, model, timeout, max_turns):
    """The tools eval's call (D233, D243, D244). mcp_config: the MCP config as a dict. Claude runs
    in an empty folder with no tools but the server's, no system prompt of ours, and none of the
    owner's settings (see fpl/eval/tools/run.py for what was checked).
    Returns (events, text, tokens, model_id); events = the stream-json lines, as dicts."""
    exe = shutil.which("claude")
    if exe is None:
        raise AskError(NOT_INSTALLED)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        cfg, work = Path(tmp) / "mcp.json", Path(tmp) / "work"
        cfg.write_text(json.dumps(mcp_config), encoding="utf-8")
        work.mkdir()
        cmd = [exe, "-p", "--setting-sources", "", "--model", model, "--mcp-config", str(cfg),
               "--strict-mcp-config", "--tools", "", "--allowedTools", "mcp__fpl",
               "--no-session-persistence", "--max-turns", str(max_turns),
               "--output-format", "stream-json", "--verbose", "--permission-prompts", "none"]
        try:
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                               encoding="utf-8", cwd=work, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise AskError(f"the model call failed (timed out after {timeout} s)")
        except OSError as e:
            raise AskError(f"the model call failed ({e})")
    events = []
    for line in r.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    out = next((e for e in reversed(events) if isinstance(e, dict) and e.get("type") == "result"), None)
    if out is None:
        if r.returncode == 0:
            raise AskError("the model call failed (unreadable output)")
        out = {"_stdout": r.stdout}
    _raise_if_failed(out, r, exe)
    tokens, model_id = _usage(out)
    return events, out.get("result") or "", tokens, model_id
