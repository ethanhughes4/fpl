# Stage 5 plan

Built from docs/prd/stage-5-decisions.md (D270-D339). Stages 1-4 are built:
`brief.build(feed)` gives the brief's data, `explain.explain(...)` the explanation lines,
`get_eval_results.text(kind)` the newest results file, all with no network.

Stage 5 is a web page that shows the weekly brief (D270, D272). `python -m fpl` writes one
data file; the page only reads it and shows it (D278, D289).

New terms, the first time they appear (D277):
- **React**: a library for building a page out of small pieces called **components**. A
  component is a function that takes data and returns what the page shows (`.tsx` file).
- **TypeScript**: JavaScript plus type labels; `tsc` checks the labels and catches a
  mismatch with the data's shape before the page runs (D303).
- **Vite**: the tool that serves the page on this PC while you work (`npm run dev`) (D277).
- **npm**: Node.js's package manager. `package.json` lists the libraries;
  `package-lock.json` pins their exact versions; `npm ci` installs exactly those;
  `node_modules/` is where they land (D306, D327).
- **Vitest**: Vite's test runner. **Testing Library** renders a component in a test and
  finds text on it; **jsdom** is a fake browser for those tests (D306).
- **Error boundary**: a React component that catches any crash while drawing the page and
  shows a fallback message instead.

## Skeleton (made in step 1)

Python:
- `fpl/page/__init__.py`:
  - `PATH = Path(__file__).parents[2] / "web" / "public" / "brief.json"` (repo root as
    `session.ROOT` does, D321).
  - `PARTS = [header]`: modules in `fpl/page/parts/`, each with
    `build(run) -> dict` of ready-to-show text (D289). `run` is one dict:
    `data` (brief.build), `feed`, `downloaded` (datetime), `explanation` (the lines
    `explain.explain` returned, or None when it did not run).
  - `build(data, feed, downloaded, explanation) -> dict` = `{module name: part.build(run)}`.
  - `write(...)`: `build` then write PATH (UTF-8, indent 2), making `web/public/` if needed.
  - **To switch a part on: add its file, add one line to `PARTS`.**
- `fpl/__main__.py` (changed once, in step 1): after `brief.build`, unless `--json`
  (D287): explanation lines are worked out (or None), printed as today, then
  `page.write(data, feed, downloaded, lines)`. `downloaded` = mtime of the folder's
  `bootstrap-static.json` (D290, D241). The write is last, so any failure writes
  nothing (D302).
- Numbers: Python formats with the existing formatters (`money.price`, `:.1f`, `:+.1f`)
  so the page shows exactly what the text brief prints (D289). Prices stay in tenths until
  printed. No Python part downloads anything.
- `tests/make_sample.py`: `python -m tests.make_sample` writes
  `tests/data/brief-sample.json` from `tests/data/snapshot` as a `--from` run makes it
  (no explanation, D329), with `downloaded` = D119's `SNAPSHOT_TIME` from
  `tests/test_rebuild.py` (D339).
- `tests/conftest.py`: an autouse fixture points `page.PATH` at a tmp file, so no test
  touches the real `web/public/brief.json`.

Page (`web/`, D288):
- Vite + React + TypeScript app. `npm test` = `tsc --noEmit && vitest run` (D324).
  `npm run dev` serves http://localhost:5173 on this PC only (D298).
- `web/src/brief.ts`: the data's shape, plain `interface` blocks, one field per line,
  no optional fields, `null` where there is no value (D323). The top interface `Brief`
  has one line per Python part.
- `web/src/App.tsx`: fetches `/brief.json`. No file → "No brief yet. Run python -m fpl."
  (D299). Bad JSON, a missing top-level part, or any crash while drawing (caught by an
  error boundary) → only "Brief file could not be read. Run python -m fpl again." (D301).
  Otherwise draws `PARTS`: one list of `[slot, Component]`, slot = `top`, `main`,
  `side` or `bottom`. **To switch a component on: add its file, add one line to `PARTS`.**
- `web/src/theme.css`: the only place colours are written, as CSS variables (D276, D305);
  fonts from `@fontsource/barlow` and `@fontsource/barlow-condensed` (D304); page grid:
  `main` and `side` side by side, `side` drops below `main` at phone width (D276, D286).
  Each component has its own `.css` that uses only those variables (D312).
