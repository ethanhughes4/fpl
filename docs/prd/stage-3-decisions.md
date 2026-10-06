# Stage 3 decisions

Context found before questioning (2026-10-06):

- Stages 1 and 2 are built (D1-D123). `python -m fpl` prints the brief
  using the "shrink" formula (D121-D123); `python -m fpl.eval` replays
  gameweeks 2-5 and saves a results table.
- No document defines stage 3. The only written hint is D50: "stage 2
  gives it to a model, stage 3 scores it". D70 moved stage 2 to evals,
  so "give the brief to a model" has not been done by any stage.
- `--json` prints the brief as plain data (D50), ready to hand to a model.
- The `anthropic` Python library 0.125.0 is installed. No
  ANTHROPIC_API_KEY is set in the shell.
- Known open item: D110 (brief reruns overwrite / remove files in
  data/raw/, against the CLAUDE.md boundary) was left for a separate change.
- Numbering continues from stage 2, starting at D124.
- No .env file exists yet, and .gitignore does not list .env
  (checked 2026-10-06 with ls and git check-ignore; the file was not read).

## Decisions given up front by the owner (2026-10-06)

D124: Stage 3: a model writes a short plain-English explanation on top of the brief: why this captain, which calls are close, what the warnings mean for the owner. (reason: owner; fulfils D50)
D125: Every number and pick still comes only from the stage 1 and 2 code. The model never changes a number and never invents a player or a fact. (reason: owner)
D126: Evals for the writing: a check that every number and name in the text matches the brief's JSON, plus a model-as-judge check for clarity. (reason: owner)
D127: The API key lives in .env. Claude Code must never read .env. (reason: owner)
D128: Tests never call the model for real. (reason: owner; same rule as D77 for the feed)
D129: Cost limits and model choice are asked, not assumed. (reason: owner)

## Questions one at a time (2026-10-06)

### Purpose
D130: Only the owner reads the explanation. It is a one-shot text printed with the brief; the owner acts on it himself on the FPL site. No follow-up chat, no other readers, not sent anywhere. (reason: owner)
D131: The explanation is on by default: `python -m fpl` prints the brief, then the explanation. `--no-explain` turns it off. (reason: owner — wants it every week with the team update)
D132: `--from <folder>` replays never call the model unless `--explain` is also given. (reason: owner — replays are for tests and evals and must not spend money silently)
D133: Scheduled runs stay out of stage 3 (D58 stands); a later stage. (reason: owner)
D134: If the key is missing or the model call fails, the normal brief is still printed, then one line saying the explanation was skipped and why; exit 0. The numbers never depend on the model being available. (reason: owner) "Key missing" now reads "Claude Code not installed or not logged in" (D147, D162).

## Questions sent as one list (2026-10-06) — owner replied only where he disagreed

Facts found for this list: `python -m fpl --from tests/data/example_{a,b,c}`
gives the briefs used in D156-D158. Claude Code 2.1.291 is installed at
~/.local/bin/claude.exe.

### Running it
D135: `--json` never calls the model; its output stays exactly as today. (reason: it is the fixed reference the checks compare against)
D136: The explanation is printed after the brief under a line `Explanation`, plain text, no markdown, at most 150 words (named constant). (reason: "short"; readable in a terminal)
D137: If both `--explain` and `--no-explain` are given, the last one on the command line wins. (reason: harmless, no error needed)

### What the model is given
D138: The model gets one input block built by code: the brief's data, the close calls (D139) and score breakdowns (D141). It never sees the raw feed. (reason: a fact not in the block cannot be used, and the checker knows exactly what is allowed)
D139: Close calls are worked out by code: captain vs vice gap; lowest outfield starter vs best outfield bench player gap; for each suggested transfer, its gain minus the bar it had to clear (2 free, 8 hit). Close = captain or bench gap <= 0.5, or transfer margin <= 2.0 (both named constants). (reason: "close" stays a number from code, D125) CHANGED by D181: captain gap close at <= 1.0.
D140: A gap is the difference of the two numbers as printed (1 decimal): 7.3 - 7.2 = 0.1 even if the unrounded gap is 0.19. (reason: the owner can subtract what he sees)
D141: Score breakdown for the captain, the vice and every player in a close call: form, points per game, minutes factor, next opponent (home/away), fixture difficulty, playing chance, next-GW score, each rounded to 1 decimal. (reason: "why this captain" needs the parts, not just the total) EXTENDED by D182.
D142: Warnings are passed as the brief has them (name, chance, news text). The model says what they mean for the team (e.g. "already on your bench") and never guesses how long an injury lasts (D58). (reason: that is all the feed knows)

