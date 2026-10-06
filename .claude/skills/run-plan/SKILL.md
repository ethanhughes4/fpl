---
description: Builds a whole stage plan, wave by wave. Steps in the same wave are built at the same time, then joined.
argument-hint: "[stage-name]"
disable-model-invocation: true
---

Build docs/prd/$0-plan.md from start to finish.

Before starting: run git status. If anything is uncommitted, stop
and ask the user to commit first.

Repeat for each wave, in order, until no step is TODO:

1. List the TODO steps in the lowest unfinished wave.
2. Start one builder agent per step, all in the same message so
   they run together. Give each the plan path, the decisions path
   and its step number.
3. Wait for all of them.
4. Join the branches one at a time, in step order:
   a. git merge <branch>
   b. If the only conflict is in the shared list the plan names
      (each branch added one line), keep every line, in the order
      the plan gives, and finish the merge.
   c. Run python -m pytest -q.
5. Mark the steps DONE in the plan file and commit "Wave <n> done".
6. Go straight on to the next wave. Do not wait for the user.

Stop and tell the user only if:
- a builder reports something unclear,
- a merge conflicts anywhere other than the shared list
  (run git merge --abort first),
- tests fail after a merge.

When every step is DONE, show the user the final brief, list the
choices the builders made, and ask them to check it against the
FPL site.