# FPL scout

Weekly Fantasy Premier League brief from the official feed.

    python -m fpl                  # download and print the brief
    python -m fpl --team <id>      # another team
    python -m fpl --from <folder>  # replay a saved download, no network
    python -m fpl --json           # print the data instead of text
    python -m pytest               # tests (never touch the live feed)

Downloads are saved in `data/raw/YYYY-MM-DD-gwNN/`.

Advice is weak before about gameweek 4: form and minutes need a few matches.

## Live check (once, by the owner)

Run `python -m fpl` against the live feed and compare the squad, bank and
free transfers with the FPL site (Transfers page). Tests cannot prove this.
