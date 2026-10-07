# Stage 4 decisions

Context found before questioning (2026-10-06):

- Stages 1-3 are built (D1-D207). `python -m fpl` prints the brief
  (shrink formula, D121) and a Sonnet-written explanation checked by
  code (D202, D143-D146); `python -m fpl.eval` replays gameweeks 2-5;
  `python -m fpl.eval.writing` scores the writing (pass bar D207).
- No document defines stage 4. Written hints: D133 "scheduled runs ...
  a later stage". Still out of scope from earlier stages: chips, price
  changes, other teams / mini-leagues, injury length, web page (D58,
  D108, D159).
- Open item: D110. A same-day brief rerun overwrites its data/raw/
  folder (download.py writes every file; D41) and removes the
  this-week.json copy (D65), against the CLAUDE.md boundary "never
  edit or delete anything in data/raw/".
- Numbering continues from stage 3, starting at D208.

## Questions one at a time (2026-10-06)

Superseded at once by the owner's reply below; no decision was taken
on scheduled runs.

## Decisions given up front by the owner (2026-10-06)

D208: Stage 4 is a local MCP server: the owner asks Claude questions about his FPL team in plain English, and Claude answers by calling tools that run the existing code. MCP (Model Context Protocol) = a standard way for a program (the "server") to offer tools that Claude can decide to call. (reason: owner)
D209: Scheduled runs are stage 5, not stage 4. Replaces D133's "a later stage". (reason: owner)
D210: The server runs on the owner's PC and is used from Claude Code first. (reason: owner)
D211: Read-only: it never makes transfers and never logs in to FPL (as D16). (reason: owner)
D212: Every number comes from the stage 1 and 2 code; the server adds no new scoring. (reason: owner)
D213: Tool ideas to be questioned: this week's brief; any player's score and breakdown; compare two players; best replacements for a player within the owner's budget; the latest eval results. (reason: owner)
D214: The stage's evals check the path as well as the answer: given a question, did Claude call the right tool with the right arguments? (reason: owner)
D215: Tests never call the live feed and never run claude (CLAUDE.md, D168). (reason: owner)
D216: D110 is fixed as step 1, because the server runs the brief too. (reason: owner)
D217: docs/roadmap.md records the stages: 4 MCP server; 5 scheduled brief before the deadline; 6 chips, price changes, mini-league rivals and outside news. The app never makes transfers itself. (reason: owner — later stages are not guessed)

Found for the question list: the `mcp` Python library is not installed
(checked 2026-10-06). Claude Code 2.1.292 is installed; `claude mcp add
--scope project` writes a `.mcp.json` file in the repo that Claude Code
reads when started here. No `.mcp.json` exists yet. The explanation's
input block (fpl/explain/block.py: brief, close calls, score
breakdowns) is already built and frozen in tests. Name matching that
ignores case and accents exists in fpl/manual.py (D68). The download
folder name has no team id, so `--team` runs share the owner's folder.

## Questions sent as one list (2026-10-06) — owner changed Q9, Q16, Q17, Q21

