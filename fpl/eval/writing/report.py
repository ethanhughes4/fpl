"""Header, table, totals, verdict and the texts (D152, D153). Saved like the other results."""
from fpl.eval import report as base


def cell(v):
    if v is None:
        return "-"
    return {True: "pass", False: "FAIL"}.get(v, str(v))


def _limit(result):
    """D200: calls refused by a Claude plan limit are said plainly, above everything else."""
    n = result.get("plan_limit") or 0
    if not n:
        return []
    return [f"PLAN LIMIT: {n} model call{'' if n == 1 else 's'} failed because a Claude plan limit "
            "was reached. Those rows are not the writer's or judge's fault; run again later."]


def render(result, commit_name):
    rows = result["rows"]
    cols = list(dict.fromkeys(k for r in rows for k in r["scores"]))
    head = ["FPL writing eval", f"Commit: {commit_name}",
            f"Model: {', '.join(result['models']) or '-'}"] + _limit(result) + result["notices"] + [""]
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
