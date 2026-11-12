# SDD ledger — plan: stages/03_plan/output/phase1-implementation-plan-2026-10-31.md

Spec: stages/02_spec/output/spec-2026-10-31.md (binding). Base commit: adf53db (chore: workspace before phase 1 build).
Official build log for Misha/QA: stages/04_build/output/build-log-phase1.md.

## Pre-flight scan (31.10.2026)

### Per task: does its own text agree with itself

| Task | Check | Finding |
|---|---|---|
| 1 | tests vs Interfaces; files created vs used | consistent. pytest must import `finbot` from `app/` -> needs pythonpath config (implementation detail) |
| 2 | test values vs rules | consistent. Checked: 120000*0.0220=2640, 2500*0.92=2300, 1*0.5=0.5->1 (HALF_UP); "10000000" = MAX_CENTS accepted, "10000000.01" rejected |
| 3 | grammar vs tests vs error list | consistent. Ambiguity A1: which error for a bad first token ("coffee 25" vs "25.999 x"). Ambiguity A2: R7 message is a fixed example string |
| 4 | schema vs tests | consistent. CHECK pot_id/kind, amount>0 match tests |
| 5 | tests vs Interfaces | consistent |
| 6 | tests vs Interfaces | consistent. Observation O1 (not a conflict): a back-dated USD/UAH entry dated before the first-ever rate stays pending until the next /rate, per R13 literal |
| 7 | tests vs files | test "soft-deleted move excluded" needs a delete; `ledger.delete_entry` is Task 8 (same wave 4) -> A3 |
| 8 | tests vs files | test "records_between includes a pot move" needs a pot move; `savings.apply_pot_entry` is Task 7 (same wave 4) -> A4 |
| 9 | golden text vs render rules | consistent. Checked: 1850 vs 1745 = +6.02% -> 6%; pct 50/23/17/10; bars 12/5/4/2; label/amount padding. Ambiguity A5: `top` with pending records; A6: alignment of Top/Savings columns unspecified |
| 10 | expected bytes vs Interfaces | consistent |
| 11 | strings vs spec R11 | R11 shows rate `0.0220`, Task 12 shows `/rate uah 0.022` -> `0.022` -> A7 |
| 12 | behaviour vs tests | consistent. Risk R1: aiogram's tests/mocked_bot.py lives on GitHub (network may be unavailable) |
| 13 | tests vs files | consumes `tests/mocked_bot.py` from Task 12, same wave 6 -> A8 |
| 14 | Files vs behaviour | "Both entry points build settings the same way" but `config.py` not in Files -> A9 |
| 15 | tests vs Interfaces | consistent |

### Pairs sharing a file or an interface

| Pair | Produces -> consumes | Found |
|---|---|---|
| 1 -> 14 | load_settings, read_env_file, TZ | consistent |
| 2 -> 3 | parse_amount, SYMBOLS, CURRENCIES | consistent |
| 2 -> 6, 8 | to_eur | consistent |
| 2 -> 7, 9, 11 | format_cents, signed | consistent |
| 4 -> 5, 6, 7, 8 | conn fixture, schema v1 | consistent (rates CHECK USD/UAH matches set_rate) |
| 3 -> 7, 8, 12 | Entry | consistent fields |
| 5 -> 8, 12 | category_for_keyword, remember_keyword, list_categories, Category | consistent |
| 6 -> 8, 12 | rate_on, set_rate, parse_rate | consistent |
| 7 -> 9, 11, 12 | Pot, PotMove, list_pots, recent_moves, apply_pot_entry, set_goal, SavingsError | consistent |
| 7 <-> 8 | same wave, both write `entries` | disjoint files; tests cross-dependency -> A3, A4 |
| 8 -> 9, 10, 11, 12 | Record (+pending), records_between, all_records, last_records, delete_entry, undo_last, set_category | consistent |
| 9 -> 12, 13 | parse_month_arg, build_month_report, render_month | consistent |
| 10 -> 12, 13 | export_csv | consistent |
| 11 -> 12, 13 | texts, as_pre | consistent; rate display -> A7 |
| 12 -> 13 | tests/mocked_bot.py | same wave -> A8 |
| 12 -> 14 | build_dispatcher | consistent |
| 13 -> 14 | jobs.py (14 adds CLI entry) | different waves, consistent |
| 14 -> 15 | `python -m finbot`, `python -m finbot.jobs daily` | consistent |

### Rulings

