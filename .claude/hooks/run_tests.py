"""Hook: the tests must pass before Claude (or a builder) can finish.

Main session (Stop): runs pytest if a .py file has uncommitted changes, and
`npm test` in web/ if a file under web/ has (D325).
Builders (SubagentStop, called with --always): always runs both, because a
builder commits its work, so git shows nothing as changed.
If git cannot answer, both run. Exit code 2 blocks.

Timed on Windows (D326), 2026-10-07: pytest 217 s, npm test 26 s, 243 s together.
That passed the 240 s limit, so the limit went to 360 s (D340). After speeding up
the tests: pytest 153 s, npm test 18 s, 171 s together; limit 510 s (D341).
A run past WARN_SHARE of the limit prints a warning, so the tests cannot quietly
outgrow it again.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PYTEST = "pytest"
NPM = "npm"
PASSING = {PYTEST: (0, 5), NPM: (0,)}  # pytest 5: no tests found
TAIL = 30  # lines of a failing run shown
LIMIT = 510  # seconds; must equal both hook "timeout"s in .claude/settings.json (D341)
WARN_SHARE = 0.8  # warn when a run takes more than this share of LIMIT


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


def warning(seconds):
    """A warning line when the tests took more than WARN_SHARE of LIMIT, else None."""
    if seconds <= WARN_SHARE * LIMIT:
        return None
    return (f"WARNING: the tests took {seconds:.0f} s, over {WARN_SHARE:.0%} of the hook's "
            f"{LIMIT} s limit. Speed them up or raise the limit before they time out.")


def main():
    always = "--always" in sys.argv
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    folder = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR", ".")
    failed = []
    start = time.monotonic()
    for name in commands(None if always else changed_paths(folder), always):
        result = run(name, folder)
        if result.returncode not in PASSING[name]:
            lines = (result.stdout + result.stderr).splitlines()[-TAIL:]
            failed.append(f"{name} failed:\n" + "\n".join(lines))
    warn = warning(time.monotonic() - start)
    if failed:
        print("Tests are failing. Fix them before finishing.\n" + "\n\n".join(failed)
              + (f"\n\n{warn}" if warn else ""), file=sys.stderr)
        sys.exit(2)
    if warn:
        print(json.dumps({"systemMessage": warn}))  # shown to the user; does not block


if __name__ == "__main__":
    main()