### Step 1: D110
D218: A brief download whose folder already exists writes to a new folder with "-2", "-3", ... added; nothing in data/raw/ is ever overwritten or deleted, the this-week.json copy included. Fixes D110; replaces D41's "overwrites" and D65's "removes the copy". (reason: first folder keeps D41's name; deadline day needs fresh news)
D219: A `--team` run for a team other than 8027067 adds "-team<id>" to its folder name. (reason: today another team's run writes over the owner's folder)

### Purpose and tools
D220: Only the owner uses the server, from Claude Code opened in this repo. Claude Desktop and other users are out of scope. (reason: D210; the server is set up per project)
D221: No tool takes a team id; every tool uses 8027067. (reason: fewer arguments, fewer wrong calls)
D222: Upcoming gameweek only; questions about past gameweeks are out of scope. (reason: the stage 1-3 code scores only the next gameweek)
D223: Five tools. get_brief(): the stage 3 input block as it is (brief, close calls, breakdowns). get_players(names): 1-4 players, each with the D141/D182 breakdown line plus club, price, six-week score, status and news, and whether he is in the squad; replaces "compare two players". find_replacements(name): for a squad player, the top 5 (named constant) incoming players by the brief's single-transfer rules (same position, bank + his selling price, three per club, chance >= 75%, half gain if the incoming player would not start, D63), each with six-week gain, price, starts or not, and whether it clears the free bar (2) and the hit bar (8). get_eval_results(kind): newest results file of kind "scoring" or "writing", newest = its commit is latest in `git log`. refresh(): downloads the feed again (D227). (reason: reuse existing tested code; one tool less to choose wrongly)
D224: Tool output is plain text with numbers printed as the brief prints them (1 decimal, prices in millions only when printing). (reason: unrounded floats would be rounded by Claude and fail the number check)
D225: Nothing in the server runs claude; get_brief never includes the stage 3 explanation. (reason: Claude calling Claude is slow and costly; the chatting Claude explains)

### Data
D226: this-week.json is read as today, and the brief header still says when transfers were entered by hand. (reason: nothing new to build)
D227: When a session starts, the server reuses today's newest download folder if one exists; otherwise its first tool call downloads. Only refresh() downloads again and makes a new folder (D218). Every tool reply starts "Data downloaded <date time>, gameweek N" with the real download time. (reason: owner — one folder per day unless asked; changed from Q9's "download once per session")

### Failures
D228: Feed down or team not found: the tool returns D45/D46's message and the server keeps running; never falls back to older saved data. (reason: D45)
D229: No match: `No player matches "X".` Several matches: each with club, position, price and id; the tools also accept an id. find_replacements on a non-squad player: `X is not in your squad.` (reason: Claude can choose and call again; names repeat)
D230: The tool descriptions say what the server cannot do (injury length, price rises, rivals, making transfers) and that Claude should say so rather than guess. No write tool exists. (reason: no invented numbers)

### Technical
D231: The official `mcp` Python SDK (FastMCP) is installed, version pinned in the README. stdio transport (Claude Code starts the server as a hidden program and talks through its input and output); `python -m fpl.mcp`, with `--from <folder>` serving a saved folder with no network. Registered in a committed .mcp.json at the repo root. Every tool is marked read-only. (reason: owner approved the new dependency)
D232: The server costs nothing to run; only the path eval spends Claude plan limits. (reason: no model calls in the server, D225)

### Proof
D233: Path eval `python -m fpl.eval.tools`: `claude -p` against the server serving the frozen gameweek-6 snapshot via `--from`. Claude gets only the five MCP tools: no file, shell or web tools. Tool calls are read from `--output-format stream-json`; field names are checked on one real call first (as F10), and that call must also show that Claude cannot read the repo and that the MCP tools run without a permission prompt. Each question has an expected tool and arguments; a player argument is right when it resolves to the same player id. The final answer must pass the stage 3 number and name checks against the tool outputs. No judge; known gap: a wrong claim in words is not caught. (reason: owner added the tool limits and the real-call checks)
D234: 10 questions x 3 runs = 30 calls, cap 40 (named constant), covering every tool at least once, one ambiguous name and two questions that should call no tool. Calls run in parallel with the stage 3 eval code (D200). `--quick` runs each question once (10 calls). Expected tools and arguments are written during planning. (reason: owner added parallel and --quick)
D235: The eval uses `opus`, the model the owner chats with. (reason: the path depends on the model)
D236: Pass bar: right tool and arguments on >= 90% of runs (27 of 30), 100% of answers pass the number and name checks; the report shows PASS or FAIL, the owner decides (as D101, D207). (reason: one slip should not fail a good run)
D237: Tests (no feed, no claude): each tool on examples a-c, worked by hand; replacements checked against the brief's own transfer choice; name errors and ambiguous names; D218/D219 folder naming; the server lists exactly 5 read-only tools through the SDK's in-memory test client; the eval report on a faked stream-json output. The owner connects the server in Claude Code once and asks three questions for real. (reason: same pattern as D160)

