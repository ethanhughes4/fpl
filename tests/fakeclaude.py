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


def stream_json(calls=(), text="All good.", tokens=(4, 20), model="claude-opus-5-5", **extra):
    """What `claude -p --output-format stream-json --verbose` prints (shapes seen on the real call,
    fpl/eval/tools/run.py): calls = [(tool, args, tool output)], then the answer and the result line.
    Tool outputs are wrapped as {"result": text}, as the SDK sends a str reply."""
    ev = [{"type": "system", "subtype": "init", "tools": [f"mcp__fpl__{c[0]}" for c in calls]}]
    for i, (tool, args, out) in enumerate(calls):
        ev.append({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": f"t{i}", "name": f"mcp__fpl__{tool}", "input": args}]}})
        ev.append({"type": "user", "message": {"role": "user", "content": [
            {"tool_use_id": f"t{i}", "type": "tool_result", "content": json.dumps({"result": out})}]}})
    ev.append({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}})
    ev.append(json.loads(ok_json(text, tokens, model, num_turns=len(calls) + 1, **extra)))
    return "\n".join(json.dumps(e, ensure_ascii=False) for e in ev) + "\n"


class FakeClaude:
    """stdout: what claude prints (default a good answer); timeout: raise TimeoutExpired;
    auth: exit code of `claude auth status`; stderr: what claude prints there. `calls` records every run call.
    reply: optional function of the prompt that gives the stdout, for runs with several questions.
    system.txt is optional (the tools eval has none); `mcp` is the config file's text when there is one."""

    def __init__(self, stdout=None, returncode=0, timeout=False, auth=0, stderr="", reply=None):
        self.stdout = ok_json() if stdout is None else stdout
        self.returncode, self.timeout, self.auth, self.stderr = returncode, timeout, auth, stderr
        self.reply = reply
        self.calls = []
        self.auth_calls = 0

    def run(self, cmd, **kw):
        if cmd[1:3] == ["auth", "status"]:
            self.auth_calls += 1
            return subprocess.CompletedProcess(cmd, self.auth, "", "")
        if cmd[0] == "git":  # the page footer's eval lookup asks git for the log: empty answer
            return subprocess.CompletedProcess(cmd, 0, "", "")
        cwd = Path(kw["cwd"])
        system = cwd / "system.txt"
        cfg = Path(cmd[cmd.index("--mcp-config") + 1]) if "--mcp-config" in cmd else None
        self.calls.append({"cmd": cmd, "kw": kw, "input": kw.get("input"), "cwd": cwd,
                           "files": sorted(p.name for p in cwd.iterdir()),
                           "system": system.read_text(encoding="utf-8") if system.exists() else None,
                           "mcp": cfg.read_text(encoding="utf-8") if cfg else None})
        if self.timeout:
            raise subprocess.TimeoutExpired(cmd, kw["timeout"])
        stdout = self.reply(kw.get("input")) if self.reply else self.stdout
        return subprocess.CompletedProcess(cmd, self.returncode, stdout, self.stderr)

    def install(self, monkeypatch):
        monkeypatch.setattr(claude.shutil, "which", lambda name: "C:/fake/claude.exe")
        monkeypatch.setattr(claude.subprocess, "run", self.run)
        return self
