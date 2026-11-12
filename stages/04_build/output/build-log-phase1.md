# Build log - phase 1

Status: complete 31.10.2026 - all 15 tasks built and reviewed; QA (stage 05) next on Misha's word.

Plan: `../../03_plan/output/phase1-implementation-plan-2026-10-31.md`. Spec: `../../02_spec/output/spec-2026-10-31.md`.
Base commit: `adf53db` (chore: workspace before phase 1 build), 31.10.2026.
Review per task: `two-axis-review` (Standards + Spec, Sonnet sub-agents). Developers: Haiku (`.claude/agents/developer.md`).

## Product-owner rulings made before the build

Ambiguities in the plan, decided inside the approved scope (spec is the authority):

1. Wrong first word: no digits -> "Start with the amount"; starts like a number but invalid -> "Amount must be like 25 or 12,50".
2. Split-number error stays the exact plan text "Write 1200 without spaces, e.g. 1200 taxi".
3. Tasks 7 and 8 run in parallel, so their tests set up each other's data with plain SQL.
4. Month report: pending (no-rate) entries are left out of totals, categories and Top 5; only their count is shown.
5. Rates are shown exactly as typed (`0.022` stays `0.022`, `0.0220` stays `0.0220`).
6. Wave 6: Task 13 runs after Task 12 (its tests need the mocked bot from Task 12).
7. Task 14: both entry points read settings with the same one-line expression; `config.py` is not changed.

For QA: an entry in USD/UAH dated before the very first rate stays pending until the next `/rate` (spec R13 taken literally).

## Tasks

