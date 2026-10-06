import argparse
import sys

from fpl import claude
from fpl.eval import report as base
from fpl.eval.writing import judge, report, run


def check_judge(ask):
    """D195: only the judge check, one call per fixed text. Printed, not saved."""
    counted = run.CountedAsk(ask)
    lines = judge.start({"ask": counted})
    tokens = "-" if counted.tokens is None else counted.tokens
    print("\n".join(["FPL judge check", f"Commit: {base.commit()}",
                      f"Model: {', '.join(counted.models) or '-'}", ""] + lines
                     + ["", f"Total tokens: {tokens}", f"Calls: {counted.calls}"]))
    return 0


def main(argv=None, ask=claude.ask, results=base.RESULTS_DIR):
    ap = argparse.ArgumentParser(prog="fpl.eval.writing")
    ap.add_argument("--judge-check", action="store_true",
                    help="run only the judge check on the fixed texts")
    if ap.parse_args(argv).judge_check:
        return check_judge(ask)
    result = run.run(ask)
    c = base.commit()
    text = report.render(result, c)
    print(text)
    print(f"Saved to {report.save(text, c, results)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
