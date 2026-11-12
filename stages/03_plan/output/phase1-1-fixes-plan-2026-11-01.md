# Phase 1.1: acceptance fixes (implementation plan)

Approved by Misha 01.11.2026 after the first acceptance on the server bot: "1 - по рекомендации 2 - делаем вмесет с доработками" (decision rows 01.11 in `shared/decisions.md`). Spec: `stages/02_spec/output/spec-2026-10-31.md`; where a task below changes a reply or a command, this plan is the newer authority.

## Global Constraints

- Code in `app/`, Python 3.12, aiogram 3.31.0, sqlite3. Read `_config/engineering-rules.md`, `_config/storage-rules.md`, `_config/telegram-rules.md` first.
- Test first: a failing test, then the code. Whole gate green before the commit: `cd app && .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pyright && .venv/bin/pytest -q`.
- One commit per task, pathspec commit of only the task's files, English message, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never stage `.agents/`, `.codex/`, `app/.env`, `app/data/`. No push.
- Never read or print `app/.env`. Never touch the server.
- Money stays int cents; every writer uses `with conn:`; dates display as `DD.MM` through `texts._day`.
- Bot copy in English, exactly as given below. Existing tests may change only where they pin copy or a return value this plan changes; say which in the report.
- Buttons already sent in Misha's chat (`e:cat:<id>`, `e:del:<id>`, `e:undo:<id>`, `p:<id>:<cat>`) must keep working.

### Task 1: Dates in replies, EUR amount in /last, clear /rate reply

**Files:** `app/finbot/texts.py`, `app/finbot/rates.py`, `app/finbot/bot/handlers.py`, `app/tests/test_texts.py`, `app/tests/test_rates.py`, `app/tests/test_bot.py`.

