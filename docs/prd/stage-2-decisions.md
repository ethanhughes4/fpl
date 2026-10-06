# Stage 2 decisions

Context found before questioning (2026-10-06):

- Stage 1 is built and tested (D1-D69). `python -m fpl` prints the brief;
  `--json` prints the same brief as plain data (D50).
- The only written hint about stage 2 is D50: "stage 2 gives it to a
  model, stage 3 scores it". D3 and D58 say stage 1 has no AI.
- The `anthropic` Python library 0.125.0 is installed. No
  ANTHROPIC_API_KEY is set in the shell.
- One real download exists: data/raw/2026-10-06-gw06/.
- Numbering continues from stage 1, starting at D70.

Also found: the scoring code (score.py, lineup.best_eleven) reads only
the feed dict, so a replay can build a "feed as it was" and run the
same code unchanged. Events have `finished` and `deadline_time`;
gameweeks 1-5 are finished, 6 is next.

## Decisions given up front by the owner (2026-10-06)

D70: Stage 2 is evals for the scoring. No AI yet. Replaces D50's "stage 2 gives it to a model". (reason: owner)
D71: Goal: replay finished gameweeks and measure how good the advice was, to compare versions of the scoring formula with evidence. (reason: owner)
D72: For each finished gameweek, build the advice using only what was known before that deadline, then score it against the points players really got. (reason: owner)
D73: Measure three things: the captain pick, the starting eleven, and how well projected scores rank all players. (reason: owner)
D74: Compare each against two baselines: the best possible choice in hindsight, and what the owner actually picked that week. (reason: owner)
D75: First experiment: pull each player's average part of the way toward what is typical for his position and price, more strongly when he has played few games; compare it with the current formula. (reason: owner)
D76: One command prints a results table and saves it to a file, so two runs can be compared. (reason: owner)
D77: Tests never call the live feed. (reason: owner; CLAUDE.md)
D78: Past gameweeks are rebuilt from the feed; event/{gw}/live/ gives every player's points and minutes for a finished gameweek. Only one download is saved. (reason: feed fact)
D79: Past injury news is not available, so the replay treats every player as fit. (reason: feed fact)
D80: Only five gameweeks are finished, so results are noisy; the report says how many gameweeks it covers. (reason: owner)

## Questions sent as one list (2026-10-06) — owner replied only where he disagreed

### Running it
D81: Run with `python -m fpl.eval`, `--team` (default 8027067) and `--from <folder>`. The brief's command is unchanged. (reason: keep brief and eval apart)
D82: Replay every finished gameweek from 2 on; gameweek 1 is skipped because nothing is known before it (D64 gives every player 0). Today that is gameweeks 2-5. (reason: gameweek 1 would only add zeros)
D83: A gameweek counts as finished when its event has `finished` and `data_checked` both true; an unchecked one is skipped and the report says so. (reason: bonus points are final only after the check)

