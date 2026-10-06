"""The one file that runs Claude Code (D165). Everything else takes `ask` as an argument."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

AUTH_TIMEOUT = 10
# D194: thinking off for these models (MAX_THINKING_TOKENS=0, env-vars docs); a real writer
# call spent 62 s mostly thinking. Opus 5.5, Sonnet 5.5 and Fable can't turn it off.
THINKING_OFF = {"haiku"}
MAX_REASON = 200  # D189: characters of the failure reason shown
NOT_INSTALLED = "Claude Code is not installed or not logged in"


class AskError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


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


def ask(prompt, system, model, timeout):
    """Returns (text, tokens, model_id). tokens is None when usage is missing."""
    exe = shutil.which("claude")
    if exe is None:
        raise AskError(NOT_INSTALLED)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        sysfile = Path(tmp) / "system.txt"
        sysfile.write_text(system, encoding="utf-8")
        cmd = [exe, "-p", "--safe-mode", "--model", model, "--system-prompt-file", str(sysfile),
               "--tools", "", "--strict-mcp-config", "--no-session-persistence",
               "--max-turns", "1", "--output-format", "json", "--permission-prompts", "none"]
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
    if r.returncode != 0 or out.get("is_error") or out.get("subtype") != "success":
        if _not_logged_in(exe):
            raise AskError(NOT_INSTALLED)
        raise AskError(f"the model call failed ({_reason(out, r)})")
    usage = out.get("usage") or {}
    parts = (usage.get("input_tokens"), usage.get("output_tokens"))
    tokens = None if None in parts else sum(parts)
    model_id = next(iter(out.get("modelUsage") or {}), None)
    return out.get("result") or "", tokens, model_id
