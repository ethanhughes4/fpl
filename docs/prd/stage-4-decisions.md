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