### Checks on every explanation (code, no model)
D143: Numbers: every number written in digits must appear in the input block as it would be printed. Signs are ignored ("4-point hit" matches -4); "6.9m" matches 6.9. (reason: catches changed or invented numbers)
D144: Names: the text must not contain any player or club name from the feed that is not in the input block. Matching ignores case and accents; allowed names are removed from the text before the search, so "João Pedro" does not trip on another "Pedro". (reason: catches swapped players)
D145: Known gaps, written down: a name not in the feed at all, and numbers written as words. The model is told to write every number in digits; the judge (D149) is the backstop. (reason: honest about what code can catch) EXTENDED by D183.
D146: The checks run on every live explanation. On a failure the explanation is not printed; one line instead, e.g. `Explanation skipped: it quoted 7.4, which is not in the brief.`, exit 0 (D134). No retry. (reason: a wrong explanation is worse than none)
D147: Other skip lines: `Explanation skipped: Claude Code is not installed or not logged in.` and `Explanation skipped: the model call failed (<reason>).` (reason: owner replaced the "no key" line; the refusal and cut-off lines are dropped because the CLI does not report them separately)

### Dropped by the owner
D148: No Anthropic API and no key: Q14-Q16 (key, .env), Q29 (Console spend limit) and Q30 (refusal fallbacks) are dropped. D127 is void: there is no .env. (reason: owner, change of plan, see D162)

