from fpl.mcp.tools import get_eval_results
from fpl.sections import header

# (label, kind, start of the results file's own line); quoted as the file has it (D322)
EVALS = [("Scoring eval", "scoring", "shrink vs current:"),
         ("Writing eval", "writing", "faithful rate:"),
         ("Tools eval", "tools", "path right:"),
         ("Tools eval", "tools", "answers passing number and name checks:")]
NO_RESULTS = "no results yet"  # D297, D308


def notes(head):
    """The text brief's header lines after the first, plus the first line's parts after the deadline."""
    first, *rest = header.render(head)
    return first.split(" · ")[2:] + rest


def evals():
    out = []
    for label, kind, start in EVALS:
        lines = [x.strip() for x in get_eval_results.text(kind).splitlines()]
        line = next((x for x in lines if x.startswith(start)), NO_RESULTS)
        out.append(f"{label}: {line}")
    return list(dict.fromkeys(out))  # no tools file: "no results yet" once, not twice


def build(run):
    d = run["downloaded"].astimezone()  # the PC's local time (D338)
    return {"downloaded": f"Data downloaded {d:%a} {d.day} {d:%b %H:%M}",
            "notes": notes(run["data"]["header"]),
            "evals": evals()}