1. `saved_text`: the first line starts `Saved DD.MM:` instead of `Saved:` (the entry's own date). Example for `25 coffee yesterday` on 01.11: `Saved 31.10: -25.00 EUR · coffee → Eating out`. Everything after the date is unchanged.
2. `removed_text`: `Removed DD.MM: -25.00 EUR · coffee` (the entry's date).
3. `/last` lines (`_last_line`): a non-EUR entry shows its EUR amount right after the currency: `4. 01.11 -25.00 USD (≈ -23.00 EUR) book`; a pending one shows `4. 01.11 -25.00 USD (no rate yet) book`. EUR entries unchanged. Put the shared part (date, amount, currency, EUR part, label, category arrow) in one helper `_entry_line(r: Record) -> str`, so `_last_line` is `f"{number}. {_entry_line(r)}"` (Task 2 reuses it).
4. `set_rate` returns `list[int]`: the ids of the entries it converted, in id order (was the count). Update its callers and tests (`len(...)` where a count was asserted).
5. `rate_set_text(currency: str, rate: Decimal, converted: list[Record]) -> str`:
   - no converted entries: `Saved: 1 USD = 0.92 EUR.`
   - one: `Saved: 1 USD = 0.92 EUR.` newline `Converted 1 entry that was waiting for this rate:` newline `01.11 -25.00 USD book = -23.00 EUR`
   - several: `Converted 3 entries that were waiting for this rate:` and one line each, oldest first, at most 5 lines, then `...and 2 more` if more.
   - Each line: `DD.MM <signed amount> <CUR> <label> = <signed eur> EUR`, signs as in `/last`.
   The `/rate` handler loads the converted records with `get_record` and passes them.
6. Tests: each new copy above (text level and one bot-level `/rate` with a pending USD entry checking the reply and the database), a pending entry in `/last`, a converted UAH entry in `/last`.

Commit: `feat: dates in saved and removed replies, EUR amount in /last, clear /rate reply`

### Task 2: /last with one button per entry and a record view

**Files:** `app/finbot/bot/keyboards.py`, `app/finbot/bot/handlers.py`, `app/finbot/texts.py`, `app/tests/test_bot.py`, `app/tests/test_texts.py`.

1. `last_keyboard(records)`: one button per record, one per row, text `<n>. <label> <signed amount> <CUR>` with the label cut to 20 characters (e.g. `1. dm -42.00 EUR`, `3. Emergency pot +200.00 EUR`), callback `EntryCb(action="open", entry_id=record.id)`. The message text of `/last` stays the numbered list.
2. New callback `open`: edit the message in place to the record view. Text: `_entry_line(record)` (from Task 1). Keyboard `record_keyboard(record)`: row 1 `Change category` (`cat`, only for expense and income) and `Delete` (`del`); row 2 `Back to list` (`EntryCb(action="back", entry_id=0)`). A record that no longer exists: answer the callback with `Already deleted.` and change nothing.
3. New callback `back`: edit the message to the current `/last` list and keyboard (`No entries yet.` and no keyboard when empty).
4. `del` (from the record view or an old /last message): as now, plus a `Back to list` button under the `Removed ...` text. `undo` (under a saved reply) stays without it.
5. `cat` and picking a category: unchanged (the pick shows the saved reply with `Change category` / `Undo`; accepted).
6. Every callback is answered exactly once (keep the `try/finally` pattern) and "message is not modified" stays ignored.
7. Tests (press buttons taken from the markup the bot sent, like the existing tests): list buttons carry each record's id and the copy above; open shows the view and its buttons (no category button for a pot move); back restores the list; delete from the view deletes only that record and shows `Back to list`; undo has no back button; old `e:cat` / `e:del` data still work; open of a deleted record.

Commit: `feat: /last opens one entry at a time with change, delete and back`

### Task 3: Goal deadline with a monthly amount

**Files:** `app/finbot/db.py`, `app/finbot/savings.py`, `app/finbot/texts.py`, `app/finbot/bot/handlers.py`, `app/tests/test_db.py`, `app/tests/test_savings.py`, `app/tests/test_texts.py`, `app/tests/test_bot.py`.

1. Migration: the server database is at `user_version = 1` with real data. `connect()` applies `schema.sql` at version 0 (as now, sets 1), then at version 1 runs `ALTER TABLE pots ADD COLUMN goal_month TEXT` and sets `user_version = 2`, in one transaction. A fresh database ends at 2 too. Test: a version-1 database with a pot and entries is upgraded with data intact; connecting twice is a no-op.
2. `Pot` gets `goal_month: str | None = None` (last field, `YYYY-MM`). `set_goal(conn, name, goal_cents, goal_month: str | None = None)` stores both; a `/goal` without a month clears the month.
3. `/goal <pot> <amount> [MM.YYYY]`: month two digits 01-12, year four digits. Wrong shape -> `Use: /goal emergency 10000 or /goal emergency 10000 12.2027`. A month before the current month -> `That month has passed. Use this month or later, e.g. 12.2027`. Existing pot-name checks stay; their usage reply becomes the new usage text.
4. `/savings` and the `/goal` reply: `savings_text(pots, moves, today: date)`. A pot with a goal and a month adds ` · by MM.YYYY: <x> EUR a month`, where months left = months from today's month to the goal month inclusive, and x = (goal - total) / months left rounded UP to the cent. Example: today 01.11.2026, 300.00 of 10,000.00 by 12.2027 -> 14 months -> `Emergency: 300.00 EUR of 10,000.00 (3%) · by 12.2027: 692.86 EUR a month`. Total already at or above the goal -> ` · goal reached`. Goal month before today's month -> ` · 12.2027 has passed`. A goal without a month: unchanged.
5. The monthly report (`reports.py`) is unchanged.

Commit: `feat: goal deadline with the monthly amount to save`

### Task 4: Command menu and help

**Files:** `app/finbot/texts.py`, `app/finbot/bot/app.py`, `app/tests/test_bot.py`, `app/tests/test_texts.py`.

1. `texts.BOT_COMMANDS: list[tuple[str, str]]`, in this order:
   - `month` - `Report for this month`
   - `last` - `Last 10 entries: change or delete`
   - `undo` - `Delete the last entry`
   - `savings` - `Savings pots and goals`
   - `goal` - `Set a goal: /goal emergency 10000 12.2027`
   - `rate` - `Set a rate: /rate usd 0.92`
   - `export` - `All entries as a CSV file`
   - `help` - `How to write entries`
2. `build_dispatcher` registers a startup handler that calls `bot.set_my_commands` with these commands (default scope). This fills Telegram's "Menu" button. A Telegram or network error there is logged with `logging.exception` and the bot keeps starting (bookkeeping must not depend on the menu).
3. `HELP`: replace the last line with `/goal emergency 10000 12.2027 - goal with a deadline` and a new last line `All commands: the Menu button next to the message field`; keep the other lines.
4. Tests: `emit_startup` on the dispatcher with the mocked bot sends one `SetMyCommands` with exactly the list above; a failing `SetMyCommands` does not raise; `/help` text.

Commit: `feat: Telegram menu with all commands, help mentions it`
