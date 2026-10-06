# Stage 2 plan

Built from docs/prd/stage-2-decisions.md (D70-D119). Stage 1 is built:
`fpl/score.py` and `fpl/sections/lineup.py` read only a feed dict, so a
rebuilt "feed as it was" runs through them unchanged.

## Skeleton (made in step 1)

- New package `fpl/eval/`, run as `python -m fpl.eval` (D81). The brief's
  code is not changed, apart from one optional argument in `score.py`
  (step 5).
- `fpl/eval/run.py` holds the two shared lists:
  - `FORMULAS = [current]` — modules in `fpl/eval/formulas/`, each with
    `NAME` and `scores(feed) -> {element id: next-GW score}` (D100).
  - `MEASURES = [captain]` — modules in `fpl/eval/measures/`, each with
    `columns(formula_names) -> [labels]`, `measure(gw) -> {label: number
    or None}` for one gameweek, and `total(label, values)` for the Total
    row. `gw` is one replayed gameweek: the rebuilt feed, real points,
    the owner's picks, and every formula's scores.
  To switch a slice on: add its file, add one line to one of these lists.
  These two lists are the only lines later steps share. Order follows
  D102: captain, eleven, ranking, top 20; formulas current, shrink.
- `fpl/eval/replay.py` rebuilds the past (D86-D89) and is pure: data in,
  numbers out, no network, no file reads.
- `fpl/eval/report.py` prints the header and table and names the
  results file. Measures do not format the table themselves.
- Shared test helper `tests/evalfeed.py` (small hand-made eval folder
  data: bootstrap, fixtures with kick-off times, live files with
  `explain` rows, picks) is made in step 1. Later steps do not edit it;
  a test takes a fresh copy and changes its own copy. `tests/conftest.py`
  (network guard, D77) is not edited.
- Steps never edit this plan file. Tuning numbers (30 days, K = 3,
  top 20) are named constants at the top of their file.

## Waves

| Wave | Steps | Notes |
|------|-------|-------|
| 1 | 1 | skeleton, end to end |
| 2 | 2, 3, 4, 5 | share only `MEASURES` / `FORMULAS` in `run.py` |
| 3 | 6 | needs step 3's pool |
| 4 | 7 | verdict line, worked example, golden |

---

## Step 1: Replay, captain column, saved table — Wave 1 — DONE

Depends on: none.

After it the user can run `python -m fpl.eval` (or `--team <id>`) and
see a table with one row per replayed gameweek (2-5 today) and a Total
row, with captain columns `current`, `mine`, `best`. The header names
the team, gameweeks covered ("2-5 (4 of 5 finished; GW1 skipped)"),
folder and commit, and prints "Few gameweeks: small differences are
likely noise." and "Injury news is not replayed, so 'mine' has an
advantage the formulas don't." The same text is saved to
`results/YYYY-MM-DD-<commit>.txt`. Downloads land in
`data/raw/YYYY-MM-DD-eval/`; `--from <folder>` replays with no network.

