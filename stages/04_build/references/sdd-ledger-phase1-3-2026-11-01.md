# SDD ledger — plan: stages/03_plan/output/phase1-3-plan-2026-11-01.md

BASE cc5a3fc

Task 1: implementer DONE_WITH_CONCERNS, commit 1ea6923, 797 passed (Sonnet developer; trailer says Sonnet 5.5, truthful, left as is).
Controller smoke on a copy of the server DB (v3): three lines -> 3 entries; Russian comma form -> 3; word-first refused; one entry unchanged; pot + expense; take too much mid-list -> "Entry 2 not saved: ..."; 11 entries refused; HELP line in place.
Two-axis review: Standards 2 documented findings (TOO_MANY_MSG has no example; telegram-rules "429 ... wait and retry once" missing in the new send loop) + smells. Spec: save/take rule splits "25 coffee, take away"; leading comma gives empty Entry 1; trailing commas stay in notes; a newline inside a note now refused.
Ruling: narrow the comma rule to save/take followed by an amount — pot moves always have one (spec R15) — cost if wrong: "30 internet, save emergency 200" saves as one expense, visible in the reply.
Ruling: skip empty parts — restores today's error for ", 25 coffee" — none.
Ruling: strip trailing commas from parts in the multi-entry path only (one-entry path keeps the original text) — cosmetic notes — none.
Ruling: retry a reply once after TelegramRetryAfter in the send loop (telegram-rules.md) — the burst loop is the first code that can hit it — a second 429 still raises, entries already saved.
Ruling: TOO_MANY_MSG built from MAX_ENTRIES and says what to do: "Up to 10 entries in one message. Nothing saved: send them in two messages." — engineering rule "example of correct input" — none.
Ruling: a newline inside a note is now refused loudly ("Nothing saved. Entry 2 ...") — accepted, added to Known risk — Misha retypes on one line.
Ruling: keyword "coffee," from "25 coffee, croissant" is pre-existing one-entry behaviour — not changed.
Fix round 1: dispatched to the same developer.
Fix round 1: commit 02817fe, 813 passed. Controller re-review of the fix diff: all six rulings applied; gate green (ruff, format, pyright 0, 813 passed). Smoke on a fresh copy of the server DB: "25 coffee, take away" one entry; ", 25 coffee" plain start error; trailing commas stripped; note on two lines refused loudly; 11 entries text updated.
Ruling: no separate closing whole-branch review — the phase is this one task, the two-axis review covered the whole phase diff (cc5a3fc..1ea6923) and the fix diff was re-reviewed by the controller — cost if wrong: a cross-module issue slips to Misha's acceptance; the change touches one handler and the parser only.
Task 1: complete (1ea6923, 02817fe).