- Ruling: work on `main` in this checkout, no worktree — project contract (stages/04_build/CONTEXT.md base commit on main; Misha's global rule: worktrees only when tests already exist) — cost if wrong: none, everything local, nothing pushed.
- Ruling: tasks of one wave run in parallel in the shared checkout (project process allows it for disjoint Files); each developer commits with an explicit pathspec, runs `ruff format` only on own files, and if the full suite fails only in a parallel developer's files, reports it instead of touching them; the controller runs the full ruff+pytest gate on the combined tree after every wave — cost if wrong: a cross-task break found at wave end instead of per task.
- Ruling: per-task review = project skill `two-axis-review` (Standards + Spec sub-agents, Sonnet), which replaces the SDD task-reviewer template — project instruction outranks the skill default — cost if wrong: none, both axes cover spec + quality.
- Ruling A1: first token with no digit (after optional `+`/symbol) -> `Start with the amount, e.g. 25 coffee`; first token that starts like a number but fails `parse_amount` -> `Amount must be like 25 or 12,50` — matches both plan tests — cost if wrong: one message wording.
- Ruling A2: R7 error text stays the exact plan string `Write 1200 without spaces, e.g. 1200 taxi` for any split number — plan says "exact" — cost if wrong: copy tweak later.
- Ruling A3: Task 7's soft-delete test sets `deleted_at` via SQL (no dependency on Task 8) — cost if wrong: none.
- Ruling A4: Task 8's pot-move test inserts the pot and the move via SQL (no dependency on Task 7) — cost if wrong: none.
- Ruling A5: report totals, categories and `top` use non-pending records only (EUR amounts unknown for pending); pending appear only in the count line — spec R14 "Pending entries are excluded from totals" — cost if wrong: a pending entry missing from Top 5 until /rate.
- Ruling A6: unspecified alignment (Top expenses amount column, several pots) is the developer's choice as long as the golden text matches exactly — cost if wrong: cosmetic.
- Ruling A7: rates are displayed as stored (`str(Decimal)`), so `/rate uah 0.022` shows `0.022` and a stored `0.0220` shows `0.0220`; R11 example holds for a rate typed as 0.0220 — cost if wrong: cosmetic.
- Ruling A8: wave 6 runs Task 12 first, Task 13 after Task 12 is reviewed (Task 13 tests need `tests/mocked_bot.py`); Task 12's MockedBot must support queued error results (aiogram-style `add_result_for(..., ok=False)`) so Task 13 can make SendDocument fail — cost if wrong: some wall-clock.
- Ruling A9: Task 14 builds settings inline in both entry points with the same expression (`os.environ` over `read_env_file(Path(".env"))` when it exists); `config.py` stays untouched (narrowest reading of Files) — cost if wrong: a 1-2 line duplication.
- Ruling R1: if aiogram's GitHub `tests/mocked_bot.py` cannot be fetched, the developer writes the equivalent (BaseSession subclass recording requests, queued results, `add_result_for`, `get_request`) — cost if wrong: none.
- Observation O1 (for QA, not changed): back-dated foreign entry before the first rate stays pending until the next /rate.

## Progress

- Ruling: fix rounds land as a separate `fix: ...` commit per round (no amend: parallel waves interleave commits, and rewriting is a destructive op) — the build log names the task's commit range — cost if wrong: some tasks have 2+ commits instead of exactly one.
- Ruling: developers' report files are explicitly requested in developer-rules.md (Task 1's Haiku declined to write a .md report under its own system rule; controller saved it from the reply) — cost if wrong: none.

