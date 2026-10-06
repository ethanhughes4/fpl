import sys

from fpl import claude
from fpl.eval import report as base
from fpl.eval.writing import report, run


def main(ask=claude.ask, results=base.RESULTS_DIR):
    result = run.run(ask)
    c = base.commit()
    text = report.render(result, c)
    print(text)
    print(f"Saved to {report.save(text, c, results)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