### Downloads
D84: Eval downloads go to data/raw/YYYY-MM-DD-eval/: bootstrap-static.json, fixtures.json, and live-gwNN.json and picks-gwNN.json for every finished gameweek. Same User-Agent, timeout and errors as D44-D46. `--from <folder>` replays a saved folder with no network. (reason: leaves the brief's folders alone)
D85: A rerun never overwrites or deletes anything in data/raw/. A file that already exists in today's eval folder is reused, not downloaded again; only missing files are fetched. (reason: owner — keeps the CLAUDE.md boundary true)

### Rebuilding the past
D86: From today's feed only id, names, position, club and start price (now_cost - cost_change_start, in tenths) are used. Today's now_cost, form, points_per_game, minutes, total_points, status, chance and news are never used in a replay. (reason: today's values carry the future; price rises follow good games)
D87: For deadline g, only live data of gameweeks before g is used. Minutes and total points = sums so far. Points per game = total points / matches with minutes > 0, counted per match from the live data's per-fixture "explain" rows, so double and blank gameweeks are right (0 if none). Form = the player's points in matches that kicked off in the 30 days before g's deadline / his club's matches in that window (0 if none). Both rounded to 1 decimal as the feed does. 30 days is a named constant. (reason: owner — count matches, not gameweeks. Checked event/5/live/ on 2026-10-06: each element has explain = [{fixture, stats: [{identifier, points, value}]}])
D88: Every player is treated as fit: status "a", no chance set, which D22 reads as 100% (D79). The report prints: "Injury news is not replayed, so 'mine' has an advantage the formulas don't." (reason: owner)
D89: A fixture counts as played when it kicked off before g's deadline. Difficulty and club come from today's feed; both are written down as known simplifications (FPL revises difficulty; a few players changed club in August). (reason: no history for either in the feed)
D90: Rebuild check: rebuilding "as of gameweek 6" from live 1-5 must match the saved gameweek-6 snapshot exactly on minutes and total points for every player, and within 0.1 on form and points per game for at least 95% of players. Leak check: changing live data for gameweek g or later leaves the projections for g unchanged. (reason: proves no leak instead of promising it; owner — also confirms D87 matches the feed)

### Measures
D91: Each week's squad is the owner's actual 15 from that gameweek's picks (Free Hit and Wildcard squads included). Each formula picks captain and eleven from that squad. Transfers are not evaluated. (reason: like for like with "mine")
D92: Real points = that gameweek's total_points in the live data (a double gameweek is already summed). (reason: official number)
D93: Captain = real points of the chosen captain, counted once, chips ignored; totalled over gameweeks. Baselines: best in the squad in hindsight, and the owner's captain. (reason: doubling changes no comparison)
D94: Eleven = sum of the eleven's real points, no captain bonus, no auto-subs. Hindsight best = best valid-formation eleven by real points, using stage 1's picker. Mine = pick positions 1-11. (reason: auto-subs hide bad starts; same rule for all three)
D95: The player pool for ranking and top 20 = players with at least one appearance (minutes > 0) before that deadline whose club has a fixture that gameweek. (reason: owner)
D96: Ranking = Spearman rank correlation (1 = projected order matches real order, 0 = no better than chance) between projected next-GW score and real points over the pool, each gameweek, then the mean. Uses statistics.correlation(..., method="ranked"), checked to work on Python 3.13.6 here. (reason: standard measure, in the standard library)
D97: Ranking is also shown for "price only" (rank by start price) as a floor; hindsight and "mine" have no ranking column. (reason: a formula that can't beat price adds nothing)
D98: Top 20 = for each formula, the 20 highest projected players in the pool (any position), average real points; shown beside "price only" (the 20 most expensive by start price). In the table and in the hand-made example. 20 is a named constant. (reason: owner)

### The experiment
D99: base = 0.3 x form + 0.7 x points per game (D61). typical = the base predicted for the player's position and start price by a straight line fitted per position over players with at least one appearance, using only data from before that deadline (statistics.linear_regression). shrunk = (n x own base + K x typical) / (n + K), n = matches with minutes > 0 before the deadline, K = 3 (named constant). Minutes and fixture factors unchanged. (reason: owner confirmed the fit uses only pre-deadline data)
D100: Formulas sit in one named list ("current", "shrink"); every run scores all of them, one column each. The brief keeps "current". No other K values until the owner asks. (reason: owner)
D101: The brief switches to a new formula only if it beats "current" on top 20 and on ranking in most gameweeks, and the owner decides, not the eval. (reason: owner)

### Output
D102: One row per replayed gameweek plus a Total row (ranking: mean). Columns: captain (each formula, mine, best), eleven (each formula, mine, best), ranking (each formula, price), top 20 (each formula, price). The header names team, gameweeks covered ("2-5 (4 of 5 finished; GW1 skipped)"), folder and commit, and says "Few gameweeks: small differences are likely noise." No confidence intervals or significance tests. (reason: 4 gameweeks are too few; per-gameweek rows show consistency)
D103: The table is saved as results/YYYY-MM-DD-<commit>.txt, the same text as printed, committed to git; compare by opening or diffing two files. With uncommitted changes the commit reads "<commit>-dirty" in the header and the file name. (reason: owner — the name says which code made it)

### Failures
D104: Missing file in --from: name it, exit 1 (D48). Feed down or team not found: D45/D46. No finished gameweek after 1: "No finished gameweeks to replay.", exit 0. No picks for a gameweek (team did not exist yet): skip it and say so. (reason: same as stage 1)

### Technical
D105: Python 3.13 standard library (statistics), requests, pytest. No numpy, pandas or scipy. No running cost. (reason: nothing needs more)

### Proof
D106: Tests: D90's rebuild and leak checks on live files copied into tests/data/; a hand-made two-gameweek example (about 8 players) with captain, eleven, ranking, top 20 and shrink worked out by hand; a unit test of the shrink formula; one golden table from the real eval download, checked by eye once then frozen; the existing network guard. (reason: same pattern as D52/D55)
D107: Three hand examples are written during planning: (a) the formula's captain blanks and the owner's hauls; (b) the hindsight eleven needs a different formation from the projected one; (c) two players with equal base but 1 vs 5 appearances, showing the 1-game player pulled harder. (reason: one rule per example)

### Boundaries and ownership
D108: Out of scope: transfers, vice-captain, bench order, chips, the six-week score, price changes, AI, charts, any change to the brief's output. (reason: keep to D73)
D109: Claude writes all of stage 2; the owner reads and edits. (reason: owner)

## Follow-ups (2026-10-06) — all accepted as recommended

D110: Known conflict: D41 (same-day brief rerun overwrites its folder) and D65 (rerun removes the this-week.json copy) break the CLAUDE.md data/raw/ boundary that D85 keeps. Stage 2 leaves them alone; they are fixed as a separate change. (reason: keep stage 2 to evals)
D111: D85's reuse covers every file, bootstrap-static.json and fixtures.json included, so a gameweek checked later the same day is picked up the next day. (reason: the alternative is overwriting)
D112: If D90's form or points-per-game check misses the bar, the builder may change D87's rebuild rule to match the feed and records how. It never changes D90's pass marks (exact for minutes and total points; within 0.1 for 95% of players on form and points per game) and never the leak check. If it cannot pass with those marks, it stops and asks the owner. (reason: owner — the feed's exact form rule is not published; the test decides, and the test is fixed)
D113: Ties: projected scores by D27 (higher rebuilt total points, then lower id); price-only by higher rebuilt total points, then lower id. A pool smaller than 20 uses all of it. (reason: same input, same output)
D114: The report adds one line per experimental formula, e.g. "shrink vs current: top 20 better in 3 of 4 gameweeks, ranking better in 2 of 4". Strictly better only; a tie is not a win. It never says "switch" (D101). (reason: the evidence for D101 on one line)
D115: "Dirty" = tracked files differ from the last commit; untracked files do not count. No git = commit "unknown". A rerun with the same date and commit overwrites its results file (results/ is not data/raw/). (reason: an uncommitted results file must not make the next run dirty)
D116: If a position has fewer than 2 players with an appearance, or they all have one price, the line cannot be fitted: that position is not shrunk that gameweek (typical = own base). (reason: rare; never pull toward a made-up number)
D117: If Spearman cannot be computed (e.g. all projections equal), the cell shows "-" and that gameweek is left out of the mean. (reason: no crash, no fake number)
D118: The hand-made example sets the top-N constant to 3. (reason: small enough to check by hand)

## Final tightenings (2026-10-06)

D119: In D90's rebuild check, the 30-day form window counts back from the moment the saved snapshot was downloaded, because that is when the feed worked form out. That moment is 2026-10-06 12:55 UTC (modification time of data/raw/2026-10-06-gw06/bootstrap-static.json, read 2026-10-06), written into the test as a named constant because copies lose file times. In the replay, the window counts back from the gameweek's deadline (D87). (reason: owner. Note: the window then starts 2026-09-06 12:55 UTC, five minutes before a 13:00 kick-off that day; both 6 September matches fall inside)