- Each component lives in `web/src/parts/<Name>.tsx` with `<Name>.css` and
  `<Name>.test.tsx`. Tests load `tests/data/brief-sample.json` and set a fake clock before
  the sample's deadline (D309, D339).

Field check (D323): `tests/test_page_shape.py` reads the interface blocks of `brief.ts` by
pattern and checks the sample has exactly those fields at every level (arrays and nested
interfaces followed), none missing, none extra. `tests/test_page_sample.py` fails when the
sample differs from what `tests/make_sample.py` would write, and says to run it (D309).

**Shared spots in a wave.** Each part step touches four shared spots: one line in Python
`PARTS`, one line in page `PARTS`, its interface block plus one line in `brief.ts`, and the
generated sample. When merging, keep every side's lines and rerun
`python -m tests.make_sample`. Everything else a step makes is its own file.

## Waves

| Wave | Steps | Notes |
|------|-------|-------|
| 1 | 1 | skeleton, tooling, roadmap; built in the main session (changes settings, builder text, conftest) |
| 2 | 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 | parts share only the spots above; step 11 shares nothing, main session (owner may be asked, D326) |
| 3 | 12 | brief.cmd and the owner's look; needs every part |

---

## Step 1: Open the page and see the team name, gameweek and deadline — Wave 1 — DONE

Depends on: none.

After it the user can run `python -m fpl --from tests/data/snapshot --no-explain`, then
`npm install` once and `npm run dev` in `web/`, open http://localhost:5173 and see a dark
page with "Ethans Team", "Gameweek 6", "Deadline Sat 10 Oct 12:00" in Barlow on #0F1714.
Deleting `web/public/brief.json` shows "No brief yet. Run python -m fpl."; breaking it
shows the could-not-read message. `python -m fpl --json` writes no file.

Creates:
- `fpl/page/__init__.py`, `fpl/page/parts/__init__.py`, `fpl/page/parts/header.py`:
  `{"team": entry name as is, "gameweek": "Gameweek 6", "deadline": "Deadline Sat 10 Oct 12:00"}`
  (D337, D338; same local-time format as `sections/header.py`).
- `web/package.json`, `web/package-lock.json`, `web/vite.config.ts` (Vitest, jsdom),
  `web/tsconfig.json`, `web/index.html`, `web/src/main.tsx`, `web/src/App.tsx`,
  `web/src/App.test.tsx`, `web/src/brief.ts`, `web/src/theme.css`,
  `web/src/parts/Header.tsx`, `Header.css`, `Header.test.tsx`, `web/src/test-setup.ts`
  (fake clock). Libraries exactly as D306, versions pinned.
- `tests/make_sample.py`, `tests/data/brief-sample.json`, `tests/test_page.py`,
  `tests/test_page_shape.py`, `tests/test_page_sample.py`.
- `.claude/rules/web.md` (applies to `web/**`): no calculations, numbers shown as given,
  colours only from the CSS variables, every component has a test (D312).

Changes:
- `fpl/__main__.py`: as in the skeleton.
- `tests/conftest.py`: the `page.PATH` fixture.
- `.gitignore`: `web/public/brief.json`, `web/node_modules/`, `web/dist/` (D288, D306).
- `.claude/settings.json`: allow `npm test *`, `npm run *`, `npm ci`; ask `npm install *`
  (D311, D327).
- `.claude/agents/builder.md`: no longer "a Python project"; names both test commands:
  `python -m pytest -q` at the repo root, and `npm ci` then `npm test` in `web/` (D313, D328).
- `docs/roadmap.md`: stage 5 = the React page; scheduled brief = stage 7; stage 6 as is
  (D270, D271, D273, D283).
- `README.md`: "The page" section: `npm install` once in `web/` (D320), how to open it,
  the terms above in one line each; costs nothing to run (D307).

Tests:
- Python (`tests/test_page.py`): header for examples a-c and the snapshot, worked by hand
  (D308); `--from` and `--team` (fake download) write the file, `--json` does not (D287);
  a failing run (missing file, ManualError) leaves the old file unchanged (D302); the
  path is the repo's whatever the working folder (D321).
- Field check and sample staleness as in the skeleton.
- Page: Header shows the three lines from the sample; App: no file, bad JSON, missing
  part, and a component that throws → the right message (D299, D301).

