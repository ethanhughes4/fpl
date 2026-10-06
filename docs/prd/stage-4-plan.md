# Stage 4 plan

Built from docs/prd/stage-4-decisions.md (D208-D248). Stages 1-3 are built:
`brief.build(feed)` and `brief.render(data)` give the brief, `explain.block.build(data, feed)`
the stage 3 input block, all with no network.

Step 1 is the D110 fix, as D216 orders. The server skeleton, and the thinnest
path through it, is step 2.

## Skeleton (made in step 2)

- `fpl/mcp/` is the server package; `python -m fpl.mcp [--from <folder>]` runs it on
  stdio (D231). The `mcp` package resolves to the installed SDK (absolute imports).
- `fpl/mcp/session.py` holds the one data folder the server serves (D227, D240, D241, D228):
  - `start(folder=None, download=fpl.download.download, now=None)`; `--from` fixes the folder
    and nothing is ever downloaded.
  - `reply(body, fresh=False) -> str`: picks the folder (below), loads the feed and returns
    `Data downloaded <Tue 6 Oct 09:14>, gameweek N` + a blank line + `body(feed)`.
    Feed down / team not found → the D45 / D46 message only; the server keeps running.
    A `ManualError` (this-week.json) or no upcoming gameweek → that message.
  - Folder choice: `--from` folder; else the current folder while its saved deadline is in
    the future; else today's newest `YYYY-MM-DD-gwNN[-K]` folder in `data/raw/` (highest K,
    no `-team`/`-eval` folders) if its deadline is in the future; else download. `fresh=True`
    always downloads (a new folder, D218). A failed download leaves the current folder as it
    was; the failing call shows only the message (D228: no answer from older data).
  - Paths are from the repo root (`Path(__file__).parents[2]`), not the working folder, so
    the eval can run claude elsewhere.
  - Download time = mtime of `bootstrap-static.json` (D241).
- `fpl/mcp/server.py`: `TOOLS = [get_brief]` — modules in `fpl/mcp/tools/`, each with
  `DESCRIPTION` (owner edits it, D238) and `tool(<typed args>) -> str` that returns
  `session.reply(...)`. `build() -> FastMCP` registers each `tool` under its module's name,
  description = `DESCRIPTION` + the shared `LIMITS` text (D230, D246: cannot see injury
  length, price rises, rivals, cannot make transfers — say so, don't guess; quote numbers
  as given, compute none), annotation `readOnlyHint=True` (D231).
  To switch a tool on: add its file, add one line to `TOOLS`.
- `.mcp.json` (repo root) registers the server as `fpl` (D243).
- Tool output is plain text, numbers printed as the brief prints them (D224).
- Nothing in `fpl/mcp/` imports `fpl.claude` (D225, D232).
- Steps never edit this plan. Tuning numbers (top 5, 1-4 players, 40 calls, 6 turns,
  180 s, 3 runs, 90%) are named constants at the top of their file.

## Waves

| Wave | Steps | Notes |
|------|-------|-------|
| 1 | 1 | D110 fix |
| 2 | 2 | skeleton + get_brief |
| 3 | 3, 5, 6 | share only `TOOLS` |
| 4 | 4 | needs `fpl/mcp/names.py` from step 3 |
| 5 | 7 | path eval; needs all five tools |

---

## Step 1: A rerun never overwrites a download — Wave 1 — DONE

Depends on: none.

After it the user can run `python -m fpl` twice in one day and see two folders,
`2026-10-06-gw06` and `2026-10-06-gw06-2`, the first untouched (this-week.json copy
included); `python -m fpl --team 123` writes `2026-10-06-gw06-team123`. `docs/roadmap.md`
is committed.

Changes:
- `fpl/download.py`: `OWNER_TEAM = 8027067`. Folder name `YYYY-MM-DD-gwNN`, plus
  `-team<id>` when team != OWNER_TEAM, plus `-2`, `-3`, ... for the first name not taken.
  Created with `mkdir(exist_ok=False)`. The this-week.json copy is never removed (D218).
- `fpl/__main__.py`: `DEFAULT_TEAM` comes from `download.OWNER_TEAM` (one number, one place).
- `README.md`: the downloads line (folder names, never overwritten).
- `docs/roadmap.md`: commit as written (D217, D209).

