# Stage 3 plan

Built from docs/prd/stage-3-decisions.md (D124-D185). Stages 1 and 2 are
built: `brief.build(feed)` gives the brief's data and `brief.render(data)`
the printed lines, both with no network.

## Skeleton (made in step 1)

- `fpl/claude.py` is the one file that runs Claude Code (D165, D173):
  `ask(prompt, system, model, timeout) -> (text, tokens, model_id)`,
  raising `AskError(reason)`. It is complete after step 1; later steps
  never edit it. Everything else takes `ask` as an argument, so tests
  pass a fake.
- `fpl/explain/` holds the explanation. Two shared lists, in two files:
  - `fpl/explain/block.py`: `PARTS = [brief]` — modules in
    `fpl/explain/parts/`, each with `lines(data, feed) -> [str]`. The
    model's input block (D138) is the parts' lines joined, in order.
    It is plain text with every number already printed as the brief
    prints it (1 decimal, prices as `6.9m`), so D143 compares like
    with like.
  - `fpl/explain/check.py`: `CHECKS = [numbers]` — modules in
    `fpl/explain/checks/`, each with `NAME`, `LIVE` (True = runs on
    every live explanation, D146; False = eval only, D151) and
    `check(text, ctx) -> None or reason`. `ctx` holds `data` (brief),
    `feed` and `block`. The reason fills
    `Explanation skipped: <reason>.`
  To switch a slice on: add its file, add one line to one of these lists.
- `fpl/eval/writing/` (made in step 4) has the third list:
  `fpl/eval/writing/run.py`: `SCORERS = [checks]` — each with `start(ctx)
  -> [notice lines]`, `score(text, ctx) -> {column: value}` and
  `summary(rows) -> [(label, value, passed)]`.
- Prompts are plain text files the owner edits (D185):
  `fpl/explain/writer.txt` (step 1) and `fpl/eval/writing/judge.txt`
  (step 7).
- `tests/fakeclaude.py` (step 1) fakes `subprocess.run` for `fpl.claude`;
  later steps do not edit it. `tests/conftest.py` gets one autouse guard
  in step 1 so a test that forgets the fake can never run claude (D168,
  D178); later steps do not edit it.
- Steps never edit this plan. Tuning numbers (150 words, 1.0 / 0.5 / 2.0,
  60 s / 180 s / 10 s, 3 runs, 40 calls, models) are named constants at
  the top of their file.

## Waves

| Wave | Steps | Notes |
|------|-------|-------|
| 1 | 1 | skeleton, end to end |
| 2 | 2, 3, 4 | share only `PARTS` (2) and `CHECKS` (3); 4 adds new files |
| 3 | 5, 6 | share only `PARTS` (5) and `CHECKS` (6) |
| 4 | 7 | judge and judge check; one line in `SCORERS` |

---

## Step 1: Brief, then an explanation from Claude Code — Wave 1 — TODO

Depends on: none.

After it the user can run `python -m fpl` and see the brief, then a line
`Explanation`, then a short plain-text explanation written by `haiku`
from the brief. `--no-explain` turns it off; `--from <folder>` does not
call the model unless `--explain` is given; the last of the two flags
wins; `--json` prints exactly what it does today and never calls the
model. If claude is missing, not logged in, fails or times out, or the
text quotes a number not in the brief, the brief is still printed with
one `Explanation skipped: ...` line, exit 0.

Creates:
- `fpl/claude.py` (D162-D173, D176, D177):
  - `shutil.which("claude")`; None → `AskError("Claude Code is not
    installed or not logged in")`.
  - In a new `TemporaryDirectory(ignore_cleanup_errors=True)`: write the
    system prompt to a file there, run the D169 command as a list (no
    `shell=True`) with that folder as `cwd`, prompt on stdin, UTF-8 in
    and out, `timeout`.
  - Timeout → `the model call failed (timed out after <N> s)`. JSON
    that cannot be read → `the model call failed (unreadable output)`.
    Non-zero exit, `is_error` true or `subtype` not `success` → run
    `claude auth status` (`AUTH_TIMEOUT = 10`); exit 1 there → the
    not-installed reason, else `the model call failed (<first line of
    result>)`.
  - Tokens = `usage.input_tokens + usage.output_tokens`, None when
    `usage` is missing; model id = the `modelUsage` key (D170).
    `total_cost_usd` is never read (D166).
