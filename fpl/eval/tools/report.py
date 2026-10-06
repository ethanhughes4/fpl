"""Header, table, totals, verdict and the answers (D236, D247). Saved like the other results."""
from fpl.eval import report as base
from fpl.eval.writing.report import _limit, cell  # same plan-limit line and pass / FAIL cells


def _called(calls):
    if not calls:
        return "-"
    return ", ".join(f"{t}({', '.join(str(v) for a in args.values() for v in (a if isinstance(a, list) else [a]))})"
                     for t, args in calls)


def render(result, commit_name):
    rows = result["rows"]
    head = ["FPL tools eval", f"Commit: {commit_name}", f"Model: {', '.join(result['models']) or '-'}"]
    head += _limit(result) + [""]
    lines = [["Q", "Run", "Tools called", "Path", "Numbers", "Names", "Tokens"]]
    lines += [[str(r["q"]), str(r["run"]), _called(r["calls"]), cell(r["path"]), cell(r["numbers"]),
               cell(r["names"]), cell(r["tokens"])] for r in rows]
    widths = [max(len(x[i]) for x in lines) for i in range(len(lines[0]))]
    table = ["  ".join(c.ljust(w) for c, w in zip(x, widths)) for x in lines]
    totals = [f"{label}: {value}" for label, value, _ in result["summary"]]
    totals += [f"Total tokens: {cell(result['tokens'])}", f"Calls: {result['calls']}"]
    if result["stopped"]:
        totals.append(f"Run {result['stopped']}.")
    ok = all(p for *_, p in result["summary"]) and bool(rows) and not result["stopped"]
    out = head + table + [""] + totals + ["", "Verdict: " + ("PASS" if ok else "FAIL"), ""]
    for r in rows:
        out += [f"--- Q{r['q']} run {r['run']}: {r['question']}"]
        if not r["path"]:
            out.append(f"(path wrong: {r['why']})")
        out += [f"(call failed: {r['error']})" if r["error"] else r["text"], ""]
    return "\n".join(out).rstrip()


def save(text, commit_name, quick=False, root=base.RESULTS_DIR, today=None):
    """-tools.txt for a full run, -tools-quick.txt for --quick (D247)."""
    return base.save(text, f"{commit_name}-tools{'-quick' if quick else ''}", root, today)