Tests (`tests/test_download.py`, tmp folders, fake HTTP): second run → `-2`, third → `-3`,
first folder's files byte-identical; rerun without this-week.json keeps the old copy;
other team → `-team<id>`, its rerun → `-team<id>-2`; owner team has no suffix.
Old tests that expected overwrite or removal are changed to the new rule.

Covers: D216, D218, D219, D209, D217, D215.

---

## Step 2: Ask Claude Code "who should I captain?" — Wave 2 — DONE

Depends on: 1.

After it the user can open Claude Code in this repo, accept the `fpl` server, ask
"who should I captain this week?" and get an answer built from `get_brief`.
`python -m fpl.mcp --from tests/data/snapshot` serves the snapshot with no network.

Creates:
- `fpl/mcp/__init__.py`, `fpl/mcp/__main__.py` (argparse `--from`, `session.start`,
  `server.build().run()` on stdio).
- `fpl/mcp/session.py`, `fpl/mcp/server.py` (skeleton above; `LIMITS` drafted, D230).
- `fpl/mcp/tools/__init__.py`, `fpl/mcp/tools/get_brief.py`: no arguments, no team id
  (D221), upcoming gameweek only (D222); body = `explain.block.build(data, feed)` as it is —
  brief (header says when transfers were entered by hand, D226), close calls, breakdowns;
  never the explanation (D225).
- `.mcp.json`: `{"mcpServers": {"fpl": {"command": "python", "args": ["-m", "fpl.mcp"]}}}`.

Changes:
- `README.md`: "Ask Claude" section — `pip install mcp==<pinned>`, what the five tools are
  (filled as they land), costs nothing to run (D232), read-only (D211).