| Task | Date | Commit | Tests (ruff, format, pytest) | Review | Deviations |
|---|---|---|---|---|---|
| 1 Scaffold and config | 31.10.2026 | `bb0f068`, fix `f8ee146` | ruff clean, format clean, pytest 9 passed, no warnings; pyright 0 errors | Standards: 1 hard (pytest warning) fixed, 1 judgement (error example) fixed; Spec: compliant | Added pytest loop-scope setting and pyright venv setting to `pyproject.toml` (ruling: plan list is a minimum); 4 extra config tests. Pins: pytest 9.2.0, pytest-asyncio 1.4.1, ruff 0.17.3 |
| 2 Money | 31.10.2026 | `0dece57` | ruff clean, format clean, pytest 26 passed (17 money); pyright 0 errors | Standards: 0 hard, 6 judgement; Spec: compliant | `re.fullmatch` instead of `^...$` (rejects a trailing newline) |
| 4 Database | 31.10.2026 | `8e94544` | ruff clean, format clean, pytest 37 passed (11 db); pyright 0 errors | Standards: 2 hard ruled acceptable (schema text inserted into the setup script is the packaged file, not user input; report length), 5 judgement; Spec: compliant | Schema and version set in one transaction; 4 extra tests (WAL, row access, parent folder, rollback) |
| 5 Categories | 31.10.2026 | `28727da` | ruff clean, format clean, pytest 8 categories tests, 67 on combined tree; pyright 0 errors | Standards: 0 hard in code (report length ruled a nit), 4 judgement; Spec: compliant | Unknown category id raises a clear error (ruling); 1 extra test |
| 6 Exchange rates | 31.10.2026 | `73bc672` | ruff clean, format clean, pytest 22 rates tests, 67 on combined tree; pyright 0 errors | Standards: 0 hard, 6 judgement; Spec: compliant | Rate and conversions saved in one transaction (all or nothing); ASCII digits only; extra tests for tie-break, stored text, rollback |
| 3 Entry parser | 31.10.2026 | `cd6f503`, fix `cc93fbf` | ruff clean, format clean, pytest 77 parser tests, 144 overall; pyright 0 errors | Standards: 2 process items, 9 judgement (full-text message tests and comments added); Spec: 1 important fixed (`1 200,50 taxi` was saved as 1.00) | Rulings: any number-like first word after the amount is a split number; pot names need a letter; dates only as `DD.MM` / `DD.MM.YYYY` with two-digit day and month, other date-like endings (`1.5`, `28.10.26`) are rejected instead of guessed |
| 8 Ledger | 31.10.2026 | `8d19db1` | ruff clean, format clean, pytest 14 ledger tests, 171 on combined tree; pyright 0 errors | Standards: 2 process items (report length; evidence covered by the wave check), 8 judgement; Spec: compliant | Saving a pot move through the expense path is refused with a clear error; extra tests for income, missing ids, undo of a pot move |
| 7 Savings pots | 31.10.2026 | `b3984c5`, fix `30d8fc4` | ruff clean, format clean, pytest 19 savings tests, 177 overall; pyright 0 errors | Standards: 1 process item, 8 judgement; Spec: 1 important fixed (pot names were case-sensitive, spec R15) | Pot names are always stored and looked up in lowercase; a non-pot entry is refused with a clear error |
| 10 CSV export | 31.10.2026 | `a449197`, test `dcc7b89` | ruff clean, format clean, pytest 2 export tests, 206 overall; pyright 0 errors | Standards: 0 hard, 4 judgement; Spec: compliant | Added a test for the rate column and a pending entry converted later (ruling: an unverified money column is a gap) |
| 11 Reply texts | 31.10.2026 | `9834eaf` | ruff clean, format clean, pytest 27 texts tests, 205 overall; pyright 0 errors | Standards: report length nit, 6 judgement; Spec: compliant, no findings | Help text wording written by the developer around the 8 examples the plan names |
| 9 Month report | 31.10.2026 | `0f497da`, fix `71debd8` | ruff clean, format clean, pytest 26 report tests, 232 overall; pyright 0 errors | Standards: 2 process items, 9 judgement (named widths, extra tests added); Spec: 1 important fixed (a month with only a save and an equal take showed "No entries.") | Golden text exact. Report carries an entry count (small interface addition, ruling); empty blocks are omitted; equal spending shows "▲ 0%"; bad `/month` argument answers "Use a month like /month 10 or /month 2026-10" |
| 13 Daily backup and monthly summary | 31.10.2026 | `1efdd4f`, fix `83991c6` | ruff clean, format clean, pytest 10 jobs tests, 256 overall; pyright 0 errors | Standards: report length nit, judgement (retention fixed); Spec: compliant, Review Focus 3 covered (twice a day, missed day, failed send) | Old-backup cleanup only touches files named `finbot-YYYY-MM-DD.db`. Known: if the CSV send fails after the report text went out, the next run sends the text again (never a missing summary) |
| 12 Telegram layer | 31.10.2026 | `13314a1`, fixes `57edafc`, `093081e` | ruff clean, format clean, pytest 47 bot tests, 296 overall; pyright 0 errors (after `60f5e29`) | Standards: button could keep spinning on an unexpected error, unchanged-edit error unhandled, big test gaps - all fixed; Spec: compliant | Handlers are registered by `create_router()` instead of one shared router (aiogram refuses to attach one router twice; ruling). Pot moves reply without buttons. Every button press is answered on every path. Tests now cover every command, foreign users' and group button presses (nothing stored, nothing deleted) |
| 1 (follow-up) | 31.10.2026 | `60f5e29` | pyright 0 errors on the whole tree | checked by the product owner (one config line) | `pythonVersion = "3.12"` for pyright |
| 15 Deploy kit | 31.10.2026 | `7b96171`, fix `19b0c47` | ruff clean, format clean, pytest 9 deploy tests, 302 overall; `bash -n` ok; dry run simulated with fake ssh/rsync, 0 calls | Standards: 1 hard fixed (the printed rollback command could delete the live database's journal when no backup existed); Spec: compliant | Not run against the server (needs Misha's approval). Bot service enabled at boot, daily job waits for network, backup copy private (600), status check waits 3 s. Rollback of code = deploy the previous commit again |
| 14 Runner with IPv4 session | 31.10.2026 | `c149c0a`, fix `c19d60b` | ruff clean, format clean, pytest 6 runner tests, 304 overall; pyright 0 errors | Standards: 1 hard fixed (on a network error the bot token could land in the server log; now masked as `***` everywhere); Spec: compliant | IPv4 through aiogram's connector settings; both entry points read settings the same way; the bot logs a crash and exits so systemd restarts it. Real Telegram connection is first exercised at Misha's acceptance |
| Final review and fix | 31.10.2026 | `3f55a7c` | ruff clean, format clean, pytest 312 passed; pyright 0 errors | Closing whole-branch review (Opus): ready for QA with 3 fixes, all fixed and re-reviewed | A currency typed after the note (`1200 taxi uah`) is rejected instead of silently saved as EUR; a pot with no remaining moves is hidden; both services create files readable only by the bot (UMask 0077) |

## Final state

- Head `3f55a7c`, 27 commits since `adf53db`. Whole `app/`: `ruff check` all passed, `ruff format --check` 38 files formatted, `pytest -q` 312 passed, `pyright` 0 errors, both entry points import, `bash -n deploy/deploy.sh` ok. Nothing pushed, nothing deployed, `app/.env` never read.
- Every task: Haiku developer, test first, then `two-axis-review` (Standards + Spec, Sonnet). Fix rounds: tasks 1 (2 rounds), 3, 7, 9, 10, 12 (2 rounds), 13, 14, 15; each closed by a scoped re-review. No task needed more than 2 rounds.
- Full ledger with every ruling, every deferred minor and the review history: `../references/sdd-ledger-phase1-2026-10-31.md`.

