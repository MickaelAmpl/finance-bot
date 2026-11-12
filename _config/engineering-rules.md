# Engineering rules

Mandatory for every code change in `app/`. The goal is small, correct, boring code: nothing that the approved spec and the current task do not need.

## Stack (approved 31.10.2026, do not change without Misha)

- Python 3.12 (server has 3.12; on the Mac use `~/.local/bin/python3.12` via `uv`).
- aiogram 3.31.0, pinned. No other runtime dependencies without the product owner's approval in the task spec.
- SQLite via the standard `sqlite3` module. No ORM.
- Dev tools: pytest, pytest-asyncio, ruff. Versions pinned in `app/requirements-dev.txt`.

## Scope discipline

- Implement exactly the task's Files and Interfaces. No extra parameters, options, flags, config keys, helper layers, base classes or "for later" hooks.
- No speculative generality: a function has one caller until a second real caller exists.
- Do not touch files outside the task's Files list. If another file must change, stop and report.
- If the plan is ambiguous, pick the narrowest reading and note it in the task report. Never invent scope.

## Code

- Money is integer cents everywhere (`amount_cents: int`). Never `float` for money. Exchange rates are `decimal.Decimal`, stored as TEXT.
- Rounding cents: `ROUND_HALF_UP`.
- Dates: `datetime.date`; "today" and month boundaries in `Europe/Vienna` (`zoneinfo`). Timestamps stored as ISO 8601 UTC text.
- Type hints on every public function. Dataclasses (`frozen=True` where possible) for records.
- Short docstrings only where the WHY is not obvious. No comments that repeat the code.
- Errors shown to the user are plain English sentences with an example of correct input.
- SQL uses parameters, never string formatting.
- Keep modules focused: one responsibility per file, as mapped in the phase plan.

## Tests and checks

- Test first: write the failing test, run it, see it fail, then the minimal code (superpowers:test-driven-development).
- Before reporting a task: `cd app && .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pytest -q` all green. Paste the summary lines in the report.
- Type errors shown by pyright (the `pyright-lsp` plugin) in the task's files are fixed before reporting.
- Tests never touch the network or the real Telegram API: use the mocked session in `tests/mocked_bot.py`.
- Tests never use `data/finbot.db`; use the `tmp_path` database fixture.

## Commits

- One task, one commit, English message: `feat: ...`, `fix: ...`, `test: ...`, `chore: ...`.
- Never commit `.env`, `*.db`, `data/`, `.venv/`, tokens or real financial data.
- Do not push anywhere. Commits stay local until Misha decides on GitHub.

## Task report (developer to product owner)

Files changed, what each change does, test and lint output summary, deviations from the plan, open risks. Under 300 words.
