## Project

FPL scout: a weekly Fantasy Premier League brief (captain, starting
eleven, transfers, injury warnings) built from the official FPL data
feed. Decisions are in docs/prd/. Read the decisions file for the
current stage before changing behaviour.

## Invariants (do not break)

- Prices stay in tenths of a million, as the feed gives them
  (61 = 6.1m). Convert to millions only when printing.
- Every tuning number (weights, thresholds) is a named constant at
  the top of its file. No bare numbers inside functions.
- Code that scores players or checks rules never downloads anything.
  It takes data in and gives numbers out.
- Every new function or feature comes with its own tests in the
  same change.

## Boundaries

- Tests must never call the live feed.
- Never edit or delete anything in data/raw/. Those downloads are
  the history that later evals replay.
- The feed is free and needs no login. Do not add passwords,
  cookies or logins.