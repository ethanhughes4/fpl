"""Header, table, totals, verdict and the texts (D152, D153). Saved like the other results."""
from fpl.eval import report as base


def cell(v):
    if v is None:
        return "-"
    return {True: "pass", False: "FAIL"}.get(v, str(v))


def render(result, commit_name):
    rows = result["rows"]
    cols = list(dict.fromkeys(k for r in rows for k in r["scores"]))
    head = ["FPL writing eval", f"Commit: {commit_name}",
            f"Model: {', '.join(result['models']) or '-'}"] + result["notices"] + [""]
    lines = [["Brief", "Run"] + cols + ["Tokens"]]
    lines += [[r["brief"], str(r["run"])] + [cell(r["scores"].get(c)) for c in cols] + [cell(r["tokens"])]
              for r in rows]
    widths = [max(len(x[i]) for x in lines) for i in range(len(lines[0]))]
    table = ["  ".join(c.ljust(w) for c, w in zip(x, widths)) for x in lines]
    totals = [f"{label}: {value}" for label, value, _ in result["summary"]]
    totals += [f"Total tokens: {cell(result['tokens'])}", f"Calls: {result['calls']}"]
    if result["stopped"]:
        totals.append(f"Run {result['stopped']}.")
    ok = all(p for *_, p in result["summary"]) and bool(rows) and not result["stopped"]
    out = head + table + [""] + totals + ["", "Verdict: " + ("PASS" if ok else "FAIL"), ""]
    for r in rows:
        out += [f"--- {r['brief']} run {r['run']}",
                f"(call failed: {r['error']})" if r["error"] else r["text"], ""]
    return "\n".join(out).rstrip()


def save(text, commit_name, root=base.RESULTS_DIR, today=None):
    return base.save(text, f"{commit_name}-writing", root, today)
