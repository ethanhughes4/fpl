---
description: Turns a finished decisions file into a requirements document for the builder.
argument-hint: "[stage-name]"
disable-model-invocation: true
---

Write the requirements document for: $ARGUMENTS

Do not interview the user. Everything you need should already
be in the decisions file. Your job is to organise it.

## Process

1. Read docs/prd/$0-decisions.md in full.
2. If any decision is unclear, or two decisions conflict, stop
   and tell the user to run /questions again. Do not guess.
3. Read CLAUDE.md, docs/, and the code this stage builds on.
   Use the project's own names for things throughout.
4. Work out where this stage will be tested. Prefer places
   that tests already use. Choose the highest level you can,
   and as few places as possible. Show these to the user and
   ask if they match what he expects. Wait for the answer.
5. Write docs/prd/$0.md using the template below.
6. Show the user a short summary and ask him to confirm.

## Rules for the document

- Every line must trace back to a decision. Put the decision
  number after it, like (D7). Add nothing that was not decided.
- Do NOT include file paths or code. They go out of date. Name
  the parts and how they connect instead.
- Use plain words. Explain each technical term the first time.

## Template

### Problem
The problem from the user's point of view. Two or three
sentences.

### Solution
What the user will be able to do when this stage is finished,
from the user's point of view.

### User stories
A long numbered list. Every behaviour gets its own line, in
this form:
  As a <who>, I want <what>, so that <why>.
Cover normal use, unusual use, and what the user sees when
something goes wrong.

### Examples
Real inputs with the exact expected output, copied from the
decisions file without changes.

### Implementation decisions
- The main parts that will be built or changed.
- What each part takes in and gives back.
- How the parts connect to each other and to the existing code.
- Libraries, models and cost limits.

### Testing decisions
- What a good test looks like here: check what the code does
  from the outside, not how it works inside.
- Which parts will be tested, at the places agreed in step 4.
- Which existing tests to copy the style of.

### Failure behaviour
What happens for missing data, a failed lookup, or a question
that cannot be answered.

### Out of scope
What this stage deliberately does not do.

### Assumptions
Every decision marked ASSUMPTION.

### Parts the owner writes himself
The parts the user chose to write, to learn.