Covers: D270, D271, D272, D273, D274, D276, D277, D278, D279, D283, D284, D286, D287,
D288, D289, D298, D299, D301, D302, D303, D304, D305, D306, D307, D311, D312, D313, D315,
D320, D321, D323, D324, D327, D328, D329, D337, D338, D339.

---

## Step 2: Bank, free transfers and formation tiles — Wave 2 — TODO

Depends on: 1.

After it the user sees three tiles beside the gameweek: Bank "0.0m", Free transfers "4",
Formation "3-4-3" (snapshot).

Creates: `fpl/page/parts/tiles.py` (`bank`, `free_transfers`, `formation` as text),
`web/src/parts/Tiles.tsx`, `Tiles.css`, `Tiles.test.tsx`, `tests/test_page_tiles.py`.
Changes: the shared spots (slot `top`).

Tests: Python: snapshot 0.0m / 4 / 3-4-3; example_c 0.5m / 0 (D333); a and b by hand.
Page: the three tiles show the sample's text.

Covers: D275, D289, D330, D333.

---

## Step 3: The pitch, the bench and the next-gameweek / 6-gameweek switch — Wave 2 — TODO

Depends on: 1.

After it the user sees the eleven on a green pitch, goalkeeper row at the top, then
defenders, midfielders, forwards; Groß's chip filled with the accent and "CAPTAIN",
Tarkowski's outlined with "VICE"; João Pedro dashed orange with "75% to play"; the bench
in order (GK, 1st, 2nd, 3rd). Flipping the switch to "Next 6 gameweeks" changes every
score on the pitch and bench, and nothing else (D292). It is the only thing on the page
that reacts to a click (D285).

Creates: `fpl/page/parts/pitch.py`: `rows` (list of rows, goalkeeper first, each player
`name`, `next`, `six` as "7.9"-style text, `role` "CAPTAIN" / "VICE" / null, `doubt`
"75% to play" / "No match" / null), `bench` (same fields plus `label` "GK", "1st", ...).
`doubt` comes from the warnings section: every squad player in it is marked; a blank
player reads "No match" (D293). `web/src/parts/Pitch.tsx`, `Pitch.css`,
`Pitch.test.tsx`, `tests/test_page_pitch.py`.
Changes: the shared spots (slot `main`).

Tests: Python: snapshot rows and roles; example_b Hart "25% to play" (D332); a blank
player → "No match"; a-c by hand. Page: captain and vice chips, the dashed doubtful
player, the switch changes pitch and bench scores and the captain card's text is untouched
(when present).

Covers: D275, D285, D289, D292, D293, D330, D332.

---

## Step 4: Captain card with "Close call" — Wave 2 — TODO

Depends on: 1.

After it the user sees the Captain card: Groß 7.9, Vice: Tarkowski 7.2, a "Close call"
tag, and "Gap of 0.7 for next gameweek. Anything at 1.0 or under counts as close."

Creates: `fpl/page/parts/captain.py`: names and next-GW scores, `close` (bool), `sentence`,
both from `close.calls()` and `CAPTAIN_CLOSE` (D290, D334): close → "Gap of X for next
gameweek. Anything at 1.0 or under counts as close."; not close → "Gap of X for next
gameweek. Over 1.0, so not close." `web/src/parts/Captain.tsx`, `Captain.css`,
`Captain.test.tsx`, `tests/test_page_captain.py`.
Changes: the shared spots (slot `side`).

Tests: Python: snapshot close sentence; a not-close example (from a-c, or a changed
score); close.py `_line` output unchanged. Page: the card, tag shown when close, hidden
when not (sample changed in the test).

Covers: D275, D290, D292, D330, D334.

---

## Step 5: Suggested transfers card — Wave 2 — TODO

Depends on: 1.

After it the user sees "Suggested transfers" with "Not made yet", then
Szoboszlai → Schade, "6.9m → 6.2m", "+14.7 over 6 GW", and O'Shea → Davis. A hit
transfer has a "−4 hit" tag and Python's "Hit: -4 points" line under the list; a bench
transfer has "bench, half gain". With none suggested it shows only Python's
"No transfer worth making. Save your ..." line and no "Not made yet" tag.

Creates: `fpl/page/parts/transfers.py` (`rows` with `out`, `in`, `prices`, `gain`,
`tags`; `hit_line` or null; `empty` line or null, from `sections/transfers.render`'s
words), `web/src/parts/Transfers.tsx`, `Transfers.css`, `Transfers.test.tsx`,
`tests/test_page_transfers.py`.
Changes: the shared spots (slot `side`).