- `fpl/explain/__init__.py`: `WRITER_MODEL = "haiku"` (D174),
  `WRITER_TIMEOUT = 60` (D176), `MAX_WORDS = 150` (D136);
  `explain(data, feed, ask) -> [lines]`: builds the block, calls `ask`
  with `writer.txt` as system prompt, runs the `LIVE` checks; returns
  `["Explanation", text]` or `["Explanation skipped: <reason>."]`
  (D134, D146, D147). No retry.
- `fpl/explain/block.py` with `PARTS = [brief]`; `fpl/explain/parts/brief.py`:
  the rendered brief lines (captain, eleven, transfers, warnings with
  chance and news text, D142).
- `fpl/explain/check.py` with `CHECKS = [numbers]`;
  `fpl/explain/checks/numbers.py` (D143, `LIVE = True`): every number in
  digits in the text must be one of the numbers in the block; signs and
  a trailing `m` ignored. Reason: `it quoted 7.4, which is not in the
  brief`.
- `fpl/explain/writer.txt`: first draft (D185): plain English, no
  markdown, at most `{max_words}` words (filled from `MAX_WORDS`), why
  this captain, each close call, what each warning means for the team
  (e.g. already on the bench), every number in digits (D145), never
  change a number, never name anyone not in the block, never guess how
  long an injury lasts (D142).
- `tests/fakeclaude.py`: a fake `subprocess.run` that records the call
  and returns a chosen JSON, exit code, timeout or garbage; also fakes
  `claude auth status`.

Changes:
- `fpl/__main__.py`: `--explain` / `--no-explain` (same `dest`, default
  None, so the last wins, D137); explain when the flag says so, else
  when not `--from` (D131, D132); never with `--json` (D135). Prints the
  brief first, then the explanation lines; exit code unchanged (D134).
- `tests/conftest.py`: autouse guard making `fpl.claude` find no claude
  unless a test installs the fake (D168).
- `CLAUDE.md`: boundary line "Tests must never run claude." (D178).
- `README.md`: the explanation, `--explain` / `--no-explain`, that it
  uses the owner's Claude Code login and plan limits (D177), no key.

Tests:
- `tests/test_claude.py`: the exact argument list of D169 with no
  `shell=True`; `cwd` is a temp folder that is empty apart from the
  system prompt file; prompt on stdin; an accented name survives UTF-8
  both ways; tokens and model id read from a real-shaped JSON (D170);
  tokens None without `usage`; no claude; non-zero exit with auth
  status 1 → not installed; with auth status 0 → first line of result;
  `is_error` true; `subtype` not success; timeout; unreadable JSON.
- `tests/test_check_numbers.py`: hand-written good and bad texts:
  `4-point hit` matches `-4`, `6.9m` matches `6.9`, `7.4` not in block
  fails with that reason.
- `tests/test_explain_cli.py` (D160), each through `main()` with the fake:
  success (brief, `Explanation`, text); Claude Code missing; call failed;
  timeout; checker failure (text quotes `7.4`); `--from` makes no call;
  `--from --explain` calls; `--no-explain` makes no call; `--explain
  --no-explain` and the reverse; `--json` output equal to today's and
  no call. All exit 0.

Decisions: D124, D125, D127 (void: no key, no .env), D128, D129 (answered
by D174, D180), D130, D131, D132, D133 (no scheduling added), D134, D135,
D136, D137, D138 (block, brief part), D142, D143, D145 (prompt asks for
digits), D146, D147, D148, D159 (no tools, no chat, no streaming,
nothing saved to data/raw/), D160 (CLI paths), D162, D163, D164, D165,
D166, D168, D169, D170, D171, D172, D173, D174 (writer), D176 (writer),
D161 (replaced by D185), D177, D178, D185 (writer draft).

Owner check (D160): run `python -m fpl` once for real.

## Step 2: Close calls in the block — Wave 2 — TODO

Depends on: 1.

After it the explanation is given the close calls and talks about them:
`python -m fpl --from tests/data/example_b --explain` explains that
Marsh 7.3 vs Innes 7.2 is a 0.1 call.

Creates: `fpl/explain/parts/close.py` (D139, D140, D181):
- `CAPTAIN_CLOSE = 1.0`, `BENCH_CLOSE = 0.5`, `TRANSFER_CLOSE = 2.0`,
  bars from `transfers.MIN_FREE_GAIN` / `MIN_HIT_GAIN`.
- `calls(data) -> [call]`: captain vs vice gap; lowest outfield starter
  vs best outfield bench player gap; per suggested transfer, printed gain
  minus its bar. Every gap is worked from the numbers rounded to 1
  decimal first. Each call has its players' names, the numbers, the
  gap or margin, and `close` true/false.
