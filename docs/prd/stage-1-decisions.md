# Stage 1 decisions

Context found before questioning (2026-10-06): repo is empty apart from
.claude/ (pytest Stop hook, /questions and /prd skills). No CLAUDE.md, no
docs/, no code. Tests run with `python -m pytest`, so Python is implied.

## Decisions given up front by the owner

D1: A terminal command prints a weekly brief for FPL team 8027067: captain, starting eleven, up to two transfers, injury warnings. (reason: owner's stated purpose)
D2: Look six gameweeks ahead, nearer weeks weighted more. (reason: owner decision)
D3: Stage 1 has no AI. Player score is built from form, minutes played, fixture difficulty and chance of playing. (reason: owner decision)
D4: Suggestions follow the game rules: same position, budget, max three players per club, free transfers. A points hit is suggested only for a big gain. (reason: owner decision)
D5: Every download is saved to a dated folder so later evals can replay it. (reason: owner decision)
D6: Python, requests, pytest. Tests never call the live feed. (reason: owner decision; installed: Python 3.13.6, requests 2.34.2, pytest 9.1.1)

## Feed facts given by the owner (base: fantasy.premierleague.com/api/)

D7: bootstrap-static/ gives events, teams and elements (players). fixtures/ gives every match with a difficulty for each side. entry/{id}/, entry/{id}/event/{gw}/picks/, entry/{id}/history/ and entry/{id}/transfers/ describe the owner's team. (reason: feed fact)
D8: Many numbers arrive as text (e.g. "form": "6.0") and must be converted. (reason: feed fact)
D9: chance_of_playing_next_round is null when there is no news. (reason: feed fact)
D10: Prices are in tenths of a million: 61 means 6.1m. (reason: feed fact)
D11: Picks show the team at the last deadline, not transfers made since. (reason: feed fact)
D12: Free transfers are not published and must be worked out from history. For team 8027067 the answer must be 4 for gameweek 6. (reason: feed fact; this is an acceptance check)

## Questions sent as one list (2026-10-06) — owner replies only where they disagree

### Running it
D13: Run with `python -m fpl`. Team ID defaults to 8027067; `--team <id>` overrides it. (reason: simplest; still works for any team)
D14: The brief is for the next gameweek whose deadline has not passed (event with is_next). (reason: only week that can still be acted on)
D15: Brief header shows gameweek, deadline in local time, bank, free transfers. (reason: the facts needed before acting)
D16: Read-only: never logs in, never makes transfers. (reason: no login, no risk)
D17: Brief also names a vice-captain (second-highest next-GW score among the starters). (reason: one line; the game asks for it)

### Score
D18: Base = 0.6 x form + 0.4 x points_per_game. (reason: owner — form covers only 30 days, can be one or two matches after a break)
D19: Score for one player in one gameweek = base x minutes factor x fixture factor x playing chance. (reason: reads as roughly expected points)
D20: Minutes factor = minutes / (90 x matches the player's club has played so far, i.e. its finished fixtures), capped at 1. (reason: owner — gameweeks finished is wrong after a blank or double gameweek)
D21: Fixture factor by the player's own side's difficulty 1..5 = 1.2 / 1.1 / 1.0 / 0.9 / 0.8, held as named constants. (reason: owner — 1.5..0.5 too steep; wants to tune)
D22: Playing chance, next gameweek: chance_of_playing_next_round / 100; if null, 100% when status is "a", otherwise 0. (reason: owner — null with a non-"a" status is not good news)
D23: Playing chance, weeks 2-6: halfway between next week's chance and 100%. Status "u" or "n" = 0 for all six weeks. (reason: owner — injuries usually heal, but the feed gives no length)
D24: Six-week weights 1.0, 0.9, 0.8, 0.7, 0.6, 0.5. (reason: straight drop, easy to check by hand)
D25: No fixture in a gameweek = 0 that week; two fixtures = sum of both fixture scores. (reason: follows the fixtures feed)
D26: Starting eleven, captain and vice-captain use the next-gameweek score. Transfers use the six-week weighted score. (reason: this week vs longer term)
D27: Ties broken by higher total_points, then lower player id. (reason: same input always gives same output)
D28: No early-season special case; README says advice is weak before about gameweek 4. (reason: keep stage 1 small)

### Squad and money
D29: Current squad = last picks plus transfers in entry/{id}/transfers/ whose event is the upcoming gameweek. (reason: fills the gap in D11)
D30: Bank = bank from the last picks, adjusted for those pending transfers. (reason: same gap)
D31: Selling price = purchase price + rise x transfers_sell_on_fee (0.5 today, read from bootstrap-static game_settings), rounded down to a tenth; if the price fell, selling price = now_cost. Purchase price = element_in_cost from transfers; for players held since the start, now_cost - cost_change_start. (reason: real FPL rule; the budget check is wrong without it; fee read from feed for the same reason as D32)
D32: Free transfers: gameweek 1 unlimited; 1 at gameweek 2, +1 each week, cap = 1 + game_settings.max_extra_free_transfers (4 today, so 5), read from bootstrap-static, never hardcoded. Each transfer uses one; extra transfers cost 4 points. Wildcard and Free Hit weeks use none and keep the count. Must give 4 for team 8027067 at gameweek 6. (reason: owner confirmed "as far as I know"; live feed checked 2026-10-06: max_extra_free_transfers = 4, is_next = 6) ASSUMPTION: the rule is unchanged for 2026/27; the gameweek-6 test is the guard.

### Transfers
D33: Suggest 0, 1 or 2 transfers, never more, even with more free transfers. (reason: D1)
D34: A free transfer is suggested only if it gains at least 2 points over six weeks; otherwise "Save it" with next week's free-transfer count. (reason: avoid pointless swaps)
D35: A 4-point hit is suggested only if that transfer gains at least 8 points over six weeks. (reason: "big gain" = earns back twice its cost)
D36: Incoming players must have status "a" and a next-week chance of at least 75%. (reason: never recommend injured players)
D37: Gain = six-week score of player in minus player out, whether or not they would start. Marked in code as a known simplification. (reason: simple)
D38: Pair search: best 50 single transfers, then every pair checked against the shared budget and three-per-club. (reason: fast, good enough)
D39: Tunable numbers (D18 weights, D21, D24, D34, D35, D36 thresholds, D38's 50) are named constants. (reason: owner wants to tune; extends D21)

### Warnings
D40: Warn for any of the 15 with status not "a", or playing chance below 100%, or no fixture next gameweek; show name, chance and the feed's news text. (reason: blanks hurt as much as injuries)

### Downloads
D41: Downloads go to data/raw/YYYY-MM-DD-gwNN/ (NN = upcoming gameweek, two digits), one JSON per endpoint: bootstrap-static.json, fixtures.json, entry.json, picks-gwNN.json (gameweek of the last deadline), history.json, transfers.json. A second run with the same date and gameweek overwrites. (reason: owner — evals look snapshots up by gameweek)
D42: `--from <folder>` builds the brief from a saved folder with no network. (reason: replay for evals and tests)
D43: data/raw/ is git-ignored; one real snapshot is copied into tests/ as frozen input. (reason: small repo, realistic tests)
D44: Requests send a browser-like User-Agent, 30-second timeout, no retries. (reason: owner — bootstrap-static is large; FPL may refuse requests without a User-Agent)

### Failures
D45: Feed unreachable or non-200 (including "The game is being updated"): print "Could not reach FPL (HTTP <code>). Try again later or use --from <folder>", exit 1. No silent fallback to old data. (reason: old data could mislead)
D46: Team not found (404): print "Team <id> not found.", exit 1. (reason: clear message)
D47: No upcoming gameweek: print "No upcoming gameweek.", exit 0. (reason: not an error)
D48: A single missing or null player value counts as 0 and the brief continues. A missing file in --from mode: name the file, exit 1. (reason: one value should not stop the brief; a missing file means broken data)
D49: No transfer worth making: print "No transfer worth making. Save it — you'll have N free next week." (reason: clear advice)

### Output
D50: The brief is built as plain data first, then printed. `--json` prints that data instead of text. (reason: owner — stage 2 gives it to a model, stage 3 scores it)
D51: Text layout as in the sample sent with question 35: header, captain, vice-captain, starting XI with formation and next-GW / 6-GW scores, bench, transfers with gain, hit line, warnings. (reason: agreed)

### Examples
D52: Three hand-made inputs (about 15-20 players) with expected briefs worked out by hand: (a) normal week, no transfer; (b) injured starter, one free transfer and a warning; (c) no free transfers, one gain of 8 or more, hit suggested. Plus one golden-file test on the real snapshot, checked by eye once, then frozen. (reason: exact numbers verifiable by hand, plus real-data coverage)

### Technical
D53: Python 3.13, requests, pytest only. No pandas. No running cost. (reason: D6)
D54: One package fpl/ (download, load, score, advise, print) with tests/ beside it. (reason: fewest files that stay testable)

### Proof
D55: Tests: unit tests for text-to-number, prices, selling price, free transfers (4 at gameweek 6 from the saved history), current squad, each rule, score with weights, valid formation (1 GK, 3-5 DEF, 2-5 MID, 1-3 FWD), captain; the three hand-made examples; the golden file; and a guard that fails any test that tries to go online. (reason: D6 enforced, not promised)
D56: The owner runs `python -m fpl` once against the live feed and checks squad, bank and free transfers against the FPL site. (reason: the one thing tests cannot prove)

### Ownership
D57: Claude writes all of stage 1. The owner reads it and edits. (reason: owner choice)

### Out of scope
D58: No AI, no chip advice, no price-change prediction, no other teams or mini-leagues, no making transfers, no web page or scheduled runs, no reading injury length from news text, no inputs beyond D3/D18. (reason: agreed)
