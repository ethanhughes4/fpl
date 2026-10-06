# Stage 1 plan

Built from docs/prd/stage-1-decisions.md (D1-D60). Repo has no code yet.

## Skeleton (made in step 1)

- `fpl/brief.py` holds `SECTIONS`, a list of section modules. That list is
  the only file later steps share.
- Each section is one file in `fpl/sections/` with two functions:
  `build(feed) -> dict` (plain data, D50) and `render(data) -> list[str]`
  (text lines). `brief.build` runs every section in list order and
  returns `{section_name: data}`. `--json` prints that dict; text mode
  prints each section's `render` in order.
- To switch a slice on: add its file, add one line to `SECTIONS`.
- Shared logic that more than one section needs lives in its own file
  (`picks.py`, `score.py`, `squad.py`, `money.py`), created by the first
  step that needs it and only imported afterwards.
- Shared test helpers (`tests/conftest.py`, `tests/fakefeed.py`) are
  made in step 1. Steps in waves 2 and 3 do not edit them. A test that
  needs a different feed takes a fresh copy from `make_feed()` and
  changes its own copy.
- Steps never edit this plan file. I mark each step DONE after its
  tests pass, including steps run in parallel.
- D54 reads as "one package `fpl/`"; the sections live in a
  subpackage of it.
- Tunable numbers sit as named constants at the top of the file that
  uses them (D39, CLAUDE.md).

Section order in `SECTIONS` follows D51: header, money, captain,
lineup, transfers, warnings.

## Waves

| Wave | Steps | Notes |
|------|-------|-------|
| 1 | 1 | skeleton, end to end |
| 2 | 2, 3 | share only `SECTIONS` |
| 3 | 4, 5, 6 | share only `SECTIONS` |
| 4 | 7 | acceptance |

---

## Step 1: Download, replay, header — Wave 1 — DONE

Depends on: none.

After it the user can run `python -m fpl` (or `--team <id>`) and see
`Gameweek 6 · deadline Sat 11 Oct 12:30` (local time). The six downloads
appear in `data/raw/YYYY-MM-DD-gw06/`. `python -m fpl --from <folder>`
prints the same brief without the network, and `--json` prints it as
JSON. Feed errors, unknown team, no upcoming gameweek and missing files
print their messages and exit codes.

Creates:
- `fpl/__init__.py`, `fpl/__main__.py`: arguments `--team` (default
  8027067), `--from`, `--json`; maps errors to messages and exit codes.
- `fpl/download.py`: fetches the six endpoints with a browser-like
  User-Agent and 30 s timeout, no retries; writes them to
  `data/raw/YYYY-MM-DD-gwNN/` (overwrites the same day and gameweek).
  If the last picks show a Free Hit, also fetches the picks of the
  gameweek before, as `picks-gwMM.json`. Raises on non-200 / 404.
- `fpl/picks.py`: which picks to use (the last picks; if they show a
  Free Hit, the gameweek before, since a Free Hit squad reverts), and
  the list of pending transfers (transfers whose event is the upcoming
  gameweek). Steps 2 and 3 import it and do not change it.
- `fpl/feed.py`: loads a folder into one dict, names any missing file;
  `num()` turns text or null into a number (null/missing = 0); finds
  the upcoming gameweek (`is_next`).
- `fpl/brief.py`: `SECTIONS`, `build`, `render`.
- `fpl/sections/__init__.py`, `fpl/sections/header.py`: gameweek and
  local deadline.
- `.gitignore`: `data/raw/`.
- `tests/conftest.py`: autouse guard that makes any network connection
  fail the test, and a `feed` fixture that returns `make_feed()`.
- `tests/fakefeed.py`: `make_feed()` returns a fresh small hand-made
  feed (a few teams, a full 15-player squad, fixtures for six
  gameweeks, picks, history, transfers) in the same shape `feed.py`
  loads. Small builders (`player()`, `fixture()`, `transfer()`) let a
  test add or change rows in its own copy.
- `tests/data/snapshot/`: one real download copied from `data/raw/`
  (I run the live command once while building; tests never do).

Changes: none.

Tests: `tests/test_feed.py` (text to number, null and missing to 0,
upcoming gameweek, missing file named), `tests/test_download.py` (fake
`requests.get`: file names and folder, User-Agent and timeout sent, HTTP
500 and 404 raise the right errors, the earlier picks file is fetched
after a Free Hit and not otherwise), `tests/test_picks.py` (last picks
used normally; the gameweek before after a Free Hit; pending transfers
are only those for the upcoming gameweek), `tests/test_cli.py` (`--from`
snapshot prints the header; `--json` parses; the D45/D46/D47/D48
messages and exit codes), plus a test that the network guard trips.

Decisions: D1 (start), D5, D6, D7, D8, D11, D13, D14, D15 (gameweek,
deadline), D16, D29 (which picks, pending transfers), D41, D42, D43,
D44, D45, D46, D47, D48, D50, D53, D54, D55 (text-to-number, online
guard), D59.

## Step 2: Starting eleven and bench — Wave 2 — TODO

Depends on: 1.

After it the user sees the starting eleven with formation (e.g. 3-5-2)
and each player's next-GW and six-GW scores, then the bench.

Creates:
- `fpl/squad.py`: current squad = the picks `picks.py` chooses, with
  `picks.py`'s pending transfers applied.
- `fpl/score.py`: base (0.6 form + 0.4 ppg), minutes factor (club's
  finished fixtures), fixture factor 1.2..0.8, playing chance (next week;
  weeks 2-6 halfway to 100%; "u"/"n" = 0), blank = 0, double = sum,
  six-week weights 1.0..0.5, tie-break key (total_points, then lower
  id). All weights and factors are named constants.
