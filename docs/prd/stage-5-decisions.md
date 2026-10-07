# Stage 5 decisions

Context found before questioning (2026-10-07):

- Stages 1-4 are built (D1-D269). `python -m fpl` downloads the feed,
  prints the brief and a Sonnet-written explanation (`claude -p`, uses
  the owner's plan limits, D202). `python -m fpl.mcp` serves five
  read-only tools to Claude Code.
- Roadmap: stage 5 is "Scheduled brief before each gameweek's
  deadline" (D209, D217). Stage 6 is chips, price changes, rivals and
  outside news. The app never makes transfers.
- Earlier "out of scope" lists that named scheduled runs or a web page:
  D58, D133, D159. Stage 5 lifts the scheduled-runs part.
- The brief today only prints to the terminal. Nothing is saved except
  the raw download (data/raw/, never edited) and eval results.
- An untracked mockup, docs/design/brief-mockup.png, shows the brief as
  a dark web page: pitch with the eleven, captain card, transfers,
  warnings, bench call, the explanation, and eval scores in the footer.
- The PC's clock is South Africa time (UTC+2, no daylight saving). The
  gameweek 6 deadline is 2026-10-10T10:00Z = Sat 12:00 local.
- Windows 11; no scheduler is set up for this repo. Claude Code's
  cloud routines (/schedule) exist but run away from this PC, so they
  cannot see data/raw/ or this-week.json.
- Numbering continues from stage 4, starting at D270.

## Questions one at a time (2026-10-07)

D270: Stage 5 is a React page that shows the weekly brief, not the scheduled brief. Replaces D209/D217's stage 5 in the roadmap; where scheduled runs go now is still open. (reason: owner; full context to follow)
D271: Scheduled runs are dropped from the roadmap entirely, not moved to a later stage. Stage 6 stays as D217 wrote it. docs/roadmap.md is updated to match when this stage is planned. (reason: owner)

## Decisions given up front by the owner (2026-10-07)

D272: D58's "no web page" is reversed for stage 5. The rest of D58 stands. (reason: owner)
D273: docs/roadmap.md is updated: stage 5 is the React page. CONFLICT with D271 (owner said "drop it out"; the pasted context says "moves to a later stage") — open, see question list.
D274: The design is fixed: match docs/design/brief-mockup.png. (reason: owner)
D275: Top to bottom the page shows: a header with team name, gameweek, deadline and three tiles (bank, free transfers, formation); the starting eleven as a pitch with the goalkeeper at the top, the captain chip filled with the accent colour, the vice chip outlined in it, and a doubtful player with a dashed orange outline and his chance of playing; a "Next gameweek" / "Next 6 gameweeks" switch that changes every score on the pitch and bench; the bench in order; side cards for captain (with a "Close call" tag when it is one), suggested transfers marked "Not made yet", warnings and the bench call; the explanation; a footer with the download time and the latest result of each eval. (reason: owner)
D276: Colours: background #0F1714, cards #17221D with border #2A3A32, text #EEF3EE, muted text #A9B8AE, pitch #1F6B45, one accent #D7F24B, warning orange #FFB25C. Fonts: Barlow for text and Barlow Condensed bold for headings and numbers. On a phone-width screen the side cards drop below the pitch. (reason: owner)
D277: React with Vite. Node.js is checked first. Every new term is explained the first time it is used: the owner has not built a React app before. (reason: owner) Checked 2026-10-07: Node.js 22.18.0 and npm 10.9.3 are installed, so nothing needs installing.
D278: Every number comes from the Python code. The page reads a file that `python -m fpl` writes; it never works out a score and never calls the FPL feed. (reason: owner, same idea as D212)
D279: Runs on the owner's PC only. No hosting, no login (D16). (reason: owner)
D280: When the explanation was skipped, its section says so and the rest of the page still shows. (reason: owner)
D281: The components have tests. Nothing calls the live feed or runs claude (CLAUDE.md, D168). (reason: owner)
D282: Questions are sent as one list with recommendations, as in stage 4. (reason: owner)

Found while preparing questions: `--json` holds the brief only. It has no team name (entry.json has it: "Ethans Team"), no explanation, no close calls or bench call, no download time and no eval results. Its scores are unrounded floats (7.882910606743415), prices are in tenths, and warnings carry chance and a `blank` flag. The mockup's numbers come from an older run (bank 0.0m, 4 free transfers); today's snapshot shows 0.8m and 2.

## Question list (2026-10-07): all accepted, owner changed Q1, Q15, Q16, Q22, Q29, Q31

### Roadmap and purpose
D283: The scheduled brief moves to stage 7 on the roadmap. Replaces D271 ("drop it out") and settles D273. (reason: owner)
D284: Only the owner uses the page, in a browser on this PC (as D220). (reason: owner)
D285: The only thing you can do on the page is flip the "Next gameweek" / "Next 6 gameweeks" switch. Nothing is clickable for details. (reason: one way to use it, less to test)
D286: "On a phone" means the layout works when the browser window is phone width. Opening the page on a real phone is out of scope. (reason: no hosting, D279)

### The data file
D287: Every `python -m fpl` run except `--json` writes the data file, including `--from` and `--team`. (reason: `--from` gives an offline page)
D288: The file is web/public/brief.json, overwritten by each run and listed in .gitignore. web/ is the React app's folder at the repo root. Nothing is written to data/raw/. (reason: the page shows the latest brief; older weeks replay from data/raw/; CLAUDE.md, D159)
D289: Python writes every number as ready-to-show text, exactly as the text brief prints it ("7.9", "6.9m", "+14.7", "75%"). The page does no arithmetic and no rounding. Prices stay in tenths inside Python. (reason: D224, D278; reuses the existing formatters)
D290: The file also holds: team name (entry.json `name`); download time (modification time of bootstrap-static.json, D241); the explanation or the reason it was skipped; the captain and bench close calls with their sentences, from explain/parts/close.py (CAPTAIN_CLOSE 1.0, BENCH_CLOSE 0.5); and the three eval lines. (reason: the page invents no wording or thresholds)
D291: The explanation section has three cases: the text; "Explanation skipped: <reason>."; "No explanation for this run." (for `--no-explain`, or `--from` without `--explain`). (reason: D280)
D292: The switch changes only the pitch and bench scores. The captain card always shows next-gameweek scores, and transfers always show the 6-gameweek gain. (reason: those are the numbers the decisions are made on)
D293: Every squad player in the warnings list, on the pitch or the bench, gets a dashed orange outline and "<chance>% to play". A player with no fixture shows "No match". (reason: reuses the warnings rule, D275)
D294: The header note lines ("includes N transfers entered by hand", "this-week.json ... ignored", "Shows your team at the last deadline ...") go in the footer as in the mockup, with Python's exact text. (reason: mockup)
D295: Empty states use Python's existing lines: "No transfer worth making. Save your N free transfers — ..." and "Warnings: none". (reason: same words as the text brief)
D296: The transfers card shows prices ("6.9m → 6.2m"), "+14.7 over 6 GW", and a "−4 hit" or "bench, half gain" tag when they apply. (reason: already in the text brief)
D297: The eval footer has one summary line per eval (scoring, writing, tools) from its newest results file, chosen by get_eval_results' existing logic, e.g. "Writing eval: faithful on 11 of 12". It shows no PASS/FAIL. A missing file reads "no results yet". (reason: owner dropped PASS/FAIL)

### Opening the page
D298: You open the page with `python -m fpl`, then `npm run dev` in web/, then http://localhost:5173. Vite's dev server serves this PC only. A brief.cmd script at the repo root does all three steps. `python -m fpl` itself never opens a browser. (reason: owner added brief.cmd)

### Failures
D299: No data file: "No brief yet. Run python -m fpl." (reason: accepted)
D300: When the file's deadline has passed, a banner says "Gameweek N's deadline has passed. Run python -m fpl." and the rest still shows. Comparing a date with the clock is not scoring. (reason: accepted)
D301: A file that cannot be read or is missing fields shows only "Brief file could not be read. Run python -m fpl again." (reason: accepted)
D302: A failed run writes nothing, so the old file stays and its footer time shows its age. (reason: accepted)

### Technical
D303: TypeScript (JavaScript plus type labels that catch mistakes in the data's shape). The data file's shape is defined once as a type, and a Python test checks the sample file against the same field list. (reason: owner)
D304: Fonts come from the @fontsource/barlow and @fontsource/barlow-condensed npm packages, served locally. The page makes no outside calls. (reason: works offline)
D305: One plain CSS file holds the colours as variables. The pitch is drawn with CSS grid. No Tailwind and no images. (reason: accepted)
D306: Libraries: react, react-dom, vite, @vitejs/plugin-react, the two font packages, typescript; for tests vitest, @testing-library/react and jsdom. Versions are pinned in a committed package-lock.json, and node_modules/ is gitignored. (reason: accepted; typescript added by D303)
D307: The page costs nothing to run. Plan limits are spent only when `python -m fpl` writes the explanation, as today. (reason: accepted)

### Proof
D308: Python tests: the file's content for examples a-c and the snapshot, worked by hand; the three explanation cases; the eval lines from a fake results folder; `--json` writes no file. (reason: accepted)
D309: Page tests (Vitest, Vite's test runner) use one sample file that the Python code makes from the snapshot, committed in tests/data/. A Python test fails if the sample goes stale. The page tests cover: each card; captain and vice chips; a dashed doubtful player; the switch; the three explanation cases; empty transfers and warnings; and the no-file, deadline-passed and broken-file messages. (reason: both sides agree on the file's shape)
D310: The Stop hook also runs `npm test` when web/ has changes. The hook change is tested on Windows before it is relied on, and its timeout stays sensible. (reason: owner)
D311: settings.json allows `npm test` and `npm run` commands, and asks before `npm install`. (reason: owner)
D312: A new rule file .claude/rules/web.md, applying to web/**, holds the page's rules: no calculations, numbers shown as given, colours only from the CSS variables, every component has a test. (reason: owner)
D313: The builder agent is told which test command belongs to which folder. (reason: owner)
D314: The owner opens the page once next to the mockup and once in a narrow window. There are no screenshot tests. (reason: comparing pixels against a picture is brittle, and the mockup's data is old)

### Ownership and boundaries
D315: Claude writes everything; the owner reads and edits. (reason: owner)
D316: Out of scope: hosting or phone access, logins, clicking players for details, a light theme, any calculation in the page, editing this-week.json from the page, the page refreshing itself when the file changes, changes to the MCP server, running evals, stage 6 features. (reason: accepted)

## Follow-ups (2026-10-07): F1-F13 accepted

D317: brief.cmd runs `python -m fpl` as is (explanation included) and passes on its arguments (`%*`), so `brief --no-explain` and `brief --from <folder>` work. (reason: the explanation is part of the page)
D318: If `python -m fpl` fails, brief.cmd shows Python's message and stops without opening the page. (reason: D45, no silent fallback to old data)
D319: brief.cmd starts the server with Vite's `--open --strictPort` on port 5173. If a server is already running, the new one stops with "port in use" and the owner refreshes the open tab. The server runs until its cmd window is closed. (reason: two flags, no wait script; the running server already serves the new file)
D320: The README says to run `npm install` once in web/. brief.cmd never installs anything. (reason: downloading code is the owner's choice)
D321: The data file's path comes from the code's own folder, as session.ROOT does, so a run from any folder writes the repo's web/public/brief.json. (reason: brief.cmd may start from Explorer)
D322: The eval footer quotes each newest results file's own line after a label, with no conversion. Scoring eval: the "shrink vs current: ..." line. Writing eval: the "faithful rate: ..." line. Tools eval: the "path right: ..." line and the "answers passing number and name checks: ..." line. Replaces D297's example "faithful on 11 of 12". (reason: turning 92% into 11 would be a calculation)
D323: The type is web/src/brief.ts: plain `interface` blocks, one field per line, no optional fields (null when there is no value). A Python test reads the field names from it by pattern and checks the sample has exactly those fields at every level, none missing and none extra. (reason: a simple format keeps the pattern reliable; both directions catch a one-sided field)
D324: `npm test` runs `tsc --noEmit` (the TypeScript check, writes nothing) and then `vitest run`. (reason: Vite strips types without checking them)
D325: The Stop hook runs `npm test` in web/ when a changed file is under web/, and pytest when a .py file changed, as today. Builders (`--always`) run both. (reason: D310)
D326: The hook timeout goes from 120 to 240 seconds. Both runs are timed on Windows in the hook step and the times written down; if they total more than 120 s, the owner is asked. (reason: D310, a sensible timeout)
D327: A builder runs `npm ci` (installs exactly what package-lock.json lists) in its worktree's web/ before testing. settings.json allows `npm ci`; `npm install` stays "ask". (reason: a worktree has no node_modules, and a builder cannot answer a permission question)
D328: The builder agent's text stops saying "Python project" and names both test commands: `python -m pytest -q` at the repo root, and `npm ci` then `npm test` in web/. (reason: D313)
D329: One sample file, tests/data/brief-sample.json, is made from the snapshot with `--from`, so its explanation case is "No explanation for this run." The page tests make the other two cases by changing that field. (reason: the sample never needs claude)

## Examples (2026-10-07): E1-E6 accepted

Found: the mockup was drawn from tests/data/snapshot; `--from tests/data/snapshot --no-explain` gives exactly its numbers.

D330: Example 1, tests/data/snapshot: the page shows the mockup's text and numbers exactly. Header: Ethans Team, "Gameweek 6", "Deadline Sat 10 Oct 12:00", tiles 0.0m / 4 / 3-4-3. Captain card: Groß 7.9, vice Tarkowski 7.2, with the "Close call" tag. Transfers: Szoboszlai → Schade (6.9m → 6.2m, +14.7) and O'Shea → Davis (4.0m → 4.0m, +11.4). João Pedro is dashed with "75% to play". Explanation: "No explanation for this run." (reason: owner; D314's visual check compares against the mockup directly)
D331: Example 2, example_a: the transfers card reads "No transfer worth making. Save your 3 free transfers — you'll have 4 free next week." and warnings read "Warnings: none". (reason: owner)
D332: Example 3, example_b: Hart is dashed with "25% to play". The bench call is not close (Orr 3.8, Gale 3.0, gap 0.8). (reason: owner)
D333: Example 4, example_c: bank 0.5m and 0 free transfers. The footer note reads "includes 1 transfer entered by hand". Lowe → Yates gets the "−4 hit" tag. The bench call is level (Fry 4.1, Kemp 4.1). (reason: owner)
D334: Python writes the card sentences for the page, with numbers from close.calls(). Captain, close: "Gap of 0.7 for next gameweek. Anything at 1.0 or under counts as close." Captain, not close: "Gap of 1.4 for next gameweek. Over 1.0, so not close." Bench, close: "Calvert-Lewin starts at 2.9. Diop is the best outfield player on the bench at 2.6. Calvert-Lewin is 0.3 ahead, which is close." Bench, not close: "... is 0.8 ahead, which is not close." Bench, level: "... They are level, which is close." Bench player ahead: "... Kemp is 0.2 ahead, which is close." Only the captain card gets a tag. The model's close-call lines (close.py _line) are unchanged. (reason: mockup wording; the page invents no text)
D335: Each hit transfer gets a "−4 hit" tag, and Python's "Hit: -4 points" total line sits under the transfers list. (reason: the total line shows −8 when there are two hits)
D336: The "Not made yet" tag is hidden when no transfer is suggested. (reason: nothing to make)
D337: The team name (entry.json `name`, as is) is the small line above "Gameweek N". (reason: mockup)
D338: The deadline and download time use Python's existing formats, "Sat 10 Oct 12:00" and "Data downloaded Wed 7 Oct 12:55", in the PC's local time. (reason: same as the text brief and the MCP server)
D339: The sample file is made with the download time fixed to D119's constant (2026-10-06 12:55 UTC), and the staleness test uses the same constant. Page tests set a fake clock before the deadline; one test sets it after the deadline to check D300's banner. (reason: copies lose file times, and the real clock passes the sample's deadline on 10 Oct)

## After stage 5 (2026-10-07)

D340: Both hook timeouts go from 240 to 360 seconds. Timed on Windows on 2026-10-07: pytest 217 s (386 tests), npm test 26 s, 243 s together, so a builder's SubagentStop hook, which runs both, passed D326's 240 s limit. The times are written at the top of run_tests.py. Speeding up the tests comes next. (reason: owner; D326 said to ask the owner past 120 s, which was missed)
D341: The tests are faster, with the same 386 results: transfers.build caches each selling price in its memo, so manual.swaps (this-week.json's names matched against every player) runs about 15 times a brief instead of 3,951; the names check compiles each name's pattern once (functools.cache). tests/test_cli.py::test_this_week_file_used_and_bad_name went from 24 s to 3 s, unchanged. Full run on Windows, 2026-10-07: pytest 199 s -> 153 s; npm test 18 s; 171 s together. Both hook timeouts go to 510 s (about three times that), held as LIMIT in run_tests.py, and a test checks the two match. A run past 80% of LIMIT (WARN_SHARE) prints a warning: in the blocking message when tests fail, as a systemMessage when they pass. (reason: owner; D340 left no room, and the limit had already been outgrown once without anyone noticing)
