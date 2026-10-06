import re
import subprocess

from fpl.mcp.session import ROOT

DESCRIPTION = (
    "The newest saved eval results file of one kind: kind is \"scoring\", \"writing\" or "
    "\"tools\". Returns the file name and its text."
)

RESULTS = ROOT / "results"
KINDS = ("scoring", "writing", "tools")
NAME = re.compile(r"(\d{4}-\d\d-\d\d)-([^-]+)(-dirty)?(?:-(writing|tools|tools-quick))?\.txt")
GIT_TIMEOUT = 10  # seconds


def _log():
    """Short commit hashes, newest first. Empty without git."""
    try:
        r = subprocess.run(["git", "log", "--format=%h"], cwd=ROOT, capture_output=True,
                           text=True, timeout=GIT_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        return []
    return r.stdout.split()


def tool(kind: str) -> str:
    if kind not in KINDS:
        return f"Unknown kind {kind!r}. Use scoring, writing or tools."
    order = {h: i for i, h in enumerate(_log())}
    found = []
    for p in RESULTS.glob("*.txt"):
        m = NAME.fullmatch(p.name)
        if m and (m[4] or "scoring") == kind:
            # newest commit = smallest log index; unknown commits last; same commit: later date
            found.append((-order.get(m[2], len(order)), m[1], p))
    if not found:
        return f"No {kind} results file found."
    p = max(found, key=lambda f: f[:2])[2]
    return f"{p.name}\n\n{p.read_text(encoding='utf-8')}"