## Product-owner rulings made during the build (beyond the pre-build list)

8. Dates: only `DD.MM` / `DD.MM.YYYY` with two-digit day and month count as a date; other date-like endings (`1.5`, `5.11`, `28.10.26`) get the date error instead of a guess (spec R6).
9. Split numbers: any number-like first word after the amount (`1 200,50`, `1 200€`) is rejected (spec R7, Review Focus 1). Pot names must contain a letter.
10. Pot names are case-insensitive everywhere (spec R15); pots with no remaining moves are hidden.
11. Month report carries an entry count so "No entries." means really no entries; equal spending shows "▲ 0%"; empty blocks are omitted.
12. Telegram layer: `create_router()` instead of one shared router (aiogram limit); pot moves reply without buttons; every button press is answered; plain text everywhere except `/month`.
13. Daily job: old-backup cleanup only touches `finbot-YYYY-MM-DD.db` files; a failed send is retried next day (the report text may come twice, never zero times).
14. Deploy kit: bot service enabled at boot; rollback command printed only when a database backup exists; files private (600).
15. Security: the bot token is masked as `***` in every log line.
16. A currency typed after the note is rejected with "Put the currency right after the amount, e.g. 1200 uah taxi".
17. Tooling: pyright told the Python version (3.12); pytest warnings removed.

Known and left for QA / Misha: see `HANDOFF.md`, section "For QA and Misha".

## QA fix set (stage 05 findings, approved by Misha 31.10.2026)

| Fix | Commit | Tests | Review | What changed for Misha |
|---|---|---|---|---|
| C tests | `961dc11` | 4 new tests, each kills its mutation | two-axis: clean | none (safety net) |
| A parser | `40b0d37` | parser 107 tests | two-axis: clean; side effect ruled (a lone future date is no longer a note) | note up to 100 characters, pot name up to 30, future dates rejected, `29.02` works |
| B rates and bot | `6a0c722` | rates + bot 96 tests | two-axis: clean, ~20 mutations caught | a rate outside USD 0.5-2 / UAH 0.005-0.1 EUR is refused; `/goal 200 5000` gets the usage hint; buttons tested by pressing them |
| D deploy | `5fd69bd`, test `3066382` | deploy 12 tests; simulated with fake server tools | two-axis: one hollow test fixed | deploy fails if the bot crash-loops; rollback line only when the database was touched; `.env` must be private; more secrets ignored by git |
| E leftovers | `fa769f4` | 372 overall | checked by the product owner by mutation | `/goal` with a too-long pot name gets the usage hint |

Gate at `fa769f4`: ruff clean, format clean, pytest 372 passed, pyright 0 errors.

## Phase 1.1: acceptance fixes (01.11.2026)

Plan: `stages/03_plan/output/phase1-1-fixes-plan-2026-11-01.md` (Misha: "1 - по рекомендации 2 - делаем вмесет с доработками"). Ledger with every review and ruling: `stages/04_build/references/sdd-ledger-phase1-1-2026-11-01.md`. Same process as phase 1: one developer per task, two-axis review per task (Task 4 small diff reviewed by the controller), fix rounds back to the same developer, one closing Opus review, one fix dispatch.

| Task | Commits | Developer | Result |
|---|---|---|---|
| 1 Dates in replies, EUR in /last, clear /rate reply | 7bf752f, ef5b6a7 | Haiku | 383 tests |
| 2 /last one button per entry, record view, back | 1ee7891, 0e3c120 | Sonnet | 406 tests |
| 3 Goal deadline, migration 1 -> 2 under BEGIN IMMEDIATE | 7e988e5, 4174f46 | Sonnet | 453 tests; live-DB copy migrates with data intact |
| 4 Telegram menu, help | 546325f | Haiku | 455 tests |
| Closing review fix: pot never below zero on delete, dated pot replies, menu timeout, cross-task tests | aaf9e4e | Sonnet | 472 tests |

Final gate at aaf9e4e: ruff clean, 38 files formatted, pyright 0 errors, pytest 472 passed. Smoke run of the real dispatcher on a copy of the live server database: every new reply and button as planned (ledger, last section).

## Phase 1.2: categories, budgets, clear month (01.11.2026)

Plan: `stages/03_plan/output/phase1-2-plan-2026-11-01.md` (Misha: "2 - на сейчас да ок 3 - да"). Ledger: `stages/04_build/references/sdd-ledger-phase1-2-2026-11-01.md`. Same process: one developer per task, two-axis review (Task 4 small diff by the controller), fix rounds, one closing Opus review, one fix dispatch.