- `fpl/sections/lineup.py`: best valid eleven by next-GW score
  (1 GK, 3-5 DEF, 2-5 MID, 1-3 FWD), bench in order.
- `README.md`: how to run; advice is weak before about gameweek 4.

Changes: `fpl/brief.py` (one line in `SECTIONS`).

Tests: `tests/test_score.py` (each factor, null chance with status "a"
and not "a", weeks 2-6 chance, blank and double gameweek, weights,
tie-break), `tests/test_squad.py` (pending transfer swaps a player in),
`tests/test_lineup.py` (formation always valid, picks the best eleven
on a small hand-made squad).

Decisions: D2, D3, D9, D18, D19, D20, D21, D22, D23, D24, D25, D26
(eleven), D27, D28, D29 (applying the swaps), D39 (score constants), D51 (XI, bench), D55
(current squad, score with weights, valid formation).

## Step 3: Bank and free transfers — Wave 2 — TODO

Depends on: 1.

After it the user sees `Bank 0.5m · Free transfers 4` under the header.

Creates:
- `fpl/money.py`: bank from the picks `picks.py` chooses, adjusted for
  `picks.py`'s pending transfers;
  selling price (purchase price + rise × sell-on fee from
  game_settings, rounded down; now_cost if fallen; purchase price from
  transfers, ignoring transfers made in Free Hit weeks, or
  now_cost - cost_change_start); free transfers from
  history (GW1 unlimited, +1 a week, cap 1 + max_extra_free_transfers
  from game_settings, Wildcard/Free Hit keep the count, pending
  transfers use them); price printing (61 → 6.1m).
- `fpl/sections/money.py`: the bank / free transfers line.

Changes: `fpl/brief.py` (one line in `SECTIONS`).

Tests: `tests/test_money.py` (price printing, selling price rise/fall/
rounding, a buy-back in a Free Hit week does not change the purchase
price, bank with a pending transfer, free transfers = 4 at gameweek 6
from the snapshot history, cap, chip weeks).

Decisions: D10, D12, D15 (bank, free transfers), D30, D31, D32, D55
(prices, selling price, free transfers), D60.

## Step 4: Captain and vice-captain — Wave 3 — TODO

Depends on: 2.

After it the user sees `Captain: X (7.4)` and `Vice: Y (6.1)` above the
eleven.

Creates: `fpl/sections/captain.py` (top two next-GW scores among the
eleven chosen by `lineup`).

Changes: `fpl/brief.py` (one line).

Tests: `tests/test_captain.py` (highest starter, vice is second, tie
broken by D27, never a bench player).

Decisions: D1 (captain), D17, D26 (captain), D51 (captain, vice), D55
(captain).

## Step 5: Injury and blank warnings — Wave 3 — TODO

Depends on: 2.

After it the user sees a warnings list: name, chance and the feed's news
text for any of the 15 with status not "a", chance below 100%, or no
fixture next gameweek.

Creates: `fpl/sections/warnings.py`.

Changes: `fpl/brief.py` (one line).

Tests: `tests/test_warnings.py` (each of the three triggers, a fit player
with a fixture gives no warning).

Decisions: D1 (warnings), D40, D51 (warnings).

## Step 6: Transfer suggestions — Wave 3 — TODO

Depends on: 2, 3.

After it the user sees up to two transfers with six-week gain and a hit
line, or `No transfer worth making. Save it — you'll have N free next
week.`

Creates: `fpl/sections/transfers.py`: candidates same position, status
"a" and chance ≥ 75%; budget from bank + selling price; max three per
club; gain = six-GW in minus out (marked `# known simplification`, D37);
best 50 singles then every pair; free transfer only if gain ≥ 2, hit
only if that transfer gains ≥ 8; never more than two. Thresholds and 50
are named constants.

Changes: `fpl/brief.py` (one line).

Tests: `tests/test_transfers.py` (each rule: position, budget, three per
club, injured player never suggested, gain below 2 saved, hit only at
≥ 8, never three transfers, pair respects shared budget, save message
with next week's count).

Decisions: D1 (transfers), D4, D26 (transfers), D33, D34, D35, D36,
D37, D38, D39 (transfer constants), D49, D51 (transfers, hit line), D55
(each rule).

## Step 7: Worked examples and golden file — Wave 4 — TODO

Depends on: 1-6.

After it `python -m pytest` checks three hand-made weeks against briefs
worked out by hand, and the real snapshot against a frozen golden brief.
The owner then runs `python -m fpl` live once and checks squad, bank and
free transfers against the FPL site.

Creates:
- `tests/data/example_a/`, `example_b/`, `example_c/`: about 15-20
  players each, same six-file layout so `--from` reads them. (a) normal
  week, no transfer; (b) injured starter, one free transfer and a
  warning; (c) free transfers already used by a pending transfer, one
  gain ≥ 8, hit suggested.
- `tests/data/expected_a.txt`, `expected_b.txt`, `expected_c.txt`, with
  the hand arithmetic in a comment file beside each.
- `tests/data/golden.txt`: snapshot brief, shown to the owner once, then
  frozen.
- `tests/test_examples.py`.

Changes: `README.md` (add the D56 live check).

Tests: the three examples and the golden file.

Decisions: D52, D55 (examples, golden), D56.

---

## UNCOVERED

None that need code. Two decisions have nothing to build:
- D57 (Claude writes stage 1, owner edits): how every step is done.
- D58 (out of scope): a list of things not to build; no step adds them.

## Notes

- D51 refers to a sample layout sent with question 35 that is not in
  the repo. Steps follow D51's listed order; the owner approves the look
  at the golden file in step 7.
- Example (c) "no free transfers" needs a pending transfer for the
  upcoming gameweek, because under D32 the count is never 0 at the
  start of a gameweek.