### Ownership and boundaries
D238: Claude writes working drafts of everything, including the five tool descriptions and the server file; the owner edits them, as D185. (reason: owner)
D239: Out of scope: stages 5 and 6 of the roadmap, Claude Desktop, HTTP or remote serving, any login, any write tool, past gameweeks, other teams, running evals from the server, the stage 3 explanation inside a tool. (reason: keep to D208)

## Follow-ups (2026-10-06): F1-F8 accepted, F7 changed by the owner

D240: Today's folder is reused only while its gameweek is still the upcoming one, judged by the deadline saved in that folder; after the deadline the first tool call downloads again. Refines D227. (reason: a morning folder must not brief a gameweek that can no longer be changed)
D241: "Data downloaded" time = modification time of bootstrap-static.json in the folder (as D119); no new file. Tests set the time themselves, because copies lose it. (reason: already the real download time)
D242: On the one real eval call, `--safe-mode` with `--mcp-config` is tried first. If the server does not load, `--safe-mode` is dropped for flags that keep the owner's CLAUDE.md, hooks and plugins out (likely `--setting-sources`), proven by the input-token count as D169. If neither works, the builder stops and asks the owner. (reason: help text says --safe-mode disables MCP servers; the owner's SessionStart hooks must not shape eval answers)
D243: The server is named `fpl` in .mcp.json, so tools appear as mcp__fpl__<tool>. Eval calls pass `--tools ""` and `--allowedTools mcp__fpl`, so only the five tools exist and none prompts. (reason: D233; --permission-prompts none denies anything that would prompt)
D244: Eval calls allow 6 turns (named constant, replaces D169's --max-turns 1 for this eval); hitting the limit counts as a wrong path. Timeout 180 s per call (named constant, as the judge in D176). (reason: a tool call plus an answer needs at least 2 turns)
D245: Each eval question lists required tools (with arguments) and allowed tools. A run's path is right when every required tool is called with the right players, in any order and across any number of calls, and no tool outside the allowed set is called. Example: "Make the transfer for me" requires nothing and allows find_replacements and get_brief. (reason: an exact call list would fail sensible extra calls)
D246: Numbers: stage 3's rule stands, only numbers printed in tool outputs pass. Tool descriptions tell Claude to quote numbers as given and not compute new ones. When get_players is given more than one player, it also prints the gap between them for next-GW score and six-week score, saying who is ahead, worked from the printed values (D140). Added to the hand-worked tests. (reason: owner — do F7's fallback now so comparisons can be answered from printed numbers)
D247: A --quick run uses the same pass shares (9 of 10) and is saved as results/YYYY-MM-DD-<commit>-tools-quick.txt; a full run as ...-tools.txt. get_eval_results gains kind "tools", returning the newest full run. (reason: comparing description edits needs saved files)
D248: With more than one player, get_players gives, for each of next-GW score and six-week score separately, the leader and every other player's gap behind him, e.g. "Next-GW: Saka leads; Palmer 0.4 behind; Isak 1.1 behind." A 0.0 gap reads "level with <leader>" (as D199); ties are ordered by D27. Hand-worked tests: two players; three players whose leaders differ between the two scores; a level case. Extends D246. (reason: owner — at most 3 lines per score, answers "who is best and by how much")

## Resolver answers after wave 2 (2026-10-06)

