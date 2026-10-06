"""Hook: the tests must pass before Claude (or a builder) can finish.

Main session (Stop): runs only if Python files have uncommitted changes.
Builders (SubagentStop, called with --always): always runs, because a
builder commits its work, so git shows nothing as changed.
If git cannot answer, the tests run anyway. Exit code 2 blocks.
"""
import json
import os
import subprocess
import sys

always = "--always" in sys.argv

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}
folder = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR", ".")

if not always:
    git = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=folder,
    )
    if git.returncode == 0 and not any(
        line.strip().endswith(".py") for line in git.stdout.splitlines()
    ):
        sys.exit(0)

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q"],
    capture_output=True, text=True, cwd=folder,
)
if result.returncode in (0, 5):      # 0: all passed. 5: no tests found.
    sys.exit(0)

print(
    "Tests are failing. Fix them before finishing.\n"
    + "\n".join(result.stdout.splitlines()[-30:]),
    file=sys.stderr,
)
sys.exit(2)