### The writing eval
D149: The judge is a separate model call, in the eval only. Per explanation it gives clarity 1-5, faithful yes/no ("does it state anything the input block does not support?") and a one-line reason. (reason: owner asked for clarity; faithful backs up D145)
D150: Run with `python -m fpl.eval.writing`. Inputs: the four briefs already in tests/data/ (examples a, b, c and the real gameweek-6 copy), each explained 3 times (named constant). (reason: the model's answer varies run to run)
D151: Code checks scored in the eval: numbers (D143), names (D144), at most 150 words, captain named, every warning player named, every close call mentioned. (reason: what "good" means, checkable)
D152: Report: one row per brief and run; totals for code-check pass rate, faithful rate, mean clarity and tokens (when the output gives them, D166); every explanation's text printed below. Saved as results/YYYY-MM-DD-<commit>-writing.txt, same rules as D103/D115. No dollar figures. (reason: owner)
D153: Pass bar: 100% code checks, 100% faithful, mean clarity >= 4.0. The report shows pass or fail; the owner decides what to do (as D101). (reason: a fabricated fact is never acceptable)
D154: Limits: 60-second timeout per call (named constant); the eval stops after 30 model calls (named constant). (reason: owner) Timeouts CHANGED by D176; cap CHANGED by D180.

### Examples (D150 inputs; the wording varies, so expected = what it must contain)
D155: An explanation must name the captain and why, mention each close call and each warning, and contain no number or name outside the input block. (reason: model text is never the same twice)
D156: Example A: Hart captain 7.9 over Marsh 7.3, gap 0.6, not close. Close: lowest outfield starter (Fry or Kemp 4.1) vs Orr 3.8, gap 0.3. "Save it, 4 free next week." No warnings. (reason: normal week) CHANGED by D184: the captain gap 0.6 is now close.
D157: Example B: Marsh 7.3 over Innes 7.2, gap 0.1, close. Hart 25% hamstring, already benched; Hart -> Wren +13.4, far above the bar of 2, not close. (reason: injury)
D158: Example C: Hart over Marsh, not close. Kemp 4.1 on the bench vs Fry 4.1 starting, gap 0.0, close. Lowe -> Yates +10.8 against a hit bar of 8, margin 2.8, not close; must say it costs 4 points. (reason: hit) CHANGED by D184: the captain gap 0.6 is now close.

### Boundaries
D159: Out of scope: chat; scheduled runs (D133); the model choosing or changing any pick; giving the model web search or any tool; saving explanations into data/raw/; streaming text to the screen; predicting injury length. (reason: keep to D124)

### Proof
D160: Tests, none of which run claude (a fake subprocess stands in): checker unit tests on hand-written good and bad texts; close calls for examples A-C worked out by hand (D156-D158); one frozen model input block for the real gameweek-6 brief, checked by eye once; every path in the brief command: success, Claude Code missing, call failed, timeout, checker failure, `--from` without a call, `--no-explain`, `--json` unchanged; the writing eval's report on a fake writer and judge. The owner runs `python -m fpl` and `python -m fpl.eval.writing` once for real. (reason: tests cannot prove the writing is good)

### Ownership
D161: The owner writes the writer prompt and the judge rubric himself, each in its own plain text file. Claude writes everything else, including a working first draft of both prompts so tests and the first eval can run. (reason: the prompt is the part most worth learning; the writing eval shows whether his edits help) CHANGED by D185.

## Change of plan (2026-10-06): Claude Code instead of the API

Docs: https://code.claude.com/docs/en/cli-reference and
https://code.claude.com/docs/en/headless (read 2026-10-06). Facts found:
`--bare` skips CLAUDE.md and hooks but "doesn't use your subscription
login" (needs ANTHROPIC_API_KEY), so it cannot be used. `--safe-mode`
turns off CLAUDE.md (user and project), skills, plugins, hooks, MCP servers
and auto memory, while "Authentication, model selection, built-in tools, and
permissions work normally". `--tools ""` disables all built-in tools.
`--output-format json` gives the text in `result`, plus `usage` and a
per-model breakdown. A failure inside the run is printed as the result on
stdout with a non-zero exit code. `--model` takes the aliases `haiku`,
`sonnet`, `opus`, `fable`; `fable` needs Fable access.

D162: Writer and judge both run Claude Code in print mode (`claude -p`) through subprocess, using the owner's existing login. No Anthropic API, no key. (reason: owner)
D163: The call runs from a new empty temporary folder, so this repo's CLAUDE.md, settings and hooks are not loaded. (reason: owner)
D164: It works on Windows. (reason: owner)
D165: The call sits behind one small function in one file (prompt in, text out), so a later switch to the API changes one file. (reason: owner)
D166: No dollar prices. Tokens are reported when the JSON output gives them. The 60-second timeout and the 30-call cap stay (D154). (reason: owner)
D167: Writer = the cheapest model available this way; judge = the strongest. (reason: owner)
D168: Tests fake the subprocess and never run claude. (reason: owner; extends D128)

## Follow-ups after the change of plan (2026-10-06): F1-F10 accepted, with the owner's changes

D169: Command (F1), checked by a real call on 2026-10-06 (F10), worked first time with Claude Code 2.1.291, exit 0, run folder still empty afterwards:
  `claude -p --safe-mode --model <alias> --system-prompt-file <file> --tools "" --strict-mcp-config --no-session-persistence --max-turns 1 --output-format json --permission-prompts none`
  with the prompt on stdin and the working directory a new empty temporary folder. input_tokens was 648 for a one-line system prompt, which shows the default Claude Code prompt and CLAUDE.md files were not loaded. (reason: owner; --safe-mode keeps out the user-level CLAUDE.md, hooks and plugins that an empty folder alone does not)
D170: Real JSON field names (from that call): `type` ("result"), `subtype` ("success"), `is_error` (false), `result` (the text), `stop_reason` ("end_turn"), `terminal_reason` ("completed"), `num_turns`, `api_error_status` (null), `usage.input_tokens`, `usage.output_tokens` (includes `usage.output_tokens_details.thinking_tokens`), `modelUsage` (an object keyed by the full model id, e.g. "claude-haiku-4-5-20251001"), `total_cost_usd` (never shown, D166). Tokens = usage.input_tokens + usage.output_tokens. The model that answered = the modelUsage key. (reason: F10)
D171: Windows (F2): find the program with shutil.which("claude"); run from a list of arguments, no shell=True; prompt on stdin, system prompt in a file in the temporary folder; UTF-8 in and out; TemporaryDirectory(ignore_cleanup_errors=True). (reason: command-line length and quoting limits; accented names; Windows file locks after a kill)
D172: Failures (F3): no claude on the path -> D147's "not installed or not logged in" line. Non-zero exit, is_error true, or subtype not "success" -> run `claude auth status` (10 s timeout, named constant); exit 1 there -> the same line, else `the model call failed (<first line of result>)`. Timeout -> `the model call failed (timed out after <N> s)`. JSON that cannot be read -> `the model call failed (unreadable output)`. (reason: F3)
D173: The one function (F4, D165): ask(prompt, system, model, timeout) -> (text, tokens, model id); tokens None when usage is missing. One error type carries the reason. All of it in one file. (reason: D166 needs tokens; D152 names the model that answered)
D174: Models (F5): writer `haiku`; judge `opus`, with no fallback model. Both named constants. (reason: owner; the judge must be the same model on every run so results can be compared)
D175: Judge output (F6): one line `clarity=<1-5> faithful=<yes|no> reason=<text>`. A line that cannot be read counts as a judge failure, never a pass. (reason: keeps D173 simple)
D176: Timeouts (F7): 60 s for the writer, 180 s for the judge (named constants). Replaces D154's single 60 s. (reason: owner; the strongest model plus startup can exceed 60 s, and the judge runs only in the eval)
D177: The calls count against the owner's Claude plan limits, not a bill. A plan limit being hit shows as `the model call failed (...)`. (reason: F8)
D178: CLAUDE.md gets the boundary line "Tests must never run claude." (reason: F9; sits beside the live-feed rule)

## Judge check and final changes (2026-10-06)

D179: Each eval run also tests the judge on 8 fixed explanations of the real gameweek-6 brief: 6 with one planted fault each, 2 clean. The judge passes only with faithful=no on all 6 faulty and faithful=yes on both clean; if it fails, the report says so at the top and that run's writing scores count as unproven. Faults: (1) a real number from the brief attached to the wrong player; (2) a made-up player name that is not in the feed; (3) a made-up fact ("he scored twice last week"); (4) a wrong number written as a word; (5) a guess at how long an injury lasts; (6) the wrong captain. Every fault is one the code checks cannot catch: a test checks that all 8 texts pass every D151 code check, so the judge check tests only the judge. Claude writes the 8 texts; the owner reads and edits them. (reason: owner — a judge nobody has tested proves nothing)
D180: Call cap per eval run = 40 (named constant). One run = 12 writer + 12 judge + 8 judge-check = 32 calls. Replaces D154's 30. (reason: owner; 30 did not fit, 40 leaves room for one more brief)
D181: Captain gap counts as close at <= 1.0. Bench gap (<= 0.5) and transfer margin (<= 2.0) are unchanged. Replaces D139's captain threshold. (reason: owner)
D182: The score breakdown (D141) also gives games played, the typical score for the player's position and start price, and the base before and after shrink. Games played is the brief's count, round(total_points / points_per_game) (D122), not the eval's exact count. The typical score is today worked out inside score.shrunk_bases and must be exposed. (reason: owner — the shrink is the newest part of the formula and needs explaining)
D183: Known gap: a real number from the brief attached to the wrong player passes the number check (D143); the judge is the backstop (D149, D179 fault 1). (reason: owner)
D184: With D181, the captain call is close in example A (Hart 7.9 vs Marsh 7.3, gap 0.6) and in example C (same gap), so both explanations must mention it. Example B (gap 0.1) is unchanged. (reason: follows from D181)
D185: Claude writes working first drafts of the writer prompt and the judge rubric, each in its own plain text file; the owner then edits them. Replaces D161's "owner writes them himself". Claude writes everything else. (reason: owner)

## Resolver answers during the build (2026-10-06)

D186: A result JSON with no `subtype` field is a failure, not a success: D172 fails anything whose subtype is not "success". (resolver; evidence: Agent SDK SDKResultMessage makes `subtype` required, "success" or an "error_*" value, https://code.claude.com/docs/en/agent-sdk/typescript)
D187: `claude auth status` exits 0 when logged in and 1 when not, as D172 assumes. (resolver; evidence: "Exits with code 0 if logged in, 1 if not.", https://code.claude.com/docs/en/cli-reference)
D188: The JSON fields read (`result`, `is_error`, `subtype`, `usage.input_tokens`, `usage.output_tokens`, `modelUsage` keyed by model id) match D170. Tokens are None when either usage count is missing, not only when `usage` is missing (D173). (resolver; evidence: SDK type `usage: NonNullableUsage; modelUsage: { [modelName: string]: ModelUsage }`, https://code.claude.com/docs/en/agent-sdk/typescript)
D189: When a model call fails (D172), after the login check the reason is the first text found in: `result`, the first entry of `errors`, the first line of stderr, the first line of stdout when it was not JSON. "unreadable output" only when none has text, or when the exit code is 0 and stdout is not JSON. The reason is kept to one line and cut to 200 characters (named constant). (owner, choosing option (c) from the resolver; evidence: "If you pass an invalid flag, Claude Code reports the error to stderr before the run starts", https://code.claude.com/docs/en/headless; error results carry `errors: string[]` and no `result`, https://code.claude.com/docs/en/agent-sdk/typescript)
D190: Names check (D144) refined: accents are still ignored, but a feed name only counts as named when the text writes it with a capital first letter, and a club code written in capitals in the feed (NEW, SUN, TOT) only when written in capitals. Names in the block are still removed ignoring case. Known gap: a sentence starting with a name-like word ("Will", "New") can still trip it. (owner; evidence: on the real gameweek-6 feed the case-blind check banned "new", "sun", "will", "max", "jack", "king", "wood", "white", "hill", "rice", "mount", so nearly every explanation would be skipped)
D191: Names check (D144, D190): a club counts as in the brief when the block prints its full name or its code in capitals (the breakdown's opponent "SUN"), so an explanation may name that club either way. Bug found by the step 7 builder: the block printed SUN but the check banned it, because only "Sunderland" was looked for. (fix during the build; follows D144 "names in the input block are allowed")
