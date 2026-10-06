"""Header, table and results file. Measures do not format anything."""
import subprocess
from datetime import date
from pathlib import Path

from fpl.eval import run

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


def wins(result, measure, new, old):
    """(gameweeks where `new` is strictly better than `old`, gameweeks replayed). None is no win."""
    rows = result["rows"].values()
    n = sum(1 for r in rows if None not in (r.get(f"{measure} {new}"), r.get(f"{measure} {old}"))
            and r[f"{measure} {new}"] > r[f"{measure} {old}"])
    return n, len(result["rows"])


def verdict(result, names):
    """D114: one line per formula after the first. Evidence only, never a recommendation (D101)."""
    out = []
    for name in names[1:]:
        t, n = wins(result, "top20", name, names[0])
        r, _ = wins(result, "ranking", name, names[0])
        out.append(f"{name} vs {names[0]}: top 20 better in {t} of {n} gameweeks, "
                   f"ranking better in {r} of {n}")
    return out


def render(result, team, folder, commit_name):
    cols = result["columns"]
    head = [f"FPL eval: team {team}", f"Gameweeks: {covered(result)}",
            f"Folder: {folder}", f"Commit: {commit_name}", FEW, INJURY, ""]
    lines = [["GW"] + cols]
    lines += [[str(g)] + [cell(r.get(c)) for c in cols] for g, r in result["rows"].items()]
    lines.append(["Total"] + [cell(result["totals"][c]) for c in cols])
    widths = [max(len(row[i]) for row in lines) for i in range(len(lines[0]))]
    table = ["  ".join(c.rjust(w) for c, w in zip(row, widths)) for row in lines]
    names = [f.NAME for f in run.FORMULAS]
    return "\n".join(head + table + [""] + verdict(result, names))


def save(text, commit_name, root=RESULTS_DIR, today=None):
    """results/YYYY-MM-DD-<commit>.txt; the same name is overwritten (D103, D115)."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{today or date.today():%Y-%m-%d}-{commit_name}.txt"
    path.write_text(text + "\n", encoding="utf-8")
    return path
