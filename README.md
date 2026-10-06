# FPL scout

Weekly Fantasy Premier League brief from the official feed.

    python -m fpl                  # download and print the brief
    python -m fpl --team <id>      # another team
    python -m fpl --from <folder>  # replay a saved download, no network
    python -m fpl --json           # print the data instead of text
    python -m fpl --no-explain     # brief only, no explanation
    python -m fpl --explain        # force the explanation (needed with --from)
    python -m pytest               # tests (never touch the live feed)

Downloads are saved in `data/raw/YYYY-MM-DD-gwNN/`. A rerun the same day never overwrites: it
makes `-2`, `-3`, ... A `--team` run for another team adds `-team<id>`.

## Explanation

After the brief, `haiku` writes a short plain-English explanation of it by
running Claude Code (`claude -p`). It uses your own Claude Code login and
counts against your plan limits; there is no API key. `--from` skips it unless
`--explain` is given; `--json` never calls it; if both flags are given the last
wins. If Claude Code is missing, fails, times out, or the text quotes a number
that is not in the brief, one `Explanation skipped: ...` line is printed instead.
The prompt is `fpl/explain/writer.txt`; edit it freely.

Known gaps in the live checks: a name that is not in the feed at all is not
caught; numbers written as words are not caught; a real number from the brief
attached to the wrong player passes. The judge in the writing eval is the
backstop.

## Eval

    python -m fpl.eval                  # download and replay finished gameweeks
    python -m fpl.eval --team <id>      # another team
    python -m fpl.eval --from <folder>  # replay a saved download, no network

Downloads go to `data/raw/YYYY-MM-DD-eval/` (files already there are reused).
The table is printed and saved to `results/YYYY-MM-DD-<commit>.txt`. Results
files are committed; compare two runs by diffing them.

## Writing eval

    python -m fpl.eval.writing          # explain 4 saved briefs, 3 runs each

Runs the real writer (`claude -p`, so it spends your Claude Code plan limits,
at most 40 calls) on the example briefs and the gameweek-6 snapshot, and scores
each text with the code checks. The table, totals, PASS or FAIL (PASS only at
100% of checks) and every text are printed and saved to
`results/YYYY-MM-DD-<commit>-writing.txt`.

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
