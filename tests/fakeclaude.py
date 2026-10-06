"""Fake `subprocess.run` for fpl.claude. Tests must never run the real claude."""
import json
import subprocess
from pathlib import Path

from fpl import claude


def ok_json(text="All good.", tokens=(648, 20), model="claude-haiku-4-5-20251001", **extra):
    d = {"type": "result", "subtype": "success", "is_error": False, "result": text,
         "stop_reason": "end_turn", "terminal_reason": "completed", "num_turns": 1,
         "api_error_status": None, "total_cost_usd": 0.001,
         "usage": {"input_tokens": tokens[0], "output_tokens": tokens[1]},
         "modelUsage": {model: {"inputTokens": tokens[0]}}}
    d.update(extra)
    return json.dumps(d)


class FakeClaude:
    """stdout: what claude prints (default a good answer); timeout: raise TimeoutExpired;
    auth: exit code of `claude auth status`. `calls` records every run call."""

    def __init__(self, stdout=None, returncode=0, timeout=False, auth=0):
        self.stdout = ok_json() if stdout is None else stdout
        self.returncode, self.timeout, self.auth = returncode, timeout, auth
        self.calls = []
        self.auth_calls = 0

    def run(self, cmd, **kw):
        if cmd[1:3] == ["auth", "status"]:
            self.auth_calls += 1
            return subprocess.CompletedProcess(cmd, self.auth, "", "")
        cwd = Path(kw["cwd"])
        self.calls.append({"cmd": cmd, "kw": kw, "input": kw.get("input"), "cwd": cwd,
                           "files": sorted(p.name for p in cwd.iterdir()),
                           "system": (cwd / "system.txt").read_text(encoding="utf-8")})
        if self.timeout:
            raise subprocess.TimeoutExpired(cmd, kw["timeout"])
        return subprocess.CompletedProcess(cmd, self.returncode, self.stdout, "")

    def install(self, monkeypatch):
        monkeypatch.setattr(claude.shutil, "which", lambda name: "C:/fake/claude.exe")
        monkeypatch.setattr(claude.subprocess, "run", self.run)
        return self
