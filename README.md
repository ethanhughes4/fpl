# FPL scout

Weekly Fantasy Premier League brief from the official feed.

    python -m fpl                  # download and print the brief
    python -m fpl --team <id>      # another team
    python -m fpl --from <folder>  # replay a saved download, no network
    python -m fpl --json           # print the data instead of text
    python -m pytest               # tests (never touch the live feed)

Downloads are saved in `data/raw/YYYY-MM-DD-gwNN/`.

## Eval

    python -m fpl.eval                  # download and replay finished gameweeks
    python -m fpl.eval --team <id>      # another team
    python -m fpl.eval --from <folder>  # replay a saved download, no network

Downloads go to `data/raw/YYYY-MM-DD-eval/` (files already there are reused).
The table is printed and saved to `results/YYYY-MM-DD-<commit>.txt`. Results
files are committed; compare two runs by diffing them.

Advice is weak before about gameweek 4: form and minutes need a few matches.

## Transfers made this week

The public feed hides transfers for the coming gameweek until its deadline.
If you have made some, put them in `this-week.json` in the repo root:

    {"gameweek": 6,
     "transfers": [{"out": "Player A", "in": "Player B"}],
     "bank": 0.8}

Names are the ones the brief prints, the surname, or first and last name
(case and accents do not matter); the bank is the one the FPL site shows. The file is used only when its gameweek is the coming
one, and a live run saves a copy with the download so `--from` replays it.

## Live check (once, by the owner)

Run `python -m fpl` against the live feed and compare the squad, bank and
free transfers with the FPL site (Transfers page). Tests cannot prove this.