- `lines(data, feed)`: a `Close calls` section listing every call and
  whether it is close.

Changes: `fpl/explain/block.py` (one line in `PARTS`).

Tests: `tests/test_explain_close.py`, worked by hand:
- A: Hart 7.9 vs Marsh 7.3, gap 0.6, close; Fry or Kemp 4.1 vs Orr 3.8,
  gap 0.3, close; no transfer (D156, D184).
- B: Marsh 7.3 vs Innes 7.2, gap 0.1, close; Hart -> Wren +13.4 against
  2, margin 11.4, not close (D157).
- C: Hart vs Marsh 0.6, close; Kemp 4.1 vs Fry 4.1, gap 0.0, close;
  Lowe -> Yates +10.8 against 8, margin 2.8, not close (D158, D184).
- rounding: 7.34 vs 7.15 prints 7.3 vs 7.2, gap 0.1 (D140).

Decisions: D138 (close calls), D139, D140, D155 (close calls), D156,
D157, D158, D181, D184.

## Step 3: Names check — Wave 2 — TODO

Depends on: 1.

After it an explanation that names a player or club from the feed who
is not in the brief is not printed: `Explanation skipped: it named
Salah, who is not in the brief.`

Creates: `fpl/explain/checks/names.py` (D144, `LIVE = True`): all player
names (`web_name`, first and last name) and club names (`name`,
`short_name`) from the feed; matching ignores case and accents
(`unicodedata`); names that appear in the block are removed from the
text first, so "João Pedro" does not trip on another "Pedro"; whole
words only.

Changes: `fpl/explain/check.py` (one line in `CHECKS`); `README.md`
(known gaps D145, D183: unknown names, numbers in words, a real number
on the wrong player — the judge is the backstop).

Tests: `tests/test_check_names.py`: allowed name passes; feed name not in
the block fails with the reason; `JOAO PEDRO` vs `João Pedro`; the
"Pedro" case; club name; a name not in the feed at all passes (known
gap, D145).

Decisions: D144, D145, D183 (written down).

## Step 4: Writing eval with code checks — Wave 2 — TODO

Depends on: 1.

After it the user can run `python -m fpl.eval.writing` and see one row
per brief and run (examples a, b, c and the real gameweek-6 copy, 3
runs each), a pass/fail column per code check, total pass rate, total
tokens, PASS or FAIL against the bar, and every explanation's text
below. Saved as `results/YYYY-MM-DD-<commit>-writing.txt`.

Creates:
- `fpl/eval/writing/__init__.py`, `fpl/eval/writing/__main__.py`: loads
  the four folders (`tests/data/example_a`, `_b`, `_c`, `snapshot`),
  builds each brief, runs, prints, saves via `report.commit()` and
  `report.save(text, f"{commit}-writing")` (D152, D103/D115 rules).
- `fpl/eval/writing/run.py`: `BRIEFS`, `RUNS = 3` (D150),
  `MAX_CALLS = 40` (D180); `SCORERS = [checks]`; an `ask` wrapper that
  counts calls and tokens and stops the run at the cap (the report says
  where it stopped). Writer = `fpl.explain`'s model, block and prompt;
  scorers' `start` runs first.
- `fpl/eval/writing/checks.py`: one column per module in `CHECKS` (all
  of them, live or not); summary = pass rate, passed only at 100%
  (D153).
- `fpl/eval/writing/report.py`: header (commit, model that answered),
  table, totals (pass rates, tokens when given, no dollars, D166), the
  verdict line PASS / FAIL with no recommendation (D153), then the texts.

Changes: `README.md` (how to run it, that it spends plan limits).

Tests: `tests/test_eval_writing.py` with a fake `ask` (D160): 12 rows;
a bad text fails its column and makes the verdict FAIL; tokens summed,
"-" when None; call cap stops the run and says so; file name ends
`-writing.txt` under a temp dir.

Decisions: D126 (code checks), D150, D151 (numbers, names), D152, D153
(code checks), D154 (replaced by D176, D180), D160 (eval report), D166,
D180.

## Step 5: Score breakdowns in the block — Wave 3 — TODO

Depends on: 2.

After it the explanation can say why the captain is the captain:
form, points per game, minutes, opponent, difficulty, chance, games
played and how far the shrink moved the base.

Creates: `fpl/explain/parts/breakdown.py` (D141, D182): for the captain,
the vice and every player in a close call (from `close.calls`): form,
points per game, minutes factor, next opponent (H/A), fixture
difficulty, playing chance, next-GW score, games played
(`score.appearances`), typical score for position and start price, base
before and after shrink; each rounded to 1 decimal.