- `tests/conftest.py`, only if the in-memory client needs it: allow `connect` to
  127.0.0.1 (asyncio's socketpair on Windows); everything else still refused.

Tests:
- `tests/test_mcp_session.py` (fake download copying a test folder, `os.utime` for the
  time, `now` passed in): reuses today's newest folder (`-2` over the plain one) with a
  future deadline; deadline passed → downloads; no folder today → first call downloads,
  second reuses; `fresh=True` → new folder; `--from` never downloads; header line text;
  feed down / team not found → D45 / D46 text, the next call works; bad this-week.json →
  its message.
- `tests/test_mcp_brief.py`: `get_brief` on examples a-c and the snapshot = header +
  the frozen block (`tests/data/explain_block.txt` for the snapshot); no "Explanation".
- `tests/test_mcp_server.py`: through the SDK's in-memory client, the listed tools are
  exactly `TOOLS` by name, each read-only, each description ends with `LIMITS`; calling
  `get_brief` returns the same text as the direct call; fake claude never called.

Covers: D208, D210, D211, D212, D213 (as D223), D220, D221, D222, D223 (get_brief),
D224, D225, D226, D227, D228, D230, D231, D232, D238, D239, D240, D241, D215, D237.

---

## Step 3: Ask about and compare 1-4 players — Wave 3 — TODO

Depends on: 2.

After it the user can ask "how does Groß compare with Haaland and Tarkowski?" and
Claude answers from `get_players`.

Creates:
- `fpl/mcp/names.py`: `resolve(arg, pool) -> element or message`. An id (int or digits)
  matches by id; a name by `manual.matches` (D68 rules). None → `No player matches "X".`;
  several → one line each: name, club, position, price, id (D229).
- `fpl/mcp/tools/get_players.py`: `names: list[str]`, `MAX_PLAYERS = 4` (1-4 else a
  message). Per player: the breakdown line (D141/D182) plus club, price, six-week score,
  status, news, in your squad or not. With 2+ players, for next-GW and six-week score
  separately: `Next-GW: Groß leads; Haaland 0.8 behind; Tarkowski level with Groß.` worked
  from printed values (D140, D246, D248), leader and ties ordered by D27 on printed values.

Changes:
- `fpl/manual.py`: `_find`'s matching becomes `matches(name, pool) -> [elements]`, used by
  `_find` (its messages unchanged).
- `fpl/explain/parts/breakdown.py`: one player's line becomes `line(name, el, feed, shrunk,
  typical)`, used by `lines` (frozen block unchanged).
- `fpl/mcp/server.py`: one line in `TOOLS`.

Tests (`tests/test_mcp_players.py`, worked by hand in `.notes.txt` as D160): one player
on examples a-c; two players; three players whose leaders differ between the two scores;
a level case; tie ordered by D27; non-squad player says so; "Palmer" in the snapshot
lists Cole (154) and Alex (301); `"154"` picks Cole; no match; 0 and 5 names → message.
Existing manual and frozen-block tests still pass.

Covers: D212, D223 (get_players), D224, D229, D246, D248, D237.

---

## Step 4: "Who could replace Szoboszlai?" — Wave 4 — TODO

Depends on: 3 (`fpl/mcp/names.py`).

After it the user can ask for replacements for a squad player and get the top 5
incoming players with gain, price, starts or not, and whether each clears the free (2)
and hit (8) bars.

Creates:
- `fpl/mcp/tools/find_replacements.py`: `name: str` (or id). `TOP_REPLACEMENTS = 5`.
  Not in the squad → `X is not in your squad.` (D229). Each row: name, club, price,
  six-week gain (halved when he would not start, D63), `starts` / `bench, half gain`,
  `clears free bar 2: yes/no`, `clears hit bar 8: yes/no`. Header gives bank + his selling
  price. None legal → says so.

Changes:
- `fpl/sections/transfers.py`: the single-swap search for one outgoing player becomes
  `replacements(feed, out_el) -> [(gain, out, in, starts)]` sorted as today (same
  position, budget = bank + selling price, three per club, available with chance ≥ 75%,
  starts judged after the swap). `build` uses it; brief output unchanged.
- `fpl/mcp/server.py`: one line in `TOOLS`.

Tests (`tests/test_mcp_replacements.py`): examples a-c by hand; snapshot "Szoboszlai" →
top is Schade +14.7 and "O'Shea" → top is Davis +11.4, the brief's own choices; a non-squad
player; a too-expensive player excluded; a fourth player from one club excluded; a
bench-only incoming player shows half gain; bars at exactly 2.0 and 8.0. All brief tests
and goldens still pass.

Covers: D212, D223 (find_replacements), D224, D229, D63, D237.

---

## Step 5: "How did the last eval do?" — Wave 3 — TODO

Depends on: 2.

After it the user can ask for the latest scoring, writing or tools eval and Claude reads
the newest results file.

Creates:
- `fpl/mcp/tools/get_eval_results.py`: `kind: "scoring" | "writing" | "tools"`. Files in
  `results/`: scoring `DATE-<commit>.txt`, writing `...-writing.txt`, tools `...-tools.txt`
  (never `-tools-quick`, D247). Newest = its commit appears first in `git log --format=%h`
  (a `-dirty` commit counts as its base; unknown commits last; same commit → later date).
  Returns the file name and its text. Bad kind or no file → a one-line message.

Changes: `fpl/mcp/server.py`: one line in `TOOLS`.

Tests (`tests/test_mcp_eval_results.py`, tmp results folder, faked git log): newest by
commit order, not by date; dirty and unknown commits; tools ignores tools-quick; scoring
ignores writing/tools files; bad kind; empty folder.

Covers: D223 (get_eval_results), D247, D237.

---

## Step 6: "Get fresh data" — Wave 3 — TODO

Depends on: 2.

After it the user can say "download the latest data" and the server makes a new folder
and replies with its time and gameweek.

Creates:
- `fpl/mcp/tools/refresh.py`: no arguments; `session.reply(..., fresh=True)`; body
  `Downloaded to data/raw/<folder>.` Under `--from`: `Serving a saved folder; nothing
  downloaded.` with the usual header.

Changes: `fpl/mcp/server.py`: one line in `TOOLS`.

Tests (`tests/test_mcp_refresh.py`): two refreshes → two new folders, both kept; the
next get_brief uses the newest; feed down → D45 message and later calls use the old
folder; `--from` never downloads.

Covers: D223 (refresh), D227, D218, D228, D237.

---

## Step 7: Path eval `python -m fpl.eval.tools` — Wave 5 — TODO

Depends on: 3, 4, 5, 6.

After it the user can run `python -m fpl.eval.tools` (30 `opus` calls, cap 40) or
`--quick` (10) and see, per question and run, the tools called, path right or wrong,
number and name checks, PASS or FAIL, saved to `results/DATE-<commit>-tools.txt` or
`...-tools-quick.txt`. The owner then connects the server in Claude Code and asks three
questions for real (D237).

First, one real call (D233, D242): try `--safe-mode` with `--mcp-config`; if the server
does not load, drop it for flags that keep the owner's CLAUDE.md, hooks and plugins out,
proven by the input-token count. Check the stream-json field names, that Claude cannot
read the repo, and that the MCP tools run with no prompt. Write what was found at the top
of `fpl/eval/tools/run.py`. If neither flag set works: stop and ask the owner.

Creates:
- `fpl/eval/tools/__init__.py`, `__main__.py` (`--quick`), `questions.py`, `run.py`
  (parallel as D200, `RUNS = 3`, `MAX_CALLS = 40`, `MAX_TURNS = 6`, `TIMEOUT = 180`,
  `MODEL = "opus"`, `PASS_PATH = 0.9`), `path.py` (stream-json → calls; required/allowed
  check, D245; player args resolved through `fpl.mcp.names` on the snapshot), `report.py`
  (save via `fpl.eval.report.save` with `-tools` / `-tools-quick`).
- A temp MCP config per run: server `fpl`, `python -m fpl.mcp --from <repo>/tests/data/snapshot`;
  claude runs in an empty temp folder with `--tools ""`, `--allowedTools mcp__fpl`,
  `--strict-mcp-config`, `--max-turns 6`, `--output-format stream-json` (D243, D244).
- Answer checks: stage 3 `numbers` and `names` checks with `block` = all tool outputs of
  that run joined (D233, D246); no tool output → any number fails.
- `tests/test_eval_tools.py`, `tests/data/tools_stream_*.jsonl` (faked stream-json).
- `tests/test_mcp_count.py`: in-memory client lists exactly 5 tools, all read-only (D237).

Changes:
- `fpl/claude.py`: `ask_tools(prompt, mcp_config, model, timeout, max_turns) -> (events,
  text, tokens, model_id)`, same error handling as `ask`; no system prompt (the owner
  chats with Claude Code's own).
- `tests/fakeclaude.py`: `system.txt` optional; a stream-json output helper.
- `README.md`: "Path eval" section.

Questions (snapshot, gameweek 6; ids: Groß 124, Haaland 411, Tarkowski 229,
Szoboszlai 368, O'Shea 304, Palmer 154 / 301):

| # | Question | Required (args) | Allowed |
|---|----------|-----------------|---------|
| 1 | Who should I captain this week? | get_brief | get_brief, get_players |
| 2 | Why is Haaland's score what it is this week? | get_players [411] | get_players, get_brief |
| 3 | Compare Groß, Tarkowski and Haaland for me. | get_players [124, 229, 411] | get_players, get_brief |
| 4 | Is Palmer better than Groß right now? | get_players [124, Palmer: 154 or 301 or the ambiguous name] | get_players, get_brief |
| 5 | Who could replace Szoboszlai? | find_replacements [368] | find_replacements, get_players, get_brief |
| 6 | I want O'Shea out. Best options? | find_replacements [304] | find_replacements, get_players, get_brief |
| 7 | How did the latest writing eval do? | get_eval_results (writing) | get_eval_results |
| 8 | Download the latest data, then tell me my captain. | refresh, get_brief | refresh, get_brief, get_players |
| 9 | Make the Szoboszlai to Schade transfer for me. | none | find_replacements, get_brief (D245) |
| 10 | What does the Bench Boost chip do? | none | none |

Pass (D236, D247): path right on ≥ 90% of runs (27 of 30; 9 of 10 quick) and 100% of
answers pass number and name checks; a turn-limit hit or timeout is a wrong path.

Tests (fake claude only): path checker on right, missing, extra-allowed, forbidden and
split-across-calls paths; Palmer by name or either id; no-tool question with a call fails;
report on faked stream-json; cap 40 stops; `--quick` file name; PASS/FAIL thresholds.

Covers: D214, D232, D233, D234, D235, D236, D242, D243, D244, D245, D246, D247, D237, D215.

---

## Plan choices to check at approval

1. Step 1 is the D110 fix (D216); the skeleton comes in step 2.
2. `refresh()` under `--from` downloads nothing and says so (eval question 8 runs that way).
3. A failed refresh keeps the server on its current folder for later calls.
4. Folder names: `DATE-gwNN[-team<id>][-K]`.
5. "Newest" results file: `-dirty` = its base commit; unknown commits rank last.
6. get_players with 0 or 5+ names returns a message.

## UNCOVERED

None. D208-D248 each appear in at least one step.
