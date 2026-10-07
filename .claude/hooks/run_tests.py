"""Hook: the tests must pass before Claude (or a builder) can finish.

Main session (Stop): runs pytest if a .py file has uncommitted changes, and
`npm test` in web/ if a file under web/ has (D325).
Builders (SubagentStop, called with --always): always runs both, because a
builder commits its work, so git shows nothing as changed.
If git cannot answer, both run. Exit code 2 blocks.

Timed on Windows (D326), 2026-10-07: TIMES
"""
import json
import os
import subprocess
import sys
from pathlib import Path

PYTEST = "pytest"
NPM = "npm"
PASSING = {PYTEST: (0, 5), NPM: (0,)}  # pytest 5: no tests found
TAIL = 30  # lines of a failing run shown


def commands(changed, always):
    """changed: paths from git status, or None when git could not answer."""
    if always or changed is None:
        return [PYTEST, NPM]
    out = []
    if any(p.endswith(".py") for p in changed):
        out.append(PYTEST)
    if any(p.replace("\\", "/").startswith("web/") for p in changed):
        out.append(NPM)
    return out


def changed_paths(folder):
    git = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                         capture_output=True, text=True, cwd=folder)
    if git.returncode != 0:
        return None
    # "XY path" or "XY old -> new"; quoted paths lose their quotes
    return [line[3:].split(" -> ")[-1].strip('"') for line in git.stdout.splitlines()]


def run(name, folder):
    if name == PYTEST:
        return subprocess.run([sys.executable, "-m", "pytest", "-q"],
                              capture_output=True, text=True, cwd=folder)
    npm = "npm.cmd" if os.name == "nt" else "npm"  # Windows has npm.cmd, not npm.exe
    return subprocess.run([npm, "test"], capture_output=True, text=True,
                          cwd=Path(folder) / "web", encoding="utf-8", errors="replace")


def main():
    always = "--always" in sys.argv
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    folder = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR", ".")
    failed = []
    for name in commands(None if always else changed_paths(folder), always):
        result = run(name, folder)
        if result.returncode not in PASSING[name]:
            lines = (result.stdout + result.stderr).splitlines()[-TAIL:]
            failed.append(f"{name} failed:\n" + "\n".join(lines))
    if failed:
        print("Tests are failing. Fix them before finishing.\n" + "\n\n".join(failed),
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
