"""python -m fpl.mcp [--from <folder>]: serve the tools on stdio (D231)."""
import argparse

from fpl.mcp import server, session


def main(argv=None):
    ap = argparse.ArgumentParser(prog="fpl.mcp")
    ap.add_argument("--from", dest="folder")
    session.start(ap.parse_args(argv).folder)
    server.build().run()


if __name__ == "__main__":
    main()
