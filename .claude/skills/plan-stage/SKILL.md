---
description: Turns a stage's decisions file into a step-by-step build plan, grouped into waves, and waits for approval. Use after /questions, before building.
argument-hint: "[stage-name]"
disable-model-invocation: true
---

Plan the build for: $ARGUMENTS

1. Read docs/prd/$0-decisions.md in full. If it does not exist, or
   any decision is unclear or conflicts with another, stop and tell
   the user to run /questions first. Do not guess.
2. Read CLAUDE.md and the existing code, so the plan fits what is
   already there.
3. Write the plan to docs/prd/$0-plan.md. Rules:
   - Every step is a vertical slice: it adds one thing the user
     can run and see, and passes through every part of the code it
     needs. No step is only setup, and no step builds one layer
     for later.
   - Step 1 is the thinnest path from start to finish that runs.
   - Step 1 also builds a skeleton where each later slice lives in
     its own file and is switched on by adding one line to a list.
     Later slices should add files, not rewrite shared ones.
   - Each step leaves the project working, with all tests passing.
   - Every step names what the user can do after it, the files it
     creates, the files it changes, the tests it adds, and the
     decision numbers it covers, like (D7).
   - Group the steps into waves. Steps in the same wave touch none
     of the same files, apart from that one list. Say which wave
     each step is in, and which earlier steps it depends on.
   - Every decision must appear in at least one step. List any
     that do not under UNCOVERED.
   - Each step has a status: TODO.
4. Show the plan and wait for approval. Do not write any code.

After approval, build one step at a time unless the user says to
run a wave in parallel. After each step: run the tests, mark the
step DONE in the plan file, say what changed in two or three
sentences, and stop until told to continue.