Task 1: dispatched (base adf53db), DONE_WITH_CONCERNS bb0f068 — concerns: pytest-asyncio deprecation warning (loop scope unset), pyright needs --pythonpath (no venv config), read_env_file keeps lines without "=" as empty keys.
Task 1: review (two-axis) — Standards: 1 Hard (pytest-asyncio deprecation warning; output not pristine), 3 Judgement; Spec: compliant, 3 Minor.
- Ruling: the plan's pyproject.toml content is the required minimum, not an exclusive list — adding `asyncio_default_fixture_loop_scope = "function"` (pristine test output, engineering-rules) and `[tool.pyright] venvPath/venv` (pyright-lsp must resolve the venv, team.md) is in scope for Task 1 — cost if wrong: two config lines.
Task 1: minor (deferred): whitespace-only BOT_TOKEN passes when read from os.environ; int() accepts "+42"/"4_2" for OWNER_ID; read_env_file keeps a line without "=" as an empty key; ConfigError docstring restates the name; [project] has no version.
Task 1: fix round 1 dispatched (FIX_BASE bb0f068) -> f8ee146 (fix: pristine pytest output, pyright venv, config error examples). Developer added test_missing_keys_show_an_example (RED seen). Haiku again declined to append to a .md report; controller saved it. Developer reports switched to task-N-report.txt.
- Ruling: transaction convention for all domain modules (Tasks 6-10, 13): `db.connect` keeps sqlite3's default isolation; every function that writes wraps its writes in `with conn:` (commit on success, rollback on error), so multi-row writes (set_rate converting entries, apply_pot_entry) are atomic — the plan is silent, R28 needs no lost money — cost if wrong: none functionally; one extra line per writer.
Task 1: fix round 1/5 (2 addressed, 0 open; commits bb0f068..f8ee146)
Task 1: complete (commits adf53db..f8ee146, review clean)
Wave 2: base f8ee146, Tasks 2 and 4 dispatched in parallel.
Task 2: DONE 0dece57 (17 tests). Review — Standards: 0 Hard, 6 Judgement; Spec: compliant, 2 Minor.
Task 2: minor (deferred): `\d` accepts non-ASCII digits ("٣٠" -> 3000); no test pins fullmatch rejecting "25\n"; ValueError texts are developer-facing (Task 3 must not show str(e)); tuple-packed asserts in test_format/signed/to_eur (plan form).
Task 2: complete (commits f8ee146..0dece57, review clean)
Task 4: DONE 8e94544 (11 tests; extra tests for WAL, Row access, parent dir, order, schema rollback). Controller read db.py: BEGIN/COMMIT inside executescript + `with conn` rollback — sound.
Wave 2 gate (combined tree at 8e94544): ruff clean, format clean (9 files), pytest 37 passed, pyright 0 errors.
- Ruling: storage conventions for Tasks 6-10 — `entries.occurred_on` and `rates.set_on` are `date.isoformat()` text (YYYY-MM-DD, sorts correctly); rates are stored as `str(Decimal)` exactly as parsed (A7); `get_category` on an unknown id raises `LookupError` (a stale button can carry a deleted/unknown id) — plan silent — cost if wrong: none (single place each).
Task 4: review — Standards: 2 Hard (f-string around schema in executescript; report >300 words), 5 Judgement; Spec: compliant, 2 Minor.
- Ruling: Task 4 Hard 1 (`executescript(f"BEGIN;\n{schema}...")` vs "SQL uses parameters, never string formatting") — the rule guards against values in SQL; the interpolated text is the trusted packaged schema.sql and executescript/PRAGMA cannot bind parameters; kept as is — cost if wrong: none (no user input reaches it).
- Ruling: Task 4 Hard 2 (report 365 words > 300) — process nit, no code impact; developers reminded to keep prose short — cost if wrong: none.
Task 4: minor (deferred): connect() does not close the connection if schema apply raises (ResourceWarning on py3.13+); test_db duplication (closing(...), literal 15); conftest local `c`; RED evidence used a NotImplementedError stub.
Task 4: note for Task 15/QA: `files("finbot") / "schema.sql"` works only from the source tree (deploy rsyncs app/ and runs `python -m finbot` there, no pip install) — keep it that way.
Task 4: complete (commits 0dece57..8e94544, review clean after rulings)
Wave 2: complete. Wave 3 base 8e94544: Tasks 3, 5, 6 dispatched in parallel.
Task 5: DONE_WITH_CONCERNS 28727da (8 tests) — concerns: keyword match case-sensitive (parser lowercases), remember_keyword unknown id -> IntegrityError.
Task 6: DONE 73bc672 (22 tests) — [0-9] digits; set_rate relies on schema CHECK for currency.
Observation O2 (for QA, from Task 5 spec review): keywords.word is the PK (Task 4 schema), so one word maps to one category across kinds; remembering 'bonus' for income overwrites an expense mapping of 'bonus'. Follows the approved schema; R9/R10 silent.
Task 5: review — Standards: 1 Hard (report 389 words, process), 4 Judgement; Spec: compliant.
- Ruling: Task 5 Hard (report length) — same as Task 4: process nit, no code impact — cost if wrong: none.
Task 5: minor (deferred): `Category(id=row["id"], ...)` built 3x (a `_to_category(row)` would remove it); test helper `category_id` vs `_`-prefixed helpers elsewhere; RED evidence was a collection error only.
Task 5: complete (commits 73bc672..28727da, review clean after ruling)
Task 6: review — Standards: 0 Hard, 6 Judgement (test duplication, str(rate) twice, names, ValueError text developer-facing, monkeypatch coupling, two behaviours in one test); report evidence on a mixed tree (covered by the controller's wave gate).
Task 6: Spec: compliant, 4 Minor (extra tests tied to rulings; no upper bound on rate; set_rate trusts caller for currency; "today" supplied by caller).
Task 6: minor (deferred): no upper bound on parse_rate; set_rate relies on schema CHECK for currency (Task 12 must pass only USD/UAH); test helper duplication; str(rate) computed twice.
Task 6: complete (commits 8e94544..73bc672, review clean)
Task 3: DONE_WITH_CONCERNS cd6f503 (60 tests) — concerns: '€25 usd book' -> EUR note 'usd book'; '25 31.02' -> date error but '25 15.11' -> note; 'DD.MM.YY' is note text; 'save 1 200 x' -> generic save message.
Wave 3 gate (combined tree at cd6f503): ruff clean, format clean (15 files), pytest 127 passed, pyright 0 errors.
Task 3: review — Standards: 2 Hard (process: TDD count does not reconcile 58 vs 60; report 450 words), 9 Judgement (incl. tests pin only message prefixes; no WHY comments on start-vs-amount choice, last-year roll-back, date-validity-before-note-check); Spec: 1 Important (split number with decimals/symbol "1 200,50 taxi" saved as 1.00 EUR — Review Focus 1, R7), 2 Minor ("save 1 200" -> pot "200"; isdigit accepts Unicode digits).
- Ruling: R7 widened per spec ("looks like a split number"): first note word that, after removing one attached symbol, is digits with an optional decimal part -> split-number error — Review Focus 1 — cost if wrong: a note starting with a number like "1.5 water" is rejected (loud, user retypes).
- Ruling: pot word must contain a letter, else `Use: save 200 emergency` — stops "save 1 200" saving 1.00 into pot "200" — cost if wrong: numeric pot names impossible.
- Ruling (narrows pre-flight A1-date ruling): spec R6 says `DD.MM`/`DD.MM.YYYY` literally; a last token shaped `\d{1,2}\.\d{1,2}(\.\d{2,4})?` is a date only with exactly 2-digit day, 2-digit month, optional 4-digit year and a real date; any other date-shaped token -> `Use a date like 28.10 or 28.10.2026` — avoids silent misdating ("3 water 1.5" -> 1 May; "28.10.26" -> today) — cost if wrong: Misha must type 05.11 instead of 5.11 (told by the error).
- Ruling: `€25 usd book` keeps EUR with note "usd book" — the confirmation shows the currency, Undo is one tap; any fix needs new copy outside the plan — cost if wrong: rare mis-entry, visible immediately.
- Ruling: Standards Hard 1/2 on Task 3 are process (evidence accounting, length): developer to name both late tests in the fix report; no code impact.
Task 3: fix round 1 dispatched (FIX_BASE cd6f503).
Task 3: fix round 1/5 (6 addressed, 0 open; commits cd6f503..cc93fbf). Accepted consequence: lone DD.MM as only note word ("25 15.11") -> split-number error; note ending in a decimal ("25 coffee 2.5") -> date error.
Task 3: minor (deferred): `\d`/isdigit accept non-ASCII digits in parser regexes; refactor candidates (_parse_expense does several jobs, "EUR" literal x4, inline f-string message) left as is.
Task 3: complete (commits 28727da..cc93fbf, review clean)
Wave 3: complete (gate at cd6f503 green; cc93fbf full suite 144 passed per developer).
Wave 4: base cc93fbf, Tasks 7 and 8 dispatched in parallel.
- Ruling: Task 7 `recent_moves` order = occurred_on DESC, id DESC ("newest" by date, since moves can be back-dated); pot name shown capitalized via `str.capitalize()`; `set_goal` on unknown pot uses the same "No pot named ..." message — plan silent — cost if wrong: order of /savings lines.
- Ruling: Task 8 `set_category` on a missing or deleted entry raises LookupError; `deleted_at` uses the same UTC ISO format as created_at; one SELECT (entries LEFT JOIN categories, pots) builds every Record — plan silent — cost if wrong: none.
Task 8: DONE 8d19db1 (14 tests) — deviation: add_transaction raises ValueError for save/take; concerns: set_category two commits; set_category accepts pot moves; list functions return pending records.
Task 7: DONE_WITH_CONCERNS b3984c5 (13 tests) — concerns: get_pot/set_goal exact-case names (R15 says case-insensitive); set_goal(0) -> IntegrityError (handler must parse_amount first); two type-checker asserts.
Wave 4 gate (combined tree at b3984c5): ruff clean, format clean (19 files), pytest 171 passed, pyright 0 errors.
Task 7: Spec review — 1 Important (R15 case-insensitive pot names enforced only by the parser; get_pot/set_goal/apply_pot_entry exact-case), 2 Minor (set_goal(0) IntegrityError; untested id tie-break and deleted take).
Task 8: Spec review — compliant, 2 Minor (test pot move lacks eur_cents so it reads as pending; no category-kind guard in set_category).
Carry to Task 12: category buttons only of the entry's own kind; no category button on pot moves (/last and confirmations); /goal amount through money.parse_amount before set_goal; /rate passes only USD/UAH to set_rate.
Task 8: Standards review — 2 Hard (report 364 words; whole-repo evidence included uncommitted Task 7 files), 8 Judgement.
- Ruling: Task 8 Hard 1/2 are process; Hard 2 is covered by the controller's wave-4 gate on the combined committed tree at b3984c5 (171 passed, ruff/format/pyright clean) — cost if wrong: none.
Task 8: minor (deferred): test pot move lacks eur_cents (reads as pending; both axes); set_category commits entry and keyword memory separately (could run remember_keyword inside the same `with conn:`); local `entry` holds a Record (rename to `record`); no WHY comment on the save/take guard; LookupError text developer-facing (Task 12 must not show it).
Task 8: complete (commits cc93fbf..8d19db1, review clean after ruling)
Task 7: Standards review — 1 Hard (report 318 words, process), 8 Judgement (runtime asserts as type narrowing; _insert helper; names; duplicated SELECT tails; repeated test setup).
- Ruling: savings is the single choke point for pot identity — get_pot, set_goal and apply_pot_entry lowercase the pot name (spec R15) — cost if wrong: none.
- Ruling: replace `assert entry.pot is not None` with an explicit ValueError guard for non-pot kinds (matches ledger.add_transaction's guard; asserts vanish under -O) — cost if wrong: none.
Task 7: fix round 1 dispatched (FIX_BASE b3984c5).
- Ruling (wave 5, Task 9): empty blocks are omitted (no "Top expenses" header without expenses, no "Savings" without pots, no category block without spending); spent equal to previous month shows "▲ 0% vs Sep"; month names are fixed English regardless of server locale; pots in the report are current totals (list_pots) — plan silent — cost if wrong: cosmetic.
- Ruling (wave 5, Task 10): CSV amounts formatted from int cents without float (`f"{c // 100}.{c % 100:02d}"`); rate column = stored text — cost if wrong: none.
- Ruling (wave 5, Task 11): savings_text separates pots with a blank line; last_text shows no category arrow when uncategorized; HELP copy written by the developer around the 8 named examples (plan names the examples, not the wording) — cost if wrong: copy tweaks.
Task 7: fix round 1/5 (2 addressed, 0 open; commits b3984c5..30d8fc4)
Task 7: minor (deferred): set_goal(0) -> IntegrityError (Task 12 validates via parse_amount); `_insert` keeps an assert for lastrowid; guard test does not pin the message; untested id tie-break and deleted take.
Task 7: complete (commits 8d19db1..30d8fc4, review clean)
Wave 4: complete. Gate at 30d8fc4 below.
Wave 5: base 30d8fc4, Tasks 9, 10, 11 dispatched in parallel.
Task 10: DONE_WITH_CONCERNS a449197 (1 test) — concerns: '1.11' in brief (it is the date 2026-11-01, consistent); rate column never populated in the test.
Task 10: review — Standards: 0 Hard, 4 Judgement (test name overclaims date order; rate branch untested; _amount duplicates format_cents shape; name); Spec: compliant, 2 Minor (rate column never exercised; test name).
- Ruling: Task 10's untested rate column is raised to a fix item — R23 column and the pending->converted path (Review Focus 2) have no test in the export, and the fix is one test — cost if wrong: one extra test.
Task 10: fix round 1 dispatched (FIX_BASE a449197).
Task 11: DONE_WITH_CONCERNS 9834eaf (27 tests) — concern: saved_text pending line contains "<EUR per 1 USD>"; must not be sent with parse_mode HTML.
Carry to Tasks 12 and 14: no default parse_mode on the Bot (plain text everywhere); only /month and the monthly summary send `as_pre(...)` with parse_mode="HTML".
Task 10: fix round 1/5 (2 addressed, 0 open; commits a449197..dcc7b89 — fix commit dcc7b89 sits after Task 11's 9834eaf). Characterization test (no RED, code already correct) — disclosed.
Task 10: minor (deferred): `_amount` repeats format_cents' shape without separator (money.py outside Files).
Task 10: complete (commits a449197 + dcc7b89, review clean)
Task 11: review — Standards: 1 Hard (report 397 words, process — same ruling as Task 4), 6 Judgement (inflow rule spelled 3 ways; repeated signed(...) and category suffix; moves[:5] double cap; test duplication); Spec: compliant, 0 findings.
Task 11: minor (deferred): `_is_inflow` vs `kind == "save"` in two places; repeated test Record construction; low-value constant test; no 4096-char guard (texts are short).
Task 11: complete (commits a449197..9834eaf, review clean)
Task 9: DONE_WITH_CONCERNS 0f497da (21 tests, golden exact) — choices: Top amounts right-aligned, pots aligned, 'Not counted' own block after blank line, bad /month arg ValueError('Use a month like /month 10 or /month 2026-10'); concern: 'No entries.' decided from totals (save+take equal month renders No entries.).
Wave 5 gate (combined tree at 0f497da): ruff clean, format clean (25 files), pytest 227 passed, pyright 0 errors.
- Ruling (Task 12, interface change): aiogram 3.31 raises "Router is already attached" when one Router joins a second Dispatcher (router.py:237), so a module-level `router` breaks per-test dispatchers. handlers.py exposes `create_router() -> Router` (handler functions stay module-level, registered inside it) instead of `router: Router`; build_dispatcher calls it. No other task consumes `router` — cost if wrong: one interface name differs from the plan.
- Ruling (Task 12): pot-move confirmations (pot_text) carry no keyboard (undo via /undo); entry_keyboard only on expense/income confirmations — R18 shows no buttons for pots, avoids a new keyboard interface — cost if wrong: one convenience button missing.
- Ruling (Task 12): stale callbacks: undo/del on an already deleted entry -> callback.answer(NOTHING_TO_UNDO), message unchanged; cat/pick on a missing entry -> callback.answer() with no text; every callback answered — no new copy — cost if wrong: none.
- Ruling (Task 12): MockedBot adapted from aiogram's tests/mocked_bot.py: requests recorded in order; results queued per method class via add_result_for(method, ok, result, error_code, description); with nothing queued the session returns ok=True with result None (True for bool methods) so handler tests need no per-call setup — cost if wrong: test helper only.
- Ruling (Task 12): plain text everywhere (no default parse_mode); only /month uses as_pre + parse_mode="HTML". /goal amount via money.parse_amount, bad input -> "Use: /goal emergency 10000"; /rate accepts only usd/uah + rates.parse_rate, bad input -> "Use: /rate usd 0.92"; /month bad arg -> reply str(ValueError) from reports.parse_month_arg; /last empty -> "No entries yet." without keyboard; category buttons only of the entry's own kind.
Task 9: review — Standards: 2 Hard (report 363 words; "▲ 0%" choice not in report — it is the controller's ruling), 9 Judgement (magic widths 12/6/5; _share name; width idiom x4; lines[1] patch; test gaps: min bar, January vs December); Spec: 1 Important ("No entries." inferred from totals: save + equal take month renders No entries.), 2 Minor (MONTH_ARG_MSG copy in reports.py; lenient month parsing).
- Ruling (Task 9, interface addition): MonthReport gets a trailing field `entries: int` (non-deleted records of any kind in the month); render_month shows "No entries." iff entries == 0 — matches the brief's "a month with no records"; no other task constructs MonthReport — cost if wrong: one extra field.
- Ruling: MONTH_ARG_MSG "Use a month like /month 10 or /month 2026-10" accepted as the /month bad-argument reply; stays in reports.py (Task 12 replies str(e)) — cost if wrong: copy tweak.
Task 9: fix round 1 dispatched (FIX_BASE 0f497da).
Task 9: fix round 1/5 (3 addressed, 0 open; commits 0f497da..71debd8)
Task 9: minor (deferred): `_share` name; width idiom repeated 4x; lines[1] patch for Spent; helper signature inconsistency; percent-of-goal shape duplicated with texts.py; `_eur` assert; lenient parse_month_arg ("05", "2026-9").
Task 9: complete (commits dcc7b89..71debd8, review clean)
Wave 5: complete. Wave 6: base 71debd8, Task 12 dispatched alone (Task 13 after Task 12, ruling A8).
Task 12: DONE_WITH_CONCERNS 13314a1 (14 tests, 246 overall) — concerns: no committed tests for /last /savings /goal /rate usage /month arg errors /start /help (scratch only); callbacks answered before editing; unknown slash commands fall to the parser ('Start with the amount'); mock ok=False path untested here.
- Ruling: Task 13 starts now, in parallel with Task 12's review (same wave, disjoint files; tests/mocked_bot.py is committed in 13314a1). Any Task 12 fix round must keep the MockedBot API (MockedBot(), .requests, .add_result_for) unchanged — cost if wrong: Task 13 test rework.
- Ruling (Task 13): "previous month has no records" = build_month_report(...).entries == 0 (field added in Task 9 fix); meta key `summary_sent:YYYY-MM` written with INSERT OR REPLACE in `with conn:` only after both sends succeed; send errors propagate (no catch) so the key stays unset; a same-day backup rerun overwrites today's file; retention keeps the 14 newest `finbot-YYYY-MM-DD.db` by name — cost if wrong: none. Known consequence: if SendMessage succeeded and SendDocument failed, the next run sends the report text again (duplicate text, never a missing summary) — for QA.
Wave 6: Task 13 dispatched (base 13314a1) in parallel with Task 12 review.
Task 13: DONE 1efdd4f (9 tests, 255 overall) — meta value = today's ISO date; same-day overwrite and missed-day tests; concerns: duplicate text after a failed document (known), late-dated entries in a summarised month never re-sent (by design), today must be Vienna (Task 14).
Task 12: Standards review — 1 Hard (report 515 words), Judgement with real risk: callback answered after the domain call (non-LookupError failure leaves the button spinning, telegram-rules); unchanged-edit TelegramBadRequest ("message is not modified") on re-pick / double "Change category" unhandled; no 4096 guard on /savings; usage strings in handlers.py; large test gaps (OwnerOnly callback branch — the data-deleting path — untested; /start /help /last /savings /goal /rate usage /month bad arg; categorized reply keyboard; cat and del callbacks; last_keyboard content; 3-per-row; MockedBot ok=False).
Task 12: Spec review — compliant; no committed tests for spec behaviours (R17 /savings,/goal; R20 /last; R12 /rate negatives; R21 /month args; R19 undo/del happy paths; R10 change category; R9/R11 categorized reply keyboard, income buttons; R25 foreign/group callbacks); Minor: unknown EntryCb action never answered; /last list replaced by one entry text after cat/del (per ruling).
- Ruling: missing committed tests for spec behaviours are Important (a wiring error would pass the current 14 tests; R25 callback path can delete data). Callback answer on every path (try/finally, exactly once) and the "message is not modified" edit refusal are Important (telegram-rules). /savings 4096 guard and usage strings in handlers.py stay deferred minors (texts.py is outside Task 12 Files; pots are few).
Task 12: fix round 1 dispatched (FIX_BASE 13314a1; Task 13's 1efdd4f sits on top, disjoint files).
Task 13: Spec review — compliant, 2 Minor (known duplicate text after a failed document; a summary for a month two back is never sent if the server is down a whole month — R24 only asks for the next run).
- Ruling: Task 15 (deploy kit) starts early, in parallel with Task 12's fix round — it consumes nothing from waves 5-6 (only the entry-point command names fixed in the plan) and its files are disjoint; Task 14 still waits for wave 6 (it modifies jobs.py and calls build_dispatcher) — cost if wrong: none.
- Ruling (Task 15): units exactly as the brief; timer `OnCalendar=*-*-* 09:00:00 Europe/Vienna` (systemd timezone suffix); deploy.sh modeled on job-digest's script, never run; executable bit committed (mode 100755); no token-like string — cost if wrong: none (not deployed in this stage).
Wave 7 (early): Task 15 dispatched (base 1efdd4f).
Task 13: Standards review — 1 Hard (report 388 words, process), Judgement: retention glob `finbot-*.db` wider than the date format (a `finbot-manual.db` would count as newest and push out a real backup); no test that unrelated files survive; `sent` really means "has entries"; partial backup on failure; no 429 retry; no 4096 check.
- Ruling: retention touches only files named exactly `finbot-YYYY-MM-DD.db` (deletion safety), with a test that other files in backup_dir survive; rename `sent` -> `has_entries`. Deferred: tempfile+rename backup, 429 retry (the daily timer retries), 4096 guard — cost if wrong: none.
Task 13: fix round 1 dispatched (FIX_BASE 1efdd4f).
Task 13: fix round 1/5 (2 addressed, 0 open; commits 1efdd4f..83991c6)
Task 13: minor (deferred): partial backup file if conn.backup fails mid-way (no tempfile+rename); no 429 retry_after handling (timer is the retry); no 4096 check on the summary text; raw meta SQL in jobs.py.
Task 13: complete (commits 13314a1..83991c6, review clean)
Task 12: fix round 1 -> 57edafc (47 bot tests, 289 overall). Controller gate: pyright 1 error at tests/test_bot.py:108 "Function type parameter syntax requires Python 3.12" — pyright does not infer 3.12 from the venv; ruff UP047 requires the PEP 695 form.
- Ruling: fix belongs to Task 1's pyproject.toml (`pythonVersion = "3.12"` under [tool.pyright]); Task 1 developer resumed for fix round 2 — cost if wrong: none.
Task 1: fix round 2/5 (1 addressed, 0 open; commit 60f5e29 — one config line). Ruling: re-review done by the controller directly (git show: +1 line `pythonVersion = "3.12"`, pyright 0 errors on the whole tree) — a one-line tooling config needs no reviewer seat — cost if wrong: none.
Task 15: DONE_WITH_CONCERNS 7b96171 (7 tests; deploy.sh 100755) — deviations: DB backup via sqlite3 backup API (WAL), timer enable --now; open risks: only DB backed up (code rollback = redeploy previous commit), finance-bot.service not enabled (reboot leaves bot down), ExecStart needs Task 14, daily unit lacks network-online, nothing run on a server.
- Ruling (Task 15): enable finance-bot.service in deploy step 7 (a reboot must not leave the bot down; spec R26 "restart on crash" in spirit); add After/Wants=network-online.target to the daily service; code rollback stays "redeploy the previous commit + restore the DB backup" (brief backs up the DB only) — cost if wrong: two lines.
Task 12: fix round 1/5 (3 addressed, 1 new Important — brief test test_undo_twice_removes_then_reports_nothing weakened: first "/undo" reply no longer asserted; commits 83991c6..57edafc)
Task 12: fix round 2 dispatched (FIX_BASE 57edafc): restore both literal replies; add AnswerCallbackQuery assertion to the del test; literal "Nothing to undo." in the stale-undo test.
- Ruling: Task 14 starts now, in parallel with Task 12 fix round 2 (test-only change in tests/test_bot.py; build_dispatcher signature is final; Task 13 complete) — cost if wrong: none.
Wave 7: Task 14 dispatched (base 7b96171).
Task 12: fix round 2 -> 093081e (test-only); scoped re-review dispatched.
Task 15: Spec review — compliant, Minor: enable --now on the timer (accepted: a timer only enabled would not fire before reboot); set -E for the ERR trap (accepted); is-active checked immediately after restart; backup copy keeps default umask (server rules want 600); R27 says "nightly" but the approved plan's single timer runs backup at 09:00 Vienna (FYI for Misha, not changed); ExecStart depends on Task 14.
- Ruling (Task 15 fix round, with the two earlier rulings): enable finance-bot.service; network-online ordering on the daily service; chmod 600 on the DB backup copy; short wait (e.g. 3 s) before the is-active check — cost if wrong: four small lines.
Task 15: Standards review — 2 Hard: (1) printed rollback line (ERR trap from step 1 on, and on first deploy with no DB) runs `rm -f finbot.db-wal ...` before a `cp` of a backup that may not exist -> could destroy committed rows; (2) report 400 words. Judgement: umask for backup; tests/env check run after code switch (brief order); fixed /tmp path for test venv; empty BOT_TOKEN passes key check; is-active immediately; service not enabled; rollback printed under dry-run; unanchored data/ exclude; DB path hard-coded.
- Ruling (Task 15 fix round 1): rollback printed only after step 2 really backed up the DB, guarded by `test -f "$BACKUP/finbot.db" &&` before any rm; first deploy prints that there is nothing to roll back; enable finance-bot.service; network-online ordering on the daily service; `umask 077` for the backup; `sleep 3` before is-active; `mktemp -d` test venv; `.env` check requires non-empty BOT_TOKEN/OWNER_ID values (still never printed). Step order stays as the brief prescribes (plan-mandated; tests also run locally before deploy) — cost if wrong: a failed server pytest leaves new code on disk until the next deploy (noted for release stage).
Task 15: fix round 1 dispatched (FIX_BASE 7b96171).
Task 12: fix round 2/5 (2 addressed, 0 open; commits 7b96171..093081e)
Task 12: minor (deferred): no 4096 guard on /savings; RATE_USAGE/GOAL_USAGE live in handlers.py (texts.py outside Files); unknown slash commands fall to the entry parser ("Start with the amount"); after cat/del from /last the list message is replaced by one entry's text (per ruling); exception paths of cat/del handlers covered by reading, only pick's tested; isinstance(callback.message, Message) x3; build_dispatcher repeated in tests (now a helper).
Task 12: complete (commits 71debd8..093081e: 13314a1, 57edafc, 093081e; review clean)
Wave 6: complete (Tasks 12, 13).
Task 14: DONE c149c0a (300 overall) — _connector_init['family']=AF_INET (aiohttp.py:85); daily job uses 'async with build_bot(...)' to close the session; real Telegram connection not exercised (acceptance stage).
Task 15: fix round 1/5 (all addressed, 0 open; commits 7b96171..19b0c47 — fix commit after Task 14's c149c0a). Simulation in a scratch clone with fake ssh/rsync: rollback only with a real backup, dry run 0 calls.
Task 15: minor (deferred): code not backed up (rollback = redeploy previous commit + DB restore); new code on disk before server pytest (brief order); ssh blip on the backup check says "nothing to roll back"; rollback test checks the first rm only; DB path hard-coded to data/finbot.db; R27 "nightly" vs 09:00 timer (FYI for Misha).
Task 15: complete (commits 1efdd4f..19b0c47: 7b96171, 19b0c47; review clean)
Task 14: review — Spec: compliant (1 Minor: logging.basicConfig in jobs, accepted). Standards: 1 Hard: bot token reaches the log — aiohttp network errors carry the request URL (.../bot<TOKEN>/...), logged by jobs (logging.exception), by aiogram's polling loop ("Failed to fetch updates") and by an uncaught traceback in __main__ (reproduced with a fake token against a local server); 1 Hard (report 427 words); Judgement: runner subprocess tests use cwd=app (would read the real app/.env if argparse ordering ever changed); no exit-code tests for the daily job (behaviour verified by probe); Settings repr includes bot_token (latent, config.py); weak RED for IPv4.
- Ruling (Task 14 fix round 1): add a token-redacting logging filter in bot/session.py (`redact_token_in_logs(token) -> None`, installed on the root logger's handlers, masking the token in the message and in exception text) and call it in both entry points right after logging and settings are set up; __main__ catches any exception from polling, logs it with logging.exception (so it passes the filter) and exits 1 (systemd Restart=always restarts it); runner subprocess tests run with cwd=tmp_path and PYTHONPATH=app so they can never read app/.env. Deferred: Settings repr (config.py, nothing prints settings) — cost if wrong: a few lines.
Task 14: fix round 1 dispatched (FIX_BASE c149c0a).
- Ruling: after Task 14 closes, one SDD final whole-branch review (Opus) over adf53db..HEAD focused on cross-task integration and triage of the deferred minors; findings go to ONE fix dispatch + one scoped re-review. This is the build stage's own closing gate, not stage 05 QA (which needs Misha's word: /code-review, /simplify, pr-review-toolkit agents, acceptance checklist stay for QA) — cost if wrong: one review seat.
Task 14: fix round 1/5 (2 addressed, 0 open; commits 19b0c47..c19d60b). Verified with fake tokens: aiogram polling log, jobs exception, tracebacks, chained exceptions -> 0 token occurrences.
Task 14: minor (deferred): filter calls getMessage() outside emit's try (malformed log args would raise in caller; none exist); handlers added after install not covered (none exist); connect/build_bot outside __main__'s try (cannot carry the token); Settings repr includes bot_token (nothing prints it); test fixture filter left on pytest root handlers.
Task 14: complete (commits 093081e..c19d60b: c149c0a, c19d60b; review clean)
Wave 7: complete. All 15 tasks complete.
Final review (Opus, adf53db..c19d60b): Ready for QA with fixes. Critical 0. Important 3: (1) currency typed after the note ("1200 taxi uah") saved as EUR; (2) a typo pot can never be removed from /savings, reports and summaries; (3) units lack UMask, so DB and backups would be world-readable (server-rules want 600). Minor 5: deleting a save from /last can push a pot below zero; entries dated at processing time, not message time (downtime across midnight); O1 back-dated foreign entry before first rate; mistyped rate unbounded ("/rate usd 092" -> 92) with no undo; capitalised/unknown commands get the entry-parser reply, no set_my_commands menu. Deferred-minor triage: none must be fixed before QA.
- Ruling (final fix dispatch, one developer): (1) parser rejects an entry whose last note word (after the date is taken) is a known currency code (CURRENCIES or UNSUPPORTED, any case) or symbol with the new message `Put the currency right after the amount, e.g. 1200 uah taxi` — R4 puts the currency right after the amount; a silent 45x error outweighs one new error string — cost if wrong: a note ending in "usd" is rejected (loud); (2) savings.list_pots hides pots with no live moves (get_pot unchanged) — cost if wrong: an emptied pot with a goal disappears from /savings until the next save; (3) `UMask=0077` in both service units + test lines — server-rules — cost if wrong: none.
- Ruling: final-review minors 4-8 go to QA and Misha as product questions (rate bound, message-time dating, negative pot after delete, command menu); not changed in the build stage — cost if wrong: they surface at acceptance.
Final fix dispatch sent (FIX_BASE c19d60b).
Final fix: 1/1 (3 addressed, 0 open; commits c19d60b..3f55a7c). Re-review: all addressed, no new breakage (hidden pot: /month skips Savings block, /savings says "No pots yet").
Final fix: minor (deferred): "25 lunch try" rejected (TRY is an unsupported code; loud, rare); /goal or take on a hidden typo pot still finds it (get_pot unchanged); UMask covers only files created after deploy (first deploy creates the DB, so no chmod needed unless a DB is copied in).
Final gate (HEAD 3f55a7c, 27 commits since adf53db): ruff clean, format clean (38 files), pytest 312 passed, pyright 0 errors, entry points import, bash -n deploy.sh ok.
Build stage complete. Workspace kept (deleting files needs Misha's yes); ledger copied to stages/04_build/references/sdd-ledger-phase1-2026-10-31.md.

## QA fix set (Misha: "да закрывай эти проблемы чтоб двигаться дальше", 31.10.2026)
Base aa10621. Four developers in parallel with disjoint files: F-A parser, F-B rates+bot, F-C ledger/savings tests, F-D deploy+gitignore.
- Ruling: rate ranges USD 0.5-2.0 EUR and UAH 0.005-0.1 EUR inclusive (told to Misha); `rates.RateError` + `rates.check_rate(currency, rate)`; message per currency with an example.
- Ruling: note max 100 characters (joined note), pot name max 30; full dates after today rejected with their own message; DD.MM without year = the latest such date not after today (fixes 29.02).
- Ruling: /goal with a pot name without a letter answers GOAL_USAGE (Q-7).
- Ruling: deploy step 8 waits longer than RestartSec, then checks the bot service alone (active and zero automatic restarts) and the timer alone; rollback line only once step 7 started (DB touched); step 5 checks .env mode 600.
Fix C: DONE 961dc11 (4 tests, mutation-checked).
Fix A: DONE 40b0d37 (parser 107 tests, RED 11 failed).
Fix C: review — Standards 3 Judgement (accept half duplicates an existing test; report's 340 measured on mixed tree, 316 at 961dc11 clean; RED via mutations, disclosed); Spec 0 findings, all 4 mutants killed (+1 extra). Fix C: complete (961dc11, review clean).
Fix B: DONE 6a0c722 (rates+bot 96 tests, full 370).
Fix A: review — Standards 1 Hard (report 538 words, process) + 3 Judgement (bare 100/30/-5 literals; misplaced comment; untested check order); Spec 0 missing/0 extra; side effects accepted: `25 01.01.2030` (lone future date, no note) now gets the future-date error instead of being a note; `25 29.02` lone gets the split message (same as `25 15.11`). Differential fuzz 163,944 inputs: only the 5 intended groups differ.
- Ruling: accept both side effects (a lone date-like word is not a real note; loud error) — cost if wrong: retype.
- Note: spec R5/R6 text predates the approved QA fixes (limits, future dates); fold into the next spec variant at phase 2 planning (approved work is not edited in place).
Fix A: complete (40b0d37, review clean after ruling).
Fix D: DONE_WITH_CONCERNS 5fd69bd (deploy tests 12) — NRestarts reset on explicit restart assumed (verify at first real deploy).
Fix B: review — Standards 1 Hard (report 548 words, process) + 4 Judgement (per-currency data in 3 tables; letter check duplicated with parser; test setup duplication; two picks hand-built); Spec 0 blocking, 2 minor (4a pick hand-built; accepted-limit tests check reply only). ~20 scratch mutations all killed; -W error 370 passed; pyright 0.
Fix B: complete (6a0c722, review clean).
Fix D: review — Standards 0 Hard, 3 Judgement (sleep 10 not tied to RestartSec=5; long ssh one-liners; report ~329 words, /tmp used once); Spec 1 partial: step-8 test is vacuous ("NRestarts" matches the step label; deleting the systemctl show call or using -ge 0 passes all 12 tests); risky (not changed): NRestarts reset on explicit restart ~85% per systemd source (fails closed; confirm "NRestarts 0" at first real deploy); "database was not touched" slightly absolute (new code on disk from step 1); state sampled twice.
Fix D: fix round 1 dispatched (FIX_BASE 5fd69bd): make the step-8 test assert the real check.
Fix D: fix round 1/5 (1 addressed; 3066382). Re-review by the controller directly: in a scratch export, mutant B (`= 0` -> `-ge 0`) and mutant A (drop the systemctl show call and zero check) each fail test_deploy_step_8_checks_restarts_and_timer_after_sleep (1 failed, 11 passed).
Fix D: minor (deferred): sleep 10 not tied to RestartSec=5; "database was not touched" wording slightly absolute (new code on disk from step 1); bot state sampled twice; NRestarts reset assumption - confirm at first real deploy.
Fix D: complete (5fd69bd, 3066382).
QA re-check (Sonnet, HEAD 3066382): items 1-6, 8 closed with evidence (clean venv 370 passed, pyright 0; deploy simulated incl. running the printed rollback line against a fake root; acceptance lines 1-10 through MockedBot unaffected). T-1: 11/12 mutations now killed; survivor: UNSUPPORTED shrunk to GBP (test parametrizes the imported tuple instead of the explicit list the brief asked for). New N-1 minor: `/goal <31+ char name> 5000` suggests a save command the parser rejects.
- Ruling: close both now (Misha: "закрывай эти проблемы"): explicit code list in the parser test; /goal pot name validated like the parser (letter + max 30 chars) -> GOAL_USAGE. One developer, controller verifies by mutation.
Fix E: DONE fa769f4 (372 tests). Controller check: removing the 30-char guard in a scratch copy fails test_goal_with_pot_name_over_30_letters_is_usage; developer showed UNSUPPORTED=("GBP",) fails 6 parser tests. Fix E: complete.
QA fix set complete. Gate at fa769f4: ruff clean, format clean (38 files), pytest 372 passed, pyright 0 errors.
