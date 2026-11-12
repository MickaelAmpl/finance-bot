# SDD ledger — plan: stages/03_plan/output/phase1-1-fixes-plan-2026-11-01.md

Spec: stages/02_spec/output/spec-2026-10-31.md (this plan is newer where it changes copy or commands). Base before Task 1: 5dc1cf6.

## Pre-flight scan

| Pair / task | Produces vs consumes | Finding |
|---|---|---|
| T1 / T2 | T1 adds `texts._entry_line`; T2 uses it for the record view | Order T1 before T2. OK |
| T1 / T3 | both edit texts.py and handlers.py (T1 on_rate, T3 on_goal/on_savings) | Different functions; sequential. OK |
| T2 / T3 | both edit test_bot.py | Sequential. OK |
| T3 / T4 | T4 HELP and menu copy name the `/goal ... 12.2027` syntax that T3 adds | Order T3 before T4. OK |
| T1 self | set_rate return type changes; callers: handlers.on_rate, tests (test_rates count asserts, test_export ignores return) | Plan says update callers. OK |
| T2 self | old buttons e:cat/e:del must keep working | Stated in task and constraints. OK |
| T3 self | migration on a live v1 database | Test on a v1 database with data required. OK |
| T4 self | startup handler must not stop the bot on a menu error | Stated. OK |

Ruling: picking a category from the record view shows the saved reply with Change category / Undo (no Back) — simplest, Misha's flow still works — cost if wrong: one more small change.

## Task 1
Base eb98db5, commit 7bf752f (developer haiku). Gate re-run by controller: ruff clean, 38 formatted, pyright 0, pytest 380 passed. Review: two-axis dispatched.
Review (two-axis, Sonnet): Standards no hard violations; smells: repeated signed(...), eur_cents-is-None vs pending, magic 5, assert in _converted_line, N+1 get_record. Spec: all copy and set_rate match; ambiguity "oldest first" vs id order.
Ruling: "oldest first" = entry (id) order, as implemented — matches /last order — cost if wrong: sort by date, one line.
Ruling: keep the assert in _converted_line (set_rate commits before get_record) and the N+1 get_record (single user, at most a few pending) — cost if wrong: none in practice.
Fix round 1 (same developer): r.pending, _MAX_LISTED, tests for 5/6 boundary and foreign income sign in /last.
Gate note: .venv has no pyright; the global `pyright` from app/ is the gate's pyright (as in phase 1).
Fix round 1: ef5b6a7 (texts.py, test_texts.py). Controller re-review of the diff: matches the round; gate ruff clean, pyright 0, pytest 383 passed.
Task 1: complete (7bf752f, ef5b6a7)

## Task 2
Base ef5b6a7. Ruling: the plan example "3. Emergency pot +200.00 EUR" is a typo; the button uses _label unchanged ("emergency pot"). Ruling: _entry_line becomes public entry_line for the record view (no wrapper).
Developer (sonnet): 1ee7891. Controller gate: ruff clean, pyright 0, pytest 403 passed. Two-axis review dispatched.
Review (two-axis, Sonnet): Spec all 7 met. Standards no hard violations; smells: private texts imports in keyboards, duplicated list view, back_keyboard chain, inconsistent gone-entry toasts, tautological test; 9/10 mutants killed (1 equivalent).
Ruling: gone-entry toast "Already deleted." for del/cat/pick (undo keeps "Nothing to undo.") — the record view makes Delete a main path, the old reply was wrong for it — cost if wrong: one string.
Ruling: keep entry_keyboard/record_keyboard names and the action switch in on_delete_entry — cosmetic — cost: none.
Fix round 1 (same developer): last_button_text in texts (+rstrip), _last_view, _back_button, gone-entry toasts, drop tautological test and docstring.
Fix round 1: 0e3c120. Controller re-review of the diff: matches the round; gate ruff clean, pyright 0, pytest 406 passed.
Task 2: complete (1ee7891, 0e3c120)