Changes:
- `fpl/score.py`: `typical_bases(elements) -> {id: typical base}` taken
  out of `shrunk_bases`, which then uses it; results unchanged.
- `fpl/explain/block.py` (one line in `PARTS`).

Tests: `tests/test_explain_breakdown.py` (example A captain's numbers by
hand; typical base equals the regression line; `shrunk_bases`
unchanged, existing `test_shrink.py` still passes);
`tests/test_explain_block.py` + `tests/data/explain_block.txt`: the
frozen block for the real gameweek-6 brief (snapshot), shown to the
owner once, then frozen (D160).

Decisions: D138 (breakdowns), D141, D182, D160 (frozen block).

## Step 6: Eval-only checks — Wave 3 — TODO

Depends on: 2, 4.

After it the writing eval also shows columns for at most 150 words,
captain named, every warning player named, every close call mentioned.

Creates (`LIVE = False` each, D151):
- `fpl/explain/checks/length.py`: words <= `MAX_WORDS`.
- `fpl/explain/checks/captain.py`: captain's name in the text.
- `fpl/explain/checks/warnings.py`: every warning player's name.
- `fpl/explain/checks/close.py`: for each close call from
  `close.calls`, both players' names in the text.

Changes: `fpl/explain/check.py` (four lines in `CHECKS`).

Tests: `tests/test_check_coverage.py`: good and bad hand-written texts
for A (must mention the 0.6 captain call, D184), B (must name Hart,
D157) and C (both close calls); 151 words fails; live explain does not
skip on an eval-only failure.

Decisions: D136 (checked), D151, D155.

## Step 7: Judge, and a check of the judge — Wave 4 — TODO

Depends on: 3, 4, 5, 6.

After it `python -m fpl.eval.writing` also shows clarity 1-5, faithful
yes/no and a reason per explanation, mean clarity and faithful rate,
and at the top whether the judge passed its own check on 8 fixed texts;
if not, that run's scores are marked unproven. Verdict PASS needs 100%
code checks, 100% faithful and mean clarity >= 4.0.

Creates:
- `fpl/eval/writing/judge.py`: `JUDGE_MODEL = "opus"`, no fallback
  (D167, D174); `JUDGE_TIMEOUT = 180` (D176); `CLARITY_BAR = 4.0`.
  `score`: asks with `judge.txt` as system prompt and block + text as
  prompt; reads one line `clarity=<1-5> faithful=<yes|no> reason=<text>`;
  anything else counts as a judge failure, never a pass (D175).
  `start`: runs the judge on the 8 texts, passes only with faithful=no
  on all 6 faulty and yes on both clean (D179).
- `fpl/eval/writing/judge.txt`: first draft of the rubric (D185).
- `fpl/eval/writing/judge_check.txt`: 8 explanations of the real
  gameweek-6 brief, each marked faulty or clean, with the six faults of
  D179; the owner reads and edits them.

Changes: `fpl/eval/writing/run.py` (one line in `SCORERS`).

Tests: `tests/test_eval_judge.py` with a fake `ask`: the line parser
(good line; clarity 6, missing field, extra text → failure); judge
check pass and fail, fail is said at the top and scores unproven;
verdict needs all three bars; all 8 texts pass every code check in
`CHECKS` against the frozen block (D179).

Decisions: D126 (judge), D149, D153, D167, D174 (judge), D175, D176
(judge), D179, D183 (fault 1), D185 (rubric draft).

Owner check (D160): run `python -m fpl.eval.writing` once for real;
read and edit `writer.txt`, `judge.txt` and `judge_check.txt`.

---

## UNCOVERED

None. D127 and D154 are replaced (D148; D176, D180) and noted where their
replacements are built. D110 (data/raw/ overwrites) is a stage 2 item
left for a separate change.

## Notes (my readings; correct them before approving)

- "The real gameweek-6 copy" (D150) = `tests/data/snapshot/`, the
  golden-file brief from stage 1.
- "Every close call mentioned" (D151) is checked as: both players'
  names appear in the text. It cannot check the reasoning; the judge
  covers that.
- The block is the brief as printed plus the parts' sections, not
  `--json`, because the JSON has unrounded floats and D143 compares
  numbers "as printed".
- Only numbers (D143) and names (D144) run live (D146); length,
  captain, warnings and close calls are eval columns only (D151).
- Each eval run's call order: 8 judge-check calls, then 12 writer and
  12 judge = 32 of the 40 allowed (D180).
