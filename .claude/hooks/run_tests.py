"""Stop hook: if Python files changed, the tests must pass before Claude can finish.

If git cannot say what changed (for example the folder is not a git
repository), the tests run anyway. Exit code 2 blocks and shows the failures.
"""
import json
import os
import subprocess
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}
folder = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR", ".")

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