| Task | Commits | Developer | Result |
|---|---|---|---|
| 1 Add and rename categories | 0866fe6, 74da0b2 | Sonnet | 586 tests |
| 2 Monthly budgets, migration 2 -> 3 | d79c096, 2814583 | Sonnet | 678 tests |
| 3 /clear a month after confirmation (pinned to the shown set) | 129e8d4, 7883830 | Sonnet | 727 tests |
| 4 Menu and help | b6b8153 | Haiku | 727 tests |
| Closing review fix: long reports split, /clear warns about /undo, reserved "Uncategorized", help order, cross-task tests | e732645 | Sonnet | 753 tests |

Final gate at e732645: ruff clean, 40 files formatted, pyright 0 errors, pytest 753 passed. Smoke run of the real dispatcher on a copy of the cleaned live database: as planned (ledger, last section).

## Phase 1.3 (01.11.2026)

Plan `stages/03_plan/output/phase1-3-plan-2026-11-01.md` (Misha: "Да давай на все ок. Стартуй"). Ledger `stages/04_build/references/sdd-ledger-phase1-3-2026-11-01.md`.

| Task | Commits | Developer | Tests |
|---|---|---|---|
| 1 Several entries in one message (one per line or comma-separated; nothing saved if any part fails; replies after all saves; retry once after 429) | 1ea6923, 02817fe | Sonnet | 813 tests |

Two-axis review (Standards + Spec, Sonnet) found: the save/take comma rule split "25 coffee, take away"; an empty part after a leading comma; trailing commas in notes; no retry after 429 (telegram-rules); the too-many text had no hint. All fixed in 02817fe. Accepted: a note on two lines is now refused loudly.

Final gate at 02817fe: ruff clean, 40 files formatted, pyright 0 errors, pytest 813 passed. Smoke run of the real dispatcher on a fresh copy of the server database (version 3): three lines -> 3 entries, Russian comma form -> 3, pot move + expense, a failing take mid-list leaves the others saved, all review cases as ruled.

## Phase 1.4: AI input (12.11.2026)

Spec `stages/02_spec/output/spec-ai-input-v2-2026-11-01.md` (approved 12.11, "утверждаю", recommended answers on [Q1]-[Q6]). Plan `stages/03_plan/output/phase1-4-plan-2026-11-12.md` (9 tasks, 4 waves). Ledger `stages/04_build/references/sdd-ledger-phase1-4-2026-11-12.md`. Same process: one Haiku developer per task (parallel inside a wave, pathspec commits), a two-axis review (Standards + Spec, two Sonnet sub-agents) per task, one fix round back to the same developer, one closing Opus review. No real model call: every test runs the real anthropic SDK over `httpx2.MockTransport`; tests block the network.

| Task | Commits | Result |
|---|---|---|
| 1 Optional key, all secrets masked in logs, network blocked in tests, fake Anthropic client | 086a551, 1254b0a | longest-first masking, stack_info, getaddrinfo guard added in review |
| 2 Drafts table (DB 3 -> 4), all-or-nothing Save | 086f44a, d64c8e2 | ISO-week dates (`2026-W44-1`) refused after review; create_draft under the write lock |
| 3 Tool schemas (strict) and read-only money tools | 7ac74e0, 91833ec | bad model arguments return tool errors instead of raising |
| 4 System prompt, memory, parser-first routing | bd846bf, 95b55c6 | locale-free weekday; verbatim prompt test |
| 5 Draft texts, Save/Cancel buttons, AI help lines | 3aca233, 97005c9 | help built from parts |
| 6 Model turn: tool loop, failures, daily cap, usage log | 8b364c8, 91ce561 | empty tool_use stop handled; no-leak log tests made real |
| 7 Bot wiring: free text, photos, Save, Cancel | fd6b10f, aa33344 | Telegram failure paths hardened (edits, 429, draft send, catch-all); album order |
| 9 Live-run script for the pre-deploy check | cadc13d, f31970f | refuses the live DB and existing files; memory like the bot |
| 8 Startup and deploy | 01cb65c | `AI input: on/off`, SDK loggers at WARNING, `AI key: present/missing` |

Gate at 01cb65c: ruff clean, 60 files formatted, pyright 0 errors, pytest 1063 passed (813 before the phase).

Closing Opus review: no blockers; 3 majors fixed in dda1f38 (slash commands never go to the AI; a correction replaces only the one live draft, otherwise the new draft says why; startup log forced), image-size finding disproved by the official vision docs (10 MB base64 limit). Gate at dda1f38: ruff clean, 60 files formatted, pyright 0 errors, pytest 1077 passed.