D249: D231's "FastMCP" is `mcp.server.mcpserver.MCPServer` in the official SDK 2.x (renamed; `mcp.server.fastmcp` is removed). mcp 2.3.0 is the latest stable release and is what README pins. (resolver; evidence: https://py.sdk.modelcontextprotocol.io/v2/migration/#fastmcp-renamed-to-mcpserver, https://pypi.org/project/mcp/, site-packages mcp/server/fastmcp.py:1)
D250: In mcp 2.3.0, `Client(server)` connects to an MCPServer in-process, `list_tools()` gives `annotations.read_only_hint`, `MCPServer.tool(name=, description=, annotations=ToolAnnotations(readOnlyHint=True))` registers a plain function, and `run()` defaults to stdio. (resolver; evidence: site-packages mcp/client/client.py:288-294, mcp_types/_types.py:1379,1433, mcp/server/mcpserver/server.py:406,669-674)
D251: The SDK's stdio server writes and reads UTF-8 whatever the Windows code page, so "·", "ß", "ã" in tool output are safe. (resolver; evidence: site-packages mcp/server/stdio.py:170-179)
D252: On Windows, asyncio's event loop makes its self-pipe with socket.socketpair(), whose fallback connects to 127.0.0.1; the MCP tests therefore allow connect to 127.0.0.1 only, everything else stays refused. (resolver; evidence: CPython 3.13 Lib/socket.py:96,598-665, Lib/asyncio/proactor_events.py:786)
D253: .mcp.json stays `python -m fpl.mcp`; the README says to start claude from the repo root. Claude Code's docs do not say which folder a project stdio server starts in (they document CLAUDE_PROJECT_DIR in the server's environment, and no `cwd` field). The owner's live connect test (D237) proves it; if it fails, switch the args to load fpl.mcp via CLAUDE_PROJECT_DIR. (owner, on resolver escalation; evidence: https://code.claude.com/docs/en/mcp "Option 3: Add a local stdio server")

## Resolver answers after wave 3 (2026-10-06)

D254: A results file's commit (`git rev-parse --short`) and `git log --format=%h` both give the shortest unique prefix of at least core.abbrev, but the length is worked out each run and grows with the repo, so the two can differ. get_eval_results therefore matches commits by prefix, either way round; a wrong match needs a 7-hex-character collision and would only rank one old file too new. (resolver; evidence: https://git-scm.com/docs/git-rev-parse, https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreabbrev, git pretty.c `case 'h'`)
D255: The SDK (mcp 2.3.0) builds each tool's input schema from its Python type hints through pydantic: `names: list[str]` is a required JSON array of strings, `kind: str` a string, and a call's JSON arguments arrive as Python list and str; bad arguments come back as an error result, not a crash. Pydantic does not turn numbers into strings, so a number id was refused before reaching the tool; get_players now takes `list[str | int]` so an id sent as a number works (D229). (resolver; evidence: site-packages mcp/server/mcpserver/tools/base.py:102-107,152-156, utilities/func_metadata.py:112,139-164,335-362)
D256: get_players's "Give between 1 and 4 players." reply was sent without the data line; it now goes through session.reply like every other reply (D227). (resolver; evidence: fpl/mcp/tools/get_players.py)

## Resolver answers after wave 5 (2026-10-07)

