---
paths:
  - "web/**"
---

# The web page (stage 5, D312)

- No calculations. The page never works out, rounds or compares a score, price or count.
  Python writes every number and sentence as ready-to-show text (D278, D289). The one
  exception is comparing the deadline with the clock for the banner (D300).
- Show numbers exactly as the file gives them. Never format, add a unit or convert.
- Colours only from the CSS variables in web/src/theme.css. No hex, rgb or named
  colours anywhere else.
- Every component has a test next to it (`<Name>.test.tsx`), using the sample from
  `src/sample.ts`. Tests never call the live feed or run claude.
- The page never fetches anything except `/brief.json`.
- A new field: add it to Python's part, to web/src/brief.ts (one field per line, no `?`,
  `null` for no value), then run `python -m tests.make_sample`.
- Tests: `npm test` in web/ (type check, then Vitest).