## Task 3
Base 0e3c120.
Developer (sonnet): 7e988e5. Controller gate: ruff clean, pyright 0, pytest 439 passed. Controller check on a copy of the live server DB (v1, 10 entries, 1 pot): connect twice -> v2, 10 entries, pot intact with goal_month NULL; goal 10000 by 2027-12 with 150.00 saved -> "703.58 EUR a month" (9850/14 rounded up). Two-axis review dispatched.
Review (two-axis, Sonnet): Spec all 5 met, copy exact, edge cases verified. Standards no hard violations; migration one transaction, idempotent, old code works on v2 (checked by reviewer). Smells: migration race bot vs daily job, goal arithmetic in texts.py, today() called 3x, string month parsed in several places; test gaps: half-way failure, 03.2027.
Ruling: goal_month stays "YYYY-MM" text (plan) — cost: none. Ruling: monthly amount rounds UP, a plan-sanctioned exception to ROUND_HALF_UP (you reach the goal on time) — cost: none. Ruling: "goal reached" wins over "has passed".
Fix round 1 (same developer): BEGIN IMMEDIATE + re-check for 1->2, months_left/monthly_cents in savings.py, today() once, tests for half-way failure and 03.2027, schema.sql version comment.
Fix round 1: 4174f46. Controller re-review: db.py BEGIN IMMEDIATE + re-check inside with conn; gate ruff clean, pyright 0, pytest 453 passed x3 (threaded lock test stable); live-DB copy migrates to v2 with 10 entries and the pot intact.
Task 3: complete (7e988e5, 4174f46)

## Task 4
Base 4174f46.
Developer (haiku): 546325f. Controller review of the small diff: BOT_COMMANDS and HELP copy match the plan character by character; startup handler registered; aiogram 3.31 start_polling calls emit_startup(bot=...) (dispatcher.py:596); TelegramAPIError caught and logged. HELP drops the "/undo /last /savings /goal /export" line as the plan says (Menu covers them). Trailer says Haiku (accurate), not amended. Gate: ruff clean, pyright 0, pytest 455 passed.
Task 4: complete (546325f)

## Final whole-branch review
Range eb98db5..546325f (Opus).
Final review (Opus): Critical none. Important: deleting a save after a take makes a pot negative (old known item 3, now one tap away in the record view and feeding the monthly amount). Minor: pot reply has no date; stale goal_month after a code rollback; R13 backdated entry vs today's rate (known item 5); menu call can delay start 60 s. Test gaps on cross-task paths.
Ruling: fix the negative pot now (guard on delete of a save) — Task 2 made it one tap away and Task 3 builds on the total; small, reversible — cost if wrong: Misha cannot delete such a save until he deletes the take first. Ruling: dated pot reply (same intent as Task 1). Ruling: request_timeout=10 on the menu call. Not fixed: rollback note goes to the release record; R13 stays a known item for Misha.
ONE fix dispatch: final-fix-brief.md (fresh Sonnet developer).
Final fix: aaf9e4e (fresh Sonnet developer). Controller scoped re-review of the diff: delete_entry check + soft delete in one `with conn:`, refusal raises SavingsError, /undo answers it, callbacks toast it without editing; pot_text dated; request_timeout=10. Gate: ruff clean, pyright 0, pytest 472 passed.
Controller smoke run on a copy of the live server DB (scratchpad/accept/smoke.py): migrates to v2; menu has 8 commands; "Saved 31.10: ..."; USD entry shows "(≈ -36.80 EUR at 0.92)"; "Emergency pot 28.10: +50.00 EUR · total 200.00 EUR"; /last one button per entry; open -> view with Delete / Back to list (pot move, no category); back restores the list; /goal ... 12.2027 -> "by 12.2027: 700.00 EUR a month"; /help new lines.
Phase 1.1 build: complete. Commits 7bf752f ef5b6a7 1ee7891 0e3c120 7e988e5 4174f46 546325f aaf9e4e. Next: Misha's deploy approval.