D257: The path eval's claude command is `claude -p --setting-sources "" --model opus --mcp-config <tmp> --strict-mcp-config --tools "" --allowedTools mcp__fpl --no-session-persistence --max-turns 6 --output-format stream-json --verbose --permission-prompts none`, run in an empty temp folder; `--safe-mode` left the server unloaded (real call, D242). An empty --setting-sources keeps out user/project/local settings, including ~/.claude/CLAUDE.md, rules, skills and settings.json hooks (SessionStart included); --strict-mcp-config keeps out other MCP servers and connectors; `mcp__fpl` allows every tool of that server; `--tools ""` does not affect MCP tools. `--verbose` with stream-json rests on the real call, not a doc sentence. (resolver; evidence: https://code.claude.com/docs/en/agent-sdk/claude-code-features, https://code.claude.com/docs/en/cli-reference, https://code.claude.com/docs/en/permissions, fpl/eval/tools/run.py header)
D258: A `-p` run that hits --max-turns ends with result subtype `error_max_turns` and a non-zero exit; ask_tools treats any subtype other than `success` as a failure, which the eval counts as a wrong path (D244). (resolver; evidence: https://code.claude.com/docs/en/agent-sdk/agent-loop)
D259: For a `-> str` tool, mcp 2.3.0 sends a plain text block and structuredContent `{"result": "<text>"}`; Claude Code passed the structured form to Claude in the real call. The eval unwraps it and also accepts plain text. (resolver; evidence: site-packages mcp/server/mcpserver/utilities/func_metadata.py:209-226,534-536,652-655; fpl/eval/tools/path.py)
D260: In the path eval, names in the question text also pass the names check; numbers still pass only when printed in a tool output (D246). A correct refusal to "Make the Szoboszlai to Schade transfer for me." may name both players. Known: a no-tool answer that writes any digit (e.g. Bench Boost "15 players") still fails the number check, as D246 says. (owner, on resolver escalation; evidence: fpl/eval/tools/run.py answer checks, tests/test_eval_tools.py)

## Owner decisions after the first quick tools run (2026-10-07)

D261: "Make the Szoboszlai to Schade transfer for me." also allows get_players (now find_replacements, get_brief, get_players). Every tool is read-only, so a lookup before refusing is fine. Replaces D245's example. (owner — the quick run failed Q9's path for a get_players call before a correct refusal)
D262: The number and name checks give every failure, not only the first (`failures()`; `check()` still returns the first, worded as before, so the rules and the writing eval are unchanged). The tools eval prints the failing numbers and names in the table cell, e.g. "FAIL (4.3, 16.6)", and under each answer in the results file with the sentence each came from. (owner — to see what failed before changing tool descriptions or the number rule)

## Owner decisions after reading the failing numbers (2026-10-07)

D263: The number check ignores a list marker starting a line ("2. ", "3) ", after any indent): it numbers the line, it is not a quoted number. The same digits anywhere else are still checked. Shared check, so the writing eval uses it too. (owner — Q2 of the quick tools run failed only on "2." and "3.")
D264: The number check reads digits with thousands separators as one number ("113,590" is 113590), in the text and in the block, so it matches either form. "7,9" (not three digits after the comma) stays two numbers. Shared check. (owner — Q7 failed on a correctly copied 113590)
D265: Tools eval only: when an answer called no tool, its number check is skipped (shown "-", counted as passing); the names check still runs. Known gap, written down: an invented number in a no-tool answer is not caught; the path check covers questions that need a tool. Replaces D260's known gap. (owner — Q10's Bench Boost answer can only be general knowledge)
D266: With more than one player, get_players also prints the price gap: "Price: Palmer costs most at 9.7m; Groß 3.8m less." Gaps are subtracted in tenths, so they are exact; a level price reads "level with <dearest>"; ties go by lower id. The description says it gives who costs more and by how much. Extends D248. (owner — Q4 computed "3.8m more" itself)

Check (no model calls): on all 60 texts in the five saved writing results, the old and new number checks give the same verdict. One saved row (fcf41b2 example_c 3) differs from today's verdict under both, because D199 added the net gain 6.8 to the block after that run.

## Owner decisions after the first full tools run (2026-10-07)

D267: find_replacements prints the hit size with its bar on each row ("worth a 4-point hit, bar 8: yes", from HIT_COST and MIN_HIT_GAIN) and the number of options returned on its first line ("..., selling price 6.9m, 5 options"; "1 option" singular; the count is the rows shown, at most TOP_REPLACEMENTS). (owner — the full run failed Q5 twice on "top 5" and "−4 hit", numbers the tool knew but did not print)
D268: The tools eval's number and name checks pass at 27 of 30 runs (9 of 10 for --quick), the same bar as the path check (PASS_ANSWERS = 0.9; replaces "every answer"). Reason: counts and standard rule numbers fail the check without being invented, and the report lists every failing number with its sentence (D262), so the owner judges the few that remain. (owner)
