# Roadmap

Decisions for each stage live in docs/prd/stage-N-decisions.md.

1. Brief: captain, eleven, transfers, warnings from the FPL feed. Built.
2. Evals for the scoring (replay finished gameweeks). Built.
3. Plain-English explanation written by a model, checked by code. Built.
4. Local MCP server: ask Claude about the team in plain English; Claude
   calls tools that run the existing code. Read-only, no new scoring. Built.
5. A React page on this PC that shows the weekly brief (D270, D283).
6. Chips, price changes, mini-league rivals and outside news.
7. Scheduled brief before each gameweek's deadline (moved from stage 5, D283).

The app never makes transfers itself, in any stage.
