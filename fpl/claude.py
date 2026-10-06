"""The one file that runs Claude Code (D165). Everything else takes `ask` as an argument."""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

AUTH_TIMEOUT = 10
NOT_INSTALLED = "Claude Code is not installed or not logged in"


class AskError(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _first_line(text):
    lines = (text or "").strip().splitlines()
    return lines[0] if lines else "no message"


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
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                               encoding="utf-8", cwd=tmp, timeout=timeout)
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
        out = {"result": r.stdout}
    if r.returncode != 0 or out.get("is_error") or out.get("subtype") != "success":
        if _not_logged_in(exe):
            raise AskError(NOT_INSTALLED)
        raise AskError(f"the model call failed ({_first_line(str(out.get('result') or ''))})")
    usage = out.get("usage") or {}
    parts = (usage.get("input_tokens"), usage.get("output_tokens"))
    tokens = None if None in parts else sum(parts)
    model_id = next(iter(out.get("modelUsage") or {}), None)
    return out.get("result") or "", tokens, model_id
