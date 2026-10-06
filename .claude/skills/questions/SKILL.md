---
description: Questions the user in depth about a planned stage until every decision is settled, and records each decision. Use before writing requirements or building.
argument-hint: "[stage-name]"
disable-model-invocation: true
---

Question the user in depth about: $ARGUMENTS

Your job is to reach full agreement on what will be built. You
are not here to be agreeable. You are here to find every gap.

## Before asking anything

1. Read CLAUDE.md, every file in docs/, and the code this stage
   will build on.
2. Create docs/prd/$0-decisions.md if it does not exist. If it
   exists, read it and continue from where it stopped.

## How to ask

- Ask ONE question at a time. Wait for the answer.
- Give your recommended answer with every question, and one
  sentence on why.
- Never ask something you can find out by reading the code or
  docs. Look it up and state what you found.
- Use plain words. Explain each technical term the first time.
- If an answer is vague, do not accept it. Ask for a number, an
  example, or a yes or no.
- If an answer conflicts with an earlier decision, say so and
  ask which one stands.
- If the user says "I don't know", explain the options and
  their trade-offs, then ask again.

## What to cover

Work through these in order. Each answer may open follow-up
questions. Finish all follow-ups before moving on.

1. Purpose: who uses this, and what can they do afterwards?
   List every kind of user and every thing each one wants to do.
2. Examples: at least three real inputs with the exact output
   the user expects for each.
3. Boundaries: what is deliberately left out?
4. Behaviour when things go wrong: missing data, a failed
   lookup, a question it cannot answer.
5. Where every number in an answer comes from.
6. Technical choices: libraries, models, cost limits.
7. How we will prove it works: which tests, which checks.
8. Which parts the user wants to write himself, to learn.

## Recording

After every answer, add a line to the decisions file:
  D<number>: <the decision> (reason: <why>)
Mark anything the user was unsure about as ASSUMPTION.

## Finishing

When you have no questions left, read the full decision list
back to the user and ask: "Is anything missing or wrong?"
Keep going until the user confirms. Do not write code. Do not
write the requirements document.