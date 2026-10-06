import argparse
import sys

from fpl import claude
from fpl.eval import report as base
from fpl.eval.tools import report, run


def main(argv=None, ask=claude.ask_tools, results=base.RESULTS_DIR):
    ap = argparse.ArgumentParser(prog="fpl.eval.tools")
    ap.add_argument("--quick", action="store_true", help="each question once (10 calls)")
    quick = ap.parse_args(argv).quick
    result = run.run(ask, runs=1 if quick else run.RUNS)
    c = base.commit()
    text = report.render(result, c)
    print(text)
    print(f"Saved to {report.save(text, c, quick, results)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