Creates:
- `fpl/eval/__init__.py`, `fpl/eval/__main__.py`: `--team` (default
  8027067), `--from`; error messages and exit codes as D104 (missing
  file named, exit 1; feed down / team not found as D45/D46; "No
  finished gameweeks to replay." exit 0).
- `fpl/eval/download.py`: `download(team)` fetches bootstrap-static,
  fixtures, and `event/{gw}/live/` and `entry/{team}/event/{gw}/picks/`
  for every finished gameweek, reusing `fpl.download._get` (same
  User-Agent, timeout, errors). Checks the team exists first with
  `entry/{team}/` (not saved). A file that already exists in today's
  folder is reused and never rewritten, bootstrap and fixtures included;
  only missing files are fetched. A picks 404 saves nothing (team did
  not exist yet). `load(folder)` reads it back; bootstrap, fixtures and
  each needed live file must exist (else `MissingFile`), picks are
  optional per gameweek.
- `fpl/eval/replay.py`:
  - finished gameweeks: `finished` and `data_checked` both true; the
    rest are listed as skipped (D83). Gameweek 1 is never replayed
    (D82).
  - `as_of(bootstrap, fixtures, lives, gw, now=None)`: a feed dict in
    the shape `fpl.feed.load` gives. Elements keep only id, names,
    position, club; `now_cost` = start price (`now_cost -
    cost_change_start`); minutes and total points = sums over live
    files before `gw`; points per game = total / matches with minutes
    > 0, counted per fixture from `explain` (that count is also kept
    on the element as `appearances`); form = points in matches
    that kicked off in the `FORM_DAYS = 30` days before `now` (default
    `gw`'s deadline) / club's matches in that window; both rounded to
    1 decimal; status "a", no chance, empty news (D86-D88). Fixtures
    are `finished` when they kicked off before the deadline; event
    `gw` is `is_next` (D89). Difficulty and club come from today's
    feed, marked `# known simplification` (D89).
  - real points: `total_points` from that gameweek's live file (D92).
- `fpl/eval/formulas/__init__.py`, `fpl/eval/formulas/current.py`:
  `scores(feed)` = `score.next_score` for every element.
- `fpl/eval/measures/__init__.py`, `fpl/eval/measures/captain.py`
  (D93): each formula's captain = top projected starter of the eleven
  `lineup.best_eleven` picks from the owner's 15 for that gameweek
  (D91), ties by D27; `mine` = the pick with `is_captain`; `best` = the
  highest real points in the squad. Real points counted once; Total =
  sum.
- `fpl/eval/run.py`: `FORMULAS`, `MEASURES`, and the loop over replayed
  gameweeks (gameweeks with no picks are skipped and named, D104).
- `fpl/eval/report.py`: header, table, Total row; commit =
  `git rev-parse --short HEAD`, `-dirty` when tracked files differ from
  HEAD (untracked ignored), `unknown` without git (D115); writes
  `results/YYYY-MM-DD-<commit>.txt`, overwriting the same name (D103).
- `tests/evalfeed.py`.

Changes: `README.md` (how to run the eval; results files are committed
and compared by diff).

Tests: `tests/test_eval_download.py` (fake `requests.get`: folder and
file names; existing files are not rewritten and not fetched; picks
404 skipped; team 404 → team not found; HTTP 500 → feed error),
`tests/test_replay.py` (sums of minutes and points; points per game
over a double gameweek counts two matches; form window includes a
match 29 days back and excludes one 31 days back; changing today's
form, points_per_game, minutes, total_points, status, news and
now_cost leaves the rebuild unchanged; start price; a fixture after
the deadline is not finished; unchecked gameweek skipped; gameweek 1
skipped), `tests/test_eval_captain.py` (hand example (a) below),
`tests/test_eval_cli.py` (`--from` prints the header lines and writes
the results file under a temp dir; dirty and unknown commit; missing
live file named, exit 1; no finished gameweeks message, exit 0; no
picks for a gameweek: skipped and said).

Decisions: D70, D71, D72, D73 (captain), D74 (captain), D76, D77, D78,
D79, D80, D81, D82, D83, D84, D85, D86, D87, D88, D89, D91, D92, D93,
D100 (list, "current"), D102 (header, rows, captain columns), D103,
D104, D105, D106 (network guard), D107 (a), D111, D113 (captain), D115.

## Step 2: Eleven columns — Wave 2 — DONE

Depends on: 1.

After it the table also shows eleven columns: `current`, `mine`,
`best`.

Creates: `fpl/eval/measures/eleven.py` (D94): each formula's eleven =
`lineup.best_eleven` on its projected scores; `mine` = picks in
positions 1-11; `best` = `lineup.pick_eleven` on real points (valid
formation). Sum of real points, no captain bonus, no auto-subs. Total =
sum.

Changes: `fpl/eval/run.py` (one line in `MEASURES`).

Tests: `tests/test_eval_eleven.py` (hand example (b) below; mine uses
positions 1-11 whatever the scores; no captain doubling).

Decisions: D73 (eleven), D74 (eleven), D94, D102 (eleven columns),
D107 (b).

## Step 3: Ranking columns — Wave 2 — DONE

Depends on: 1.

After it the table also shows ranking columns: one per formula and
`price`, each the Spearman correlation for that gameweek, Total = mean.

Creates:
- `fpl/eval/pool.py` (D95): players with minutes > 0 in the rebuilt
  feed whose club has a fixture in that gameweek. Step 6 imports it.
- `fpl/eval/measures/ranking.py`: `statistics.correlation(projected,
  real, method="ranked")` over the pool (D96); `price` ranks by start
  price, ties by rebuilt total points then lower id (D97, D113). If it
  cannot be computed (e.g. all projections equal, StatisticsError) the
  cell is `None`, printed "-", and left out of the mean (D117).

Changes: `fpl/eval/run.py` (one line in `MEASURES`).

Tests: `tests/test_eval_ranking.py` (pool excludes a player with 0
minutes and one whose club blanks; perfect order gives 1.0, reversed
-1.0; price column; all-equal projections give "-" and the mean skips
that gameweek).

Decisions: D73 (ranking), D95, D96, D97 (ranking), D102 (ranking
columns), D113 (price), D117.

## Step 4: Rebuild and leak checks on real data — Wave 2 — DONE

Depends on: 1.

After it `python -m pytest` proves the rebuild matches the feed and
cannot see the future.

Creates:
- `tests/data/eval_real/`: one real eval download (bootstrap-static,
  fixtures, live-gw01..05, picks-gw01..05), copied from
  `data/raw/YYYY-MM-DD-eval/` in the main checkout. If none exists, the
  builder runs `python -m fpl.eval` there once (tests never do). Also
  `tests/data/eval_real/gw06-bootstrap-static.json`, a copy of
  `data/raw/2026-10-06-gw06/bootstrap-static.json` (not
  `tests/data/snapshot/`, which is a different download).
- `tests/test_rebuild.py`:
  - rebuild check (D90): `as_of(..., gw=6, now=SNAPSHOT_TIME)` from live
    1-5, `SNAPSHOT_TIME = 2026-10-06 12:55 UTC` as a named constant
    (D119). Minutes and total points equal the gw06 file for every
    player; form and points per game within 0.1 for at least 95% of
    players.
  - leak check: for each replayed gameweek g, changing every number in
    live files g and later leaves every formula's scores for g
    unchanged.

Changes: `fpl/eval/replay.py` only if the form or points-per-game check
misses the bar (D112): change the rule, never the pass marks or the
leak check, and say how in a comment at the rule and in the report. If
it cannot pass, stop and report BLOCKED.

Tests: as above.

Decisions: D87 (proved), D90, D106 (rebuild and leak checks), D112,
D119.

## Step 5: Shrink formula — Wave 2 — DONE

Depends on: 1.

After it every column that has one entry per formula shows a `shrink`
entry beside `current`. The brief still uses `current`.

Creates: `fpl/eval/formulas/shrink.py` (D99): per position, fit
`statistics.linear_regression(start price, base)` over players with
minutes > 0 in the rebuilt feed; typical = fitted base at the player's
start price; shrunk = (n × base + K × typical) / (n + K), `K = 3`, n =
matches with minutes > 0 before the deadline. If a position has fewer
than 2 such players or one price only, that position is not shrunk
(D116). Minutes, chance and fixture factors unchanged.

Changes:
- `fpl/score.py`: `gw_score` and `next_score` take an optional base
  value (default: `base(el)` as now), so the brief is unchanged.
- `fpl/eval/run.py` (one line in `FORMULAS`).

n is the `appearances` field step 1's `as_of` puts on each element.

Tests: `tests/test_shrink.py` (hand example (c) below; fewer than 2
players and one-price cases leave base alone; the fit ignores players
with 0 minutes), plus the existing brief tests still pass unchanged.

Decisions: D75, D99, D100 ("shrink"), D107 (c), D116.

## Step 6: Top 20 columns — Wave 3 — DONE

Depends on: 3.

After it the table also shows top-20 columns: one per formula and
`price`, each the average real points of the 20 highest projected (or
most expensive) players in the pool.

Creates: `fpl/eval/measures/top20.py`: `TOP_N = 20`; any position;
ties by D27 for formulas, by rebuilt total points then lower id for
price (D113); a pool smaller than `TOP_N` uses all of it. Total = sum
(D102 makes only ranking a mean).

Changes: `fpl/eval/run.py` (one line in `MEASURES`).

Tests: `tests/test_eval_top20.py` (picks the top N by projection and by
price; ties; pool smaller than N).

Decisions: D73 (ranking, top 20), D97 (top 20 price), D98, D102 (top-20
columns), D113.

## Step 7: Verdict line, worked example, golden table — Wave 4 — DONE

Depends on: 1-6.

After it the report ends with one line per experimental formula, e.g.
"shrink vs current: top 20 better in 3 of 4 gameweeks, ranking better
in 2 of 4" (strictly better; a tie or "-" is not a win; never says
"switch"). `python -m pytest` checks a hand-worked example and the real
download against a frozen golden table.

Creates:
- `tests/data/eval_example/`: two replayed gameweeks (live 1-3), about
  8 players with interesting numbers in a full 15-man squad (D91 needs
  15; the rest score 0), with captain, eleven, ranking, top N (`TOP_N`
  set to 3, D118) and shrink worked out by hand in
  `tests/data/eval_expected.notes.txt`; expected table in
  `tests/data/eval_expected.txt`.
- `tests/data/eval_golden.txt`: the table from `tests/data/eval_real/`,
  shown to the owner once, then frozen.
- `tests/test_eval_examples.py`: compares everything except the folder
  and commit in the header.

Changes: `fpl/eval/report.py` (the verdict line, D114).

Tests: as above, plus a unit test of the verdict line (wins counted
strictly; "-" never wins).

Decisions: D101 (report never chooses), D106 (example, golden), D114,
D118.

---

## Hand examples (D107)

Real points, projected scores and owner's picks for one gameweek. Each
becomes a unit test in the step named.

### (a) Captain: the formula's captain blanks, the owner's hauls (step 1)

| Player | Pos | Projected | Real | Owner |
|--------|-----|-----------|------|-------|
| X | FWD | 7.2 | 2 | starter |
| Y | MID | 6.1 | 13 | captain |
| Z | DEF | 1.0 | 15 | bench |
| other 12 | | ≤ 5.0 | ≤ 6 | |

X is the top projected starter, so current's captain = X.
Captain: current 2, mine 13, best 15 (Z, best in the whole squad,
counted once, no doubling).

### (b) Hindsight eleven needs a different formation (step 2)

| Player | Proj | Real | Player | Proj | Real |
|--------|------|------|--------|------|------|
| GK1 | 4.0 | 6 | M1 | 5.0 | 3 |
| GK2 | 3.0 | 1 | M2 | 4.9 | 3 |
| D1 | 4.0 | 2 | M3 | 4.8 | 3 |
| D2 | 3.9 | 2 | M4 | 4.7 | 3 |
| D3 | 3.8 | 2 | M5 | 1.0 | 0 |
| D4 | 1.0 | 9 | F1 | 4.5 | 2 |
| D5 | 0.9 | 8 | F2 | 4.4 | 1 |
| | | | F3 | 4.3 | 1 |

- Projected eleven: 3-4-3 (GK1, D1-D3, M1-M4, F1-F3), projected 48.3
  (3-4-3 outfield 44.3 beats 3-5-2 and 4-4-2 at 41.0). Real: 6 + 6 +
  12 + 4 = **28**.
- Hindsight best: 5-4-1 (GK1, D1-D5, M1-M4, F1): 6 + 23 + 12 + 2 =
  **43**. Next best 4-4-2 = 42, 3-4-3 = 41.
- Mine (positions 1-11 = GK1, D1-D4, M1-M4, F1, F2, 4-4-2): 6 + 15 +
  12 + 3 = **36**.

### (c) Shrink pulls the 1-game player harder (step 5)

Four midfielders with appearances; base = 0.3 form + 0.7 ppg.

| Player | Start price | Base | n |
|--------|-------------|------|---|
| C | 40 | 2.0 | 4 |
| D | 80 | 6.0 | 4 |
| A | 60 | 6.0 | 1 |
| B | 60 | 6.0 | 5 |

Fit over C, D, A, B: mean price 60, mean base 5.0; slope = 80 / 800 =
0.1; line: base = 0.1 × price − 1. Typical at price 60 = 5.0.

- A: (1 × 6.0 + 3 × 5.0) / (1 + 3) = 21 / 4 = **5.25** (pulled 0.75)
- B: (5 × 6.0 + 3 × 5.0) / (5 + 3) = 45 / 8 = **5.625** (pulled 0.375)

---

## UNCOVERED

None that need code. Four decisions have nothing to build:
- D101: the owner decides any switch; the brief keeps "current" and the
  verdict line never says "switch" (step 7).
- D108: out of scope list; no step adds those things.
- D109: Claude writes stage 2; how every step is done.
- D110: D41/D65 data/raw/ conflict left for a separate change.

## Notes (my readings; correct them before approving)

- Team check: D84 lists no entry file, but D104 needs "team not found"
  apart from "no picks that gameweek". Step 1 calls `entry/{team}/`
  once to check, without saving it. In `--from`, a missing picks file
  means "no picks" (skip), not "missing file" (exit 1).
- D106's "about 8 players": an eleven needs a 15-man squad (D91), so
  the example has 15 in the squad and about 8 with non-zero numbers.
- "Two-gameweek example" = two replayed gameweeks (2 and 3).
- D102 Total row: ranking is a mean; captain, eleven and top 20 are
  sums (top 20 = sum of each gameweek's average). Say if top 20
  should be a mean too.
- D90's snapshot is `data/raw/2026-10-06-gw06/bootstrap-static.json`
  (the D119 file). `tests/data/snapshot/bootstrap-static.json` is a
  different download and is not used.
- Builders run in worktrees where `data/raw/` (gitignored) is empty;
  step 4 copies from the main checkout's `data/raw/`.