Tests: Python: snapshot two rows; example_a empty line (D331); example_c Lowe → Yates
with "−4 hit" and the hit line (D333); two hits → "Hit: -8 points" (D335). Page: rows,
tags, empty state with the tag hidden (D336).

Covers: D275, D289, D292, D295, D296, D330, D331, D333, D335, D336.

---

## Step 6: Warnings card — Wave 2 — TODO

Depends on: 1.

After it the user sees "Warnings": João Pedro, "75%", "Knee injury - 75% chance of
playing"; with none, "Warnings: none".

Creates: `fpl/page/parts/warnings.py` (rows `name`, `chance` "75%", `news` with the text
brief's "no fixture next gameweek" fallback; `empty` line or null),
`web/src/parts/Warnings.tsx`, `Warnings.css`, `Warnings.test.tsx`,
`tests/test_page_warnings.py`.
Changes: the shared spots (slot `side`).

Tests: Python: snapshot row; example_a "Warnings: none" (D331); example_b Hart 25%;
a blank player's news. Page: rows and the empty state.

Covers: D275, D293, D295, D330, D331, D332.

---

## Step 7: Bench call card — Wave 2 — TODO

Depends on: 1.

After it the user sees "Bench call": "Calvert-Lewin starts at 2.9. Diop is the best
outfield player on the bench at 2.6. Calvert-Lewin is 0.3 ahead, which is close."

Creates: `fpl/page/parts/bench_call.py`: one `sentence` from `close.calls()` bench entry
and `BENCH_CLOSE`, in D334's four forms (ahead close, ahead not close, level, bench player
ahead); null when there is no bench call. No tag (D334). `web/src/parts/BenchCall.tsx`,
`BenchCall.css`, `BenchCall.test.tsx`, `tests/test_page_bench_call.py`.
Changes: the shared spots (slot `side`).

Tests: Python: snapshot (0.3, close); example_b Orr 3.8 / Gale 3.0, "0.8 ahead, which is
not close" (D332); example_c Fry / Kemp level (D333); a bench player ahead (changed
score). Page: the sentence shows.

Covers: D275, D290, D330, D332, D333, D334.

---

## Step 8: Explanation section — Wave 2 — TODO

Depends on: 1.

After it the user sees the Explanation section with the model's text after a live run;
"Explanation skipped: <reason>." when it was skipped; "No explanation for this run." for
`--no-explain` or `--from` without `--explain`. The rest of the page shows in all three.

Creates: `fpl/page/parts/explanation.py`: `{"text": ..., "message": ...}`, one of them null,
from `run["explanation"]` (D291), `web/src/parts/Explanation.tsx`, `Explanation.css`,
`Explanation.test.tsx`, `tests/test_page_explanation.py`.
Changes: the shared spots (slot `bottom`).

Tests: Python: the three cases, the explained one with `tests.fakeclaude` through `main`
(no real claude, D281). Page: the sample's message, plus text and skipped made by
changing that field (D329), the other cards still present (D280).

Covers: D280, D281, D290, D291, D307, D329, D330.

---

## Step 9: Footer: download time, notes and eval lines — Wave 2 — TODO

Depends on: 1.

