---
description: Builds a whole stage plan, wave by wave. Steps in the same wave are built at the same time, then joined. Open questions go to the resolver.
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
5. If any builder reported something under BLOCKED, or made a
   claim about an outside rule or data format, send those points
   to the resolver agent with the decisions path. Then:
   - For each answer, add a line to the decisions file:
     D<number>: <answer> (resolver; evidence: <source>)
   - If the answer makes built code wrong, fix it, add a test for
     it, and run the tests.
   - Collect every ESCALATE for the user.
6. Mark the steps DONE in the plan file and commit "Wave <n> done".
7. If there are ESCALATE items, stop and ask the user. Otherwise
   go straight on to the next wave.

Also stop and tell the user if:
- a merge conflicts anywhere other than the shared list
  (run git merge --abort first),
- tests still fail after one attempt to fix them.

When every step is DONE, show the user the final brief, then list
every decision the resolver added, with its evidence, so the user
can check them.