# SDD ledger — plan: stages/03_plan/output/phase1-2-plan-2026-11-01.md

Spec: stages/02_spec/output/spec-2026-10-31.md (budgets and custom categories were backlog there; this plan is newer). Base before Task 1: see Task 1 line.

## Pre-flight scan

| Pair / task | Produces vs consumes | Finding |
|---|---|---|
| T1 / T2 | T1 adds categories.find_category; T2 matches the budget category with it | Order T1 before T2. OK |
| T1 / T2 / T3 | all edit texts.py, handlers.py, test_bot.py, test_texts.py | Different functions; sequential. OK |
| T2 / T3 | T3 clears expenses that T2's spent sums read; T2 counts only non-deleted | Consistent. OK |
| T1-T3 / T4 | T4 menu and help name commands from T1-T3 | Order last. OK |
| T2 self | migration 2 -> 3 on the live DB (version 2, real data) | Locked re-check pattern required; test on a v2 DB. OK |
| T3 self | confirm compares the count to avoid deleting more than shown | Stated. OK |

Ruling: categories cannot be deleted in this phase (entries refer to them) — cost if wrong: a later small task.

## Task 1
Base 028bcf9.
Developer (sonnet): 0866fe6. Controller gate: ruff clean, pyright 0, pytest 553 passed. Developer choices: rename to own name in another case allowed; "/category add Income" alone is usage; longest match leaving no new name gives usage; inner spaces collapsed. Two-axis review dispatched.
Review (two-axis, Sonnet): Spec all 6 met, developer choices accepted. Standards no hard violations; smells: domain rules in the handler (unlike SavingsError), count by loading rows, zero-width look-alike names, unbounded echo of the typed word.
Ruling: keep "/category add Income tax" -> income "tax"; on_goal keeps its own pot-name check; category buttons show the full name (max 30).
Fix round 1 (same developer): CategoryError in categories.py with the checks, NFC + strip Cf, echo cut to 30.
Fix round 1: 74da0b2. Controller re-review: CategoryError with checks in categories.py, COUNT(*), _clean_name (Cf removed, NFC, spaces); gate ruff clean, pyright 0, pytest 586 passed. Note: removing all Cf also drops ZWJ/ZWNJ (emoji sequences, some scripts) - accepted, Misha writes Russian/English.
Task 1: complete (0866fe6, 74da0b2)

## Task 2
Base 74da0b2.
Developer (sonnet): d79c096. Controller gate: ruff clean, pyright 0, pytest 676 passed. Developer choices: formatter in reports.py (import cycle), Budgets block before Top expenses, already-over budget set reply, any zero removes, "/budget Rent" usage. Two-axis review dispatched.
Review (two-axis, Sonnet): Spec all 7 met (edge cases run on scratch data), developer choices accepted. Standards no hard violations; migration verified (v2 data intact, previous release works on v3). Smells: texts imports reports._MONTHS (cycle workaround), left/over branch duplicated, untested kind filter, failed-upgrade test fails before any write.
Ruling: plan error texts without examples stay (plan wording). Ruling: /month over 4096 only with ~30 long-named budgets with 8-digit amounts — known item, not fixed. Ruling: empty month shows "No entries." even with budgets.
Fix round 1 (same developer): MONTHS + formatters public in texts.py, one left/over helper, tests for kind filter and post-CREATE failure, schema.sql comment.
Fix round 1: 2814583. Controller re-review: texts no longer imports reports (reports imports MONTHS, budget_line from texts); gate ruff clean, pyright 0, pytest 678 passed.
Task 2: complete (d79c096, 2814583)

## Task 3
Base 2814583.
Developer (sonnet): 129e8d4. Controller gate: ruff clean, pyright 0, pytest 711 passed. Developer flags: count-only check lets an old confirm button delete new entries if the count matches again (to fix: carry the max entry id at prompt time). Two-axis review dispatched.
Review (two-axis, Sonnet): Spec all 5 met, choices accepted. Standards/safety: count-only confirm reproduced (old button deletes unseen entries when the count matches again); recount outside the transaction; a 48 h+ old prompt deletes silently; forged month raises (nothing written). Mutation table: 9 checks all caught.
Ruling: pin the shown set with last_id + count, BEGIN IMMEDIATE, old prompt refused with "This question is too old. Send /clear again.", forged data ignored. Month-bounds duplication stays; /clear 13 keeps the /month error text.
Fix round 1 (same developer) dispatched.
Fix round 1: 7883830. Controller re-review: clearable_summary (count, max id), clear_month compares both under BEGIN IMMEDIATE, deletes id <= last_id; gate ruff clean, pyright 0, pytest 727 passed.
Task 3: complete (129e8d4, 7883830)

## Task 4
Base 7883830.
Developer (haiku): b6b8153. Controller review: BOT_COMMANDS 11 entries and HELP lines match the plan character by character; gate ruff clean, pyright 0, pytest 727 passed.
Task 4: complete (b6b8153)

## Final whole-branch review
Range 028bcf9..b6b8153 (Opus).
Final review (Opus): Critical none, Important none. Verified on scratch: migration race (4 processes x 15 trials), rollback to 028bcf9 on v3, rename+budget end to end, cleared entries' buttons, confirm pinning. Minor: /undo after /clear removes an unrelated entry; /month and the daily summary over 4096 reachable with ~30 budgeted categories (daily summary would then fail every day); "Uncategorized" name collides with the report label; HELP example order; budget line month has no year for an entry in another year. Test gaps on cross-task paths.
Ruling: fix 1-4 (split long reports as telegram-rules requires; clear reply warns about /undo; reserve "Uncategorized"; swap the two HELP lines) — small, reversible, safer; tell Misha the two copy changes. Not fixed: year in the budget line (edge case of the existing date rule).
ONE fix dispatch: final-fix-brief.md (fresh Sonnet developer).
Final fix: e732645 (fresh Sonnet developer). Controller scoped re-review: split_report (blank lines, then lines, then cut) used by /month and the daily summary; "Uncategorized" refused in is_valid_name; /clear result warns about /undo; HELP order. Note: as_pre escaping can add a few characters to a 4000-character piece (limit 4096) — fine unless a piece is full of & < >. Gate: ruff clean, pyright 0, pytest 753 passed.
Controller smoke run on a copy of the cleaned live DB (scratchpad/accept/smoke12.py): migrates to v3; menu 11 commands; /category add Rent; /budget Rent 850.00; new word "rent" -> pick Rent -> "Rent: 800.00 of 850.00 in November · 50.00 left"; second expense -> "over by 50.00"; /budget and /month Budgets block; /clear 2 entries -> deleted with the /undo warning; second press -> "changed since you asked"; budget back to 0.00.
Phase 1.2 build: complete. Commits 0866fe6 74da0b2 d79c096 2814583 129e8d4 7883830 b6b8153 e732645. Next: Misha's deploy approval.
