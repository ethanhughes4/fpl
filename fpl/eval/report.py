"""Header, table and results file. Measures do not format anything."""
import subprocess
from datetime import date
from pathlib import Path

RESULTS_DIR = Path("results")
FEW = "Few gameweeks: small differences are likely noise."
INJURY = "Injury news is not replayed, so 'mine' has an advantage the formulas don't."


def commit():
    """Short hash, '-dirty' when tracked files differ from HEAD, 'unknown' without git (D115)."""
    here = Path(__file__).parent
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=here,
                           capture_output=True, text=True)
        if h.returncode:
            return "unknown"
        dirty = subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=here).returncode
    except OSError:
        return "unknown"
    return h.stdout.strip() + ("-dirty" if dirty else "")


def covered(result):
    gws = result["gameweeks"]
    contiguous = gws == list(range(gws[0], gws[-1] + 1))
    span = f"{gws[0]}-{gws[-1]}" if contiguous else ",".join(map(str, gws))
    return f"{span} ({len(gws)} of {result['n_finished']} finished; {'; '.join(result['notes'])})"


def cell(v):
    if v is None:
        return "-"
    return f"{v:.2f}" if isinstance(v, float) else str(v)


def render(result, team, folder, commit_name):
    cols = result["columns"]
    head = [f"FPL eval: team {team}", f"Gameweeks: {covered(result)}",
            f"Folder: {folder}", f"Commit: {commit_name}", FEW, INJURY, ""]
    lines = [["GW"] + cols]
    lines += [[str(g)] + [cell(r.get(c)) for c in cols] for g, r in result["rows"].items()]
    lines.append(["Total"] + [cell(result["totals"][c]) for c in cols])
    widths = [max(len(row[i]) for row in lines) for i in range(len(lines[0]))]
    table = ["  ".join(c.rjust(w) for c, w in zip(row, widths)) for row in lines]
    return "\n".join(head + table)


def save(text, commit_name, root=RESULTS_DIR, today=None):
    """results/YYYY-MM-DD-<commit>.txt; the same name is overwritten (D103, D115)."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{today or date.today():%Y-%m-%d}-{commit_name}.txt"
    path.write_text(text + "\n", encoding="utf-8")
    return path