After it the user sees in the footer "Data downloaded Tue 6 Oct 14:55"-style time, the
header notes ("Shows your team at the last deadline. ..." or "includes 1 transfer entered
by hand" or the "this-week.json ... ignored" line), and one line per eval:
"Scoring eval: shrink vs current: ...", "Writing eval: faithful rate: ...",
"Tools eval: path right: ...", "Tools eval: answers passing number and name checks: ..."
quoted from each newest results file; "no results yet" when there is none.

Creates: `fpl/page/parts/footer.py`: `downloaded` (D338 format), `notes` (the
`sections/header.render` lines after the first, plus that first line's parts after the
deadline; Python's exact text, D294), `evals` (label + the quoted line, using
`get_eval_results.text(kind)`, no changes to the MCP server, D316, D322).
`web/src/parts/Footer.tsx`, `Footer.css`, `Footer.test.tsx`, `tests/test_page_footer.py`.
Changes: the shared spots (slot `bottom`).

Tests: Python: eval lines from a fake results folder (monkeypatched `RESULTS`), a
missing kind → "no results yet" (D308); notes for snapshot (no file), example_c
("includes 1 transfer entered by hand", D333), an ignored this-week.json; download time
from a set mtime. Page: the footer lines, no PASS/FAIL.

Covers: D290, D294, D297, D308, D316, D322, D330, D333, D338.

---

## Step 10: "Deadline has passed" banner — Wave 2 — TODO

Depends on: 1.

After it a page left open past the deadline shows "Gameweek 6's deadline has passed. Run
python -m fpl." above the rest, which still shows.

Creates: `fpl/page/parts/deadline.py` (`utc`: the feed's deadline_time as given,
`passed`: the banner text), `web/src/parts/Deadline.tsx`, `Deadline.css`,
`Deadline.test.tsx`, `tests/test_page_deadline.py`.
Changes: the shared spots (slot `top`, first).

Tests: Python: snapshot text and time. Page: fake clock before the deadline → no banner;
after → banner and the header still shown (D300, D339).

Covers: D300, D339.

---

## Step 11: Stop hook runs the page tests — Wave 2 — TODO

Depends on: 1. Built in the main session (the owner may need to answer, D326).

After it, ending a session with a changed file under `web/` runs `npm test` in `web/`;
a changed `.py` file runs pytest as today; builders (`--always`) run both. A failure
blocks as today.

Changes: `.claude/hooks/run_tests.py`: a function `commands(changed_paths, always)` picks
pytest, npm test, or both (D325); npm is called so it works on Windows (`npm.cmd`);
`.claude/settings.json`: both hook timeouts 120 → 240 s (D326).
Creates: `tests/test_hook.py` (`commands` only; it runs nothing).

Check on Windows (D310, D326): run the hook by hand with a web change and with
`--always`; time pytest and npm test; write both times in a comment at the top of
`run_tests.py`. If they total more than 120 s, ask the owner before going on.

Tests: web-only change → npm only; .py only → pytest only; both; neither → nothing;
`--always` → both.

Covers: D310, D325, D326.

---

## Step 12: `brief` opens the page in one go — Wave 3 — TODO

Depends on: 2-10.

After it the user can type `brief` (or `brief --no-explain`, `brief --from <folder>`) at
the repo root or double-click brief.cmd: it runs `python -m fpl` with the arguments, and
on success starts `npm run dev -- --open --strictPort --port 5173` in `web/`, which opens
the browser. If Python fails, its message stays on screen and no page opens. A second
`brief` while a server runs stops with "port in use"; refreshing the open tab shows the
new file. It never installs anything.

Creates: `brief.cmd` (repo root; works from any folder, D321), `tests/test_brief_cmd.py`
(Windows only: a broken `--from` folder → non-zero exit, Python's message, npm never
started).
Changes: `README.md`: `brief` replaces the three steps, `npm install` once first.

Owner's look (D314): open the page from `brief --from tests/data/snapshot --no-explain`
next to `docs/design/brief-mockup.png`, check the text and numbers match D330 (the
mockup's explanation and footer are the only differences: D322, D329); then narrow the
window to phone width and check the side cards drop below the pitch.

Covers: D274, D298, D314, D317, D318, D319, D320, D330.

---

## Plan choices to check at approval

1. Steps in wave 2 share four spots, not one list: the two `PARTS` lists, the `Brief`
   interface (plus each step's own interface block, all in `brief.ts` as D323 says), and
   the generated sample. Merging keeps both sides and reruns `python -m tests.make_sample`.
   The other way is one interface file per part, which breaks D323's "the type is
   brief.ts".
2. Step 1 and step 11 are built in the main session, not by builders: step 1 changes
   the builder's own text, settings and conftest; step 11 may need the owner (D326).
   After step 1, reload Claude Code so the new npm permissions apply to builders.
3. A crash anywhere while drawing shows the D301 message (error boundary), instead of
   checking every field when loading. The Python field test (D323) keeps the shape right.
4. Python writes the pitch as rows (goalkeeper first) and the bench labels ("GK", "1st",
   ...), so the page does no grouping or counting.
5. The banner text and deadline time come from Python (step 10); the page only compares
   the time with the clock (D300).
6. brief.cmd is tested only for the failure path; the success path opens a browser and
   is the owner's look in step 12.

## UNCOVERED

- D282 (questions sent as one list): how questions were asked, nothing to build.

All other decisions D270-D339 appear in at least one step.
