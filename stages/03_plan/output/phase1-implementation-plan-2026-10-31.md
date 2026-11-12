# Phase 1 Personal Ledger Implementation Plan

Status: approved by Misha on 2026-10-31 ("Утверждаю"). Execution: subagent-driven, as set in `_config/team.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Telegram bot that records Misha's expenses, income and savings from one-line messages and sends a monthly summary, running on his VPS server.

**Architecture:** Pure Python modules (money, parser, categories, rates, savings, ledger, reports, export, texts) over one SQLite file, wrapped by a thin aiogram layer (handlers, keyboards, owner-only middleware) running with long polling. A daily systemd timer runs `finbot.jobs daily`: database backup, then the monthly summary when due.

**Tech Stack:** Python 3.12, aiogram 3.31.0, sqlite3 (stdlib), pytest + pytest-asyncio, ruff, systemd.

**Spec:** `../../02_spec/output/spec-2026-10-31.md` (requirements R1-R28). Rules: `../../../_config/engineering-rules.md`, `../../../_config/telegram-rules.md`.

## Global Constraints

- Python `>=3.12`; `aiogram==3.31.0`; no other runtime dependency.
- All code under `app/`: package `app/finbot/`, tests `app/tests/`, deploy files `app/deploy/`. Commands run from `app/`.
- Money: `int` cents only. Rates: `decimal.Decimal`, stored as TEXT. Cent rounding `ROUND_HALF_UP`.
- Currencies: `("EUR", "USD", "UAH")`; base currency EUR. Time zone `Europe/Vienna` for "today" and months.
- UI copy in English, exactly as given in the tasks. Amounts shown as `1,200.00`; sign ASCII `-` / `+`.
- Every task: ruff check, ruff format --check and pytest green; one commit with the given message.
- Tests never call the network: Telegram via `tests/mocked_bot.py`, DB via `tmp_path`.
- No feature, option or file beyond this plan (`_config/engineering-rules.md`, Scope discipline).

## Review Focus

1. `1 200 taxi` (a number typed with a space) must be rejected, never saved as 1.00 EUR. Test: Task 3.
2. A USD/UAH entry before any rate exists must be saved as pending, excluded from totals with a visible count, and converted by `/rate`. Tests: Tasks 6, 8, 9, 12.
3. The daily job running twice, or after a missed day, must send exactly one summary per month; a failed send must not be marked as sent. Test: Task 13.
4. A message from anyone except the owner, or from a group, must get no reply and store nothing. Test: Task 12.
5. `take` above the balance, `/undo` twice, `/undo` on an empty ledger: clear message, data unchanged. Tests: Tasks 7, 8, 12.

## File map

| File | Responsibility | Task |
|---|---|---|
| `app/pyproject.toml`, `requirements*.txt`, `.env.example` | packaging, pins, ruff/pytest config | 1 |
| `app/finbot/config.py` | settings from env and `.env` | 1 |
| `app/finbot/money.py` | parse/format cents, convert to EUR | 2 |
| `app/finbot/parser.py` | one-line entry grammar | 3 |
| `app/finbot/db.py`, `app/finbot/schema.sql` | connection, schema v1, default categories | 4 |
| `app/finbot/categories.py` | categories and keyword memory | 5 |
| `app/finbot/rates.py` | manual rates, pending conversion | 6 |
| `app/finbot/savings.py` | pots, goals, moves | 7 |
| `app/finbot/ledger.py` | add, categorize, delete, undo, history | 8 |
| `app/finbot/reports.py` | month report data and text | 9 |
| `app/finbot/export.py` | CSV export | 10 |
| `app/finbot/texts.py` | every user-facing reply string | 11 |
| `app/finbot/bot/` (`access.py`, `keyboards.py`, `handlers.py`, `app.py`), `app/tests/mocked_bot.py` | Telegram layer | 12 |
| `app/finbot/jobs.py` | backup and monthly summary | 13 |
| `app/finbot/__main__.py`, `app/finbot/bot/session.py`, entry in `jobs.py` | run polling, IPv4 session, `python -m finbot.jobs daily` | 14 |
| `app/deploy/*` | systemd units, deploy script | 15 |

## Waves (tasks in one wave run in parallel; files never overlap)

| Wave | Tasks | Day |
|---|---|---|
| 1 | 1 | Mon 2.11 |
| 2 | 2, 4 | Mon 2.11 |
| 3 | 3, 5, 6 | Mon 2.11 |
| 4 | 7, 8 | Tue 3.11 |
| 5 | 9, 10, 11 | Tue 3.11 |
| 6 | 12, 13 | Wed 4.11 |
| 7 | 14, 15 | Wed 4.11 |
| QA, acceptance, release | stages 05 and 06 | Thu 5.11 - Fri 6.11 |

Shared test fixture (Task 4 adds it to `app/tests/conftest.py`): `conn` = `db.connect(tmp_path / "t.db")`. Later tasks may add fixtures to their own test files only.

---

### Task 1: Scaffold and config

**Files:**
- Create: `app/pyproject.toml`, `app/requirements.txt`, `app/requirements-dev.txt`, `app/.env.example`, `app/finbot/__init__.py`, `app/finbot/config.py`, `app/tests/__init__.py`, `app/tests/test_config.py`

**Interfaces:**
- Produces: `ConfigError(Exception)`; `@dataclass(frozen=True) Settings(bot_token: str, owner_id: int, db_path: Path, backup_dir: Path)`; `TZ: ZoneInfo = ZoneInfo("Europe/Vienna")`; `read_env_file(path: Path) -> dict[str, str]`; `load_settings(env: Mapping[str, str]) -> Settings`.

- [ ] **Step 1: Tooling.** `pyproject.toml`: project `finbot`, `requires-python = ">=3.12"`; ruff `line-length = 100`, `target-version = "py312"`, lint `select = ["E", "F", "I", "B", "UP", "SIM"]`; pytest `asyncio_mode = "auto"`, `testpaths = ["tests"]`. `requirements.txt`: `aiogram==3.31.0`. `requirements-dev.txt`: `-r requirements.txt` plus pytest, pytest-asyncio, ruff pinned with `==` to the latest versions on the task date. `.env.example`: `BOT_TOKEN=`, `OWNER_ID=`, `DB_PATH=data/finbot.db`, `BACKUP_DIR=data/backups`. Create the venv: `~/.local/bin/uv venv --python 3.12 .venv && ~/.local/bin/uv pip install --python .venv/bin/python -r requirements-dev.txt`.
- [ ] **Step 2: Write failing tests** in `tests/test_config.py`:

```python
def test_load_settings_reads_keys_and_defaults():
    s = load_settings({"BOT_TOKEN": "123:abc", "OWNER_ID": "42"})
    assert (s.bot_token, s.owner_id) == ("123:abc", 42)
    assert s.db_path == Path("data/finbot.db") and s.backup_dir == Path("data/backups")

def test_missing_token_raises():  # message names the key
    with pytest.raises(ConfigError, match="BOT_TOKEN"):
        load_settings({"OWNER_ID": "42"})

def test_owner_id_must_be_integer():
    with pytest.raises(ConfigError, match="OWNER_ID"):
        load_settings({"BOT_TOKEN": "x", "OWNER_ID": "abc"})

def test_read_env_file_skips_comments_and_blanks(tmp_path):
    p = tmp_path / ".env"
    p.write_text("A=1\n# note\n\nB = two \n")
    assert read_env_file(p) == {"A": "1", "B": "two"}
```

- [ ] **Step 3: Run** `.venv/bin/pytest tests/test_config.py -q` - FAIL (import error).
- [ ] **Step 4: Implement** `config.py` per Interfaces. Empty values count as missing.
- [ ] **Step 5: Run** `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pytest -q` - all pass.
- [ ] **Step 6: Commit** `chore: scaffold finbot package and config`

### Task 2: Money

**Files:** Create `app/finbot/money.py`, `app/tests/test_money.py`

**Interfaces:**
- Produces: `CURRENCIES = ("EUR", "USD", "UAH")`; `SYMBOLS = {"€": "EUR", "$": "USD", "₴": "UAH"}`; `MAX_CENTS = 1_000_000_000`; `parse_amount(text: str) -> int` (raises `ValueError`); `format_cents(cents: int) -> str`; `signed(cents: int, positive: bool) -> str`; `to_eur(cents: int, rate: Decimal) -> int`.

- [ ] **Step 1: Failing tests:**

```python
@pytest.mark.parametrize("text,cents", [("25", 2500), ("12,50", 1250), ("12.5", 1250),
                                        ("0.01", 1), ("10000000", 1_000_000_000)])
def test_parse_amount(text, cents): assert parse_amount(text) == cents

@pytest.mark.parametrize("text", ["", "0", "-5", "1.234", "1,2,3", "10000000.01", "abc", "1e3", "1 200"])
def test_parse_amount_rejects(text):
    with pytest.raises(ValueError): parse_amount(text)

def test_format(): assert (format_cents(120000), format_cents(-2500), format_cents(5)) == ("1,200.00", "-25.00", "0.05")
def test_signed(): assert (signed(2500, False), signed(300000, True)) == ("-25.00", "+3,000.00")
def test_to_eur(): assert (to_eur(120000, Decimal("0.0220")), to_eur(2500, Decimal("0.92")), to_eur(1, Decimal("0.5"))) == (2640, 2300, 1)
```

- [ ] **Step 2: Run** `.venv/bin/pytest tests/test_money.py -q` - FAIL.
- [ ] **Step 3: Implement.** `parse_amount`: regex `^\d+([.,]\d{1,2})?$`, then `Decimal` with `.`; reject 0 and above `MAX_CENTS`.
- [ ] **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: money parsing and formatting`

### Task 3: Entry parser

**Files:** Create `app/finbot/parser.py`, `app/tests/test_parser.py`

**Interfaces:**
- Consumes: `money.parse_amount`, `money.SYMBOLS`, `money.CURRENCIES`.
- Produces: `Kind = Literal["expense", "income", "save", "take"]`; `@dataclass(frozen=True) Entry(kind: Kind, amount_cents: int, currency: str, note: str, keyword: str, pot: str | None, on: date)`; `ParseError(ValueError)` whose `str()` is the user-facing message; `UNSUPPORTED = ("GBP", "CHF", "PLN", "CZK", "HUF", "TRY", "JPY")`; `parse_entry(text: str, today: date) -> Entry`.

Grammar (spec R1-R7, R15): tokens split on whitespace. `save`/`take` first token (case-insensitive) -> pot entry: amount, optional `eur`/`€`, one pot word (lowercased), optional date; note and keyword `""`. Otherwise: first token is the amount with optional leading `+` (income) and an optional attached symbol before or after; next token may be a currency code (any case) or symbol; the last token is a date (`yesterday`, `DD.MM`, `DD.MM.YYYY`) only if at least one note word remains; the rest is the note. Keyword = first note word lowercased.

Error messages (exact):
- no note: `Add a word after the amount, e.g. 25 coffee`
- first token not an amount: `Start with the amount, e.g. 25 coffee`
- first note word all digits: `Write 1200 without spaces, e.g. 1200 taxi`
- unsupported code: `GBP is not supported. Use EUR, USD or UAH` (code uppercased)
- bad date: `Use a date like 28.10 or 28.10.2026`
- bad pot syntax: `Use: save 200 emergency`
- pot currency not EUR: `Pots are in EUR for now`
- bad amount: `Amount must be like 25 or 12,50`

- [ ] **Step 1: Failing tests** with `TODAY = date(2026, 11, 1)`:

```python
@pytest.mark.parametrize("text,expected", [
    ("25 coffee", Entry("expense", 2500, "EUR", "coffee", "coffee", None, TODAY)),
    ("12,50 Lunch at work", Entry("expense", 1250, "EUR", "Lunch at work", "lunch", None, TODAY)),
    ("+3000 salary", Entry("income", 300000, "EUR", "salary", "salary", None, TODAY)),
    ("1200 uah taxi", Entry("expense", 120000, "UAH", "taxi", "taxi", None, TODAY)),
    ("25 coffee yesterday", Entry("expense", 2500, "EUR", "coffee", "coffee", None, date(2026, 10, 31))),
    ("25 coffee 15.11", Entry("expense", 2500, "EUR", "coffee", "coffee", None, date(2025, 11, 15))),
    ("25 yesterday", Entry("expense", 2500, "EUR", "yesterday", "yesterday", None, TODAY)),
    ("save 200 emergency", Entry("save", 20000, "EUR", "", "", "emergency", TODAY)),
    ("take 50 Emergency", Entry("take", 5000, "EUR", "", "", "emergency", TODAY)),
])
def test_parse(text, expected): assert parse_entry(text, TODAY) == expected

@pytest.mark.parametrize("text", ["€25 coffee", "25€ coffee", "25 € coffee", "25 EUR coffee"])
def test_eur_forms(text): assert parse_entry(text, TODAY).currency == "EUR"

@pytest.mark.parametrize("text,cur", [("25 usd book", "USD"), ("$5 tip", "USD"), ("₴100 metro", "UAH")])
def test_currencies(text, cur): assert parse_entry(text, TODAY).currency == cur

def test_dates():
    assert parse_entry("25 coffee 28.10", TODAY).on == date(2026, 10, 28)
    assert parse_entry("25 coffee 28.10.2025", TODAY).on == date(2025, 10, 28)

@pytest.mark.parametrize("text,msg", [
    ("25", "Add a word after the amount"), ("coffee 25", "Start with the amount"),
    ("1 200 taxi", "Write 1200 without spaces"), ("25 gbp beer", "GBP is not supported"),
    ("25 coffee 31.02", "Use a date like"), ("save emergency", "Use: save 200 emergency"),
    ("save 200 usd emergency", "Pots are in EUR"), ("25.999 x", "Amount must be like"),
])
def test_errors(text, msg):
    with pytest.raises(ParseError, match=msg): parse_entry(text, TODAY)
```

- [ ] **Step 2: Run** `.venv/bin/pytest tests/test_parser.py -q` - FAIL.
- [ ] **Step 3: Implement** `parse_entry` per grammar.
- [ ] **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: parse one-line entries`

### Task 4: Database

**Files:** Create `app/finbot/db.py`, `app/finbot/schema.sql`, `app/tests/conftest.py`, `app/tests/test_db.py`

**Interfaces:**
- Produces: `connect(path: Path) -> sqlite3.Connection` (creates parent dir, `row_factory = sqlite3.Row`, `PRAGMA foreign_keys = ON`, `journal_mode = WAL`, applies `schema.sql` when `user_version` is 0 and sets it to 1); fixture `conn`.

Schema v1 (`schema.sql`, exact tables):

```sql
CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL CHECK (kind IN ('expense','income')), position INTEGER NOT NULL);
CREATE TABLE keywords (word TEXT PRIMARY KEY, category_id INTEGER NOT NULL REFERENCES categories(id));
CREATE TABLE rates (id INTEGER PRIMARY KEY, currency TEXT NOT NULL CHECK (currency IN ('USD','UAH')),
  eur_per_unit TEXT NOT NULL, set_on TEXT NOT NULL);
CREATE TABLE pots (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, goal_cents INTEGER CHECK (goal_cents > 0));
CREATE TABLE entries (id INTEGER PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('expense','income','save','take')),
  amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
  currency TEXT NOT NULL CHECK (currency IN ('EUR','USD','UAH')),
  rate TEXT, eur_cents INTEGER,
  category_id INTEGER REFERENCES categories(id), pot_id INTEGER REFERENCES pots(id),
  keyword TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT '',
  occurred_on TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  deleted_at TEXT,
  CHECK ((kind IN ('save','take')) = (pot_id IS NOT NULL)));
CREATE INDEX entries_on ON entries(occurred_on) WHERE deleted_at IS NULL;
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
```

Followed by `INSERT INTO categories (name, kind, position)` for spec R8 in that order: 12 expense (positions 1-12), 3 income (1-3). EUR entries store `rate = NULL`, `eur_cents = amount_cents`. Pending = `currency != 'EUR' AND eur_cents IS NULL`.

- [ ] **Step 1: Failing tests:** schema created (`user_version == 1`, tables exist, 12 expense + 3 income categories); `connect` twice on one file keeps 15 categories; `PRAGMA foreign_keys` returns 1; inserting `amount_cents = 0` raises `sqlite3.IntegrityError`; a `save` entry without `pot_id` raises `IntegrityError`.
- [ ] **Step 2: Run** `.venv/bin/pytest tests/test_db.py -q` - FAIL.
- [ ] **Step 3: Implement** `db.py`, `schema.sql`, the `conn` fixture in `conftest.py`. `schema.sql` is read with `importlib.resources`.
- [ ] **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: sqlite schema and connection`

### Task 5: Categories

**Files:** Create `app/finbot/categories.py`, `app/tests/test_categories.py`

**Interfaces:**
- Consumes: fixture `conn`.
- Produces: `@dataclass(frozen=True) Category(id: int, name: str, kind: str)`; `list_categories(conn, kind: str) -> list[Category]` (by position); `get_category(conn, category_id: int) -> Category`; `category_for_keyword(conn, word: str, kind: str) -> Category | None` (None when unmapped or mapped to the other kind); `remember_keyword(conn, word: str, category_id: int) -> None` (upsert).

- [ ] **Step 1: Failing tests:** `[c.name for c in list_categories(conn, "expense")] == ["Groceries", "Eating out", "Transport", "Housing", "Utilities", "Health", "Shopping", "Entertainment", "Travel", "Subscriptions", "Gifts", "Other"]`; income list `["Salary", "Freelance", "Other income"]`; remember `coffee` -> Eating out then `category_for_keyword(conn, "coffee", "expense").name == "Eating out"`; remembering `coffee` -> Groceries overwrites; `salary` mapped to Salary returns None for kind `expense`.
- [ ] **Step 2: Run** - FAIL. **Step 3: Implement.** **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: categories and keyword memory`

### Task 6: Exchange rates

**Files:** Create `app/finbot/rates.py`, `app/tests/test_rates.py`

**Interfaces:**
- Consumes: `money.to_eur`, fixture `conn`.
- Produces: `parse_rate(text: str) -> Decimal` (accepts `,`; > 0; at most 6 decimals; `ValueError` otherwise); `rate_on(conn, currency: str, on: date) -> Decimal | None` (latest `set_on <= on`, ties by highest id); `set_rate(conn, currency: str, eur_per_unit: Decimal, on: date) -> int` (stores the rate, converts every non-deleted pending entry of that currency with it: `rate`, `eur_cents = to_eur(amount_cents, rate)`; returns the number converted).

- [ ] **Step 1: Failing tests:** `parse_rate("0.92") == Decimal("0.92")`, `parse_rate("0,022") == Decimal("0.022")`, rejects `"0"`, `"-1"`, `"abc"`, `"0.1234567"`; `rate_on(conn, "USD", date(2026, 11, 5))` is None before any rate; after `set_rate(conn, "USD", Decimal("0.92"), date(2026, 11, 1))` it is `Decimal("0.92")`, and `rate_on(..., date(2026, 10, 31))` is None; with rates on 1.11 (0.92) and 3.11 (0.93), `rate_on(..., 2.11) == 0.92` and `rate_on(..., 4.11) == 0.93`; a pending USD entry of 2500 (insert by SQL) becomes `eur_cents == 2300`, `rate == "0.92"`, `set_rate` returns 1, while a pending UAH entry and a deleted pending USD entry stay untouched.
- [ ] **Step 2: Run** - FAIL. **Step 3: Implement.** **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: manual exchange rates`

### Task 7: Savings pots

**Files:** Create `app/finbot/savings.py`, `app/tests/test_savings.py`

**Interfaces:**
- Consumes: `parser.Entry`, `money.format_cents`, fixture `conn`.
- Produces: `SavingsError(ValueError)`; `@dataclass(frozen=True) Pot(id: int, name: str, total_cents: int, goal_cents: int | None)`; `@dataclass(frozen=True) PotMove(entry_id: int, kind: str, amount_cents: int, on: date)`; `apply_pot_entry(conn, entry: Entry) -> tuple[int, Pot]` (inserts the `save`/`take` entry with `currency = 'EUR'`, `eur_cents = amount_cents`; returns the new entry id and the pot after the move); `set_goal(conn, name: str, goal_cents: int) -> Pot`; `get_pot(conn, name: str) -> Pot | None`; `list_pots(conn) -> list[Pot]` (by name); `recent_moves(conn, pot_id: int, limit: int = 5) -> list[PotMove]` (newest first). Total = sum of `save` minus sum of `take`, deleted excluded.

Error messages (exact): unknown pot on take or goal: `No pot named emergency yet. Start it with: save 100 emergency`; over balance: `Emergency has 150.00 EUR, cannot take 200.00` (pot name capitalized).

- [ ] **Step 1: Failing tests:** save 200 -> total 20000, pot created; save 100 -> 30000; take 50 -> 25000; take 999 -> `SavingsError` and entry count unchanged; take from unknown pot -> `SavingsError`; `set_goal(conn, "emergency", 1_000_000).goal_cents == 1_000_000`; goal on unknown pot -> `SavingsError`; 6 moves -> `recent_moves` returns 5 newest; a soft-deleted move is excluded from the total.
- [ ] **Step 2: Run** - FAIL. **Step 3: Implement.** **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: savings pots`

### Task 8: Ledger

**Files:** Create `app/finbot/ledger.py`, `app/tests/test_ledger.py`

**Interfaces:**
- Consumes: `parser.Entry`; `categories.category_for_keyword`, `categories.remember_keyword`; `rates.rate_on`; `money.to_eur`.
- Produces: `@dataclass(frozen=True) Record(id: int, kind: str, amount_cents: int, currency: str, rate: Decimal | None, eur_cents: int | None, category: str | None, pot: str | None, keyword: str, note: str, on: date)` with property `pending: bool` (`eur_cents is None`); `add_transaction(conn, entry: Entry) -> Record` (expense/income only); `get_record(conn, entry_id: int) -> Record | None` (None if deleted); `set_category(conn, entry_id: int, category_id: int) -> Record` (also remembers the keyword when non-empty); `delete_entry(conn, entry_id: int) -> Record | None` (soft delete; None if missing or already deleted); `undo_last(conn) -> Record | None` (deletes the newest non-deleted entry by id, any kind); `last_records(conn, limit: int = 10) -> list[Record]` (newest first); `records_between(conn, start: date, end: date) -> list[Record]` (inclusive, not deleted, by date then id); `all_records(conn) -> list[Record]` (not deleted, by date then id).

- [ ] **Step 1: Failing tests** (entries built with `parse_entry(..., date(2026, 11, 1))`): `25 coffee` -> category None, `eur_cents == 2500`, `rate is None`; after remembering coffee -> Eating out, a new `25 coffee` gets `category == "Eating out"`; with UAH rate 0.022, `1200 uah taxi` -> `eur_cents == 2640`, `rate == Decimal("0.022")`; `25 usd book` without a rate -> `pending is True`; `set_category` changes the record and the keyword memory; `delete_entry` twice -> second returns None; `undo_last` returns the newest, the next call the one before, on empty ledger None; 12 records -> `last_records` returns 10, newest first; `records_between` excludes deleted and out-of-range records and includes a pot move with `pot == "emergency"`.
- [ ] **Step 2: Run** - FAIL. **Step 3: Implement.** **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: ledger records, undo and history`

### Task 9: Month report

**Files:** Create `app/finbot/reports.py`, `app/tests/test_reports.py`

**Interfaces:**
- Consumes: `ledger.records_between`, `ledger.Record`, `savings.list_pots`, `savings.Pot`, `money.format_cents`.
- Produces: `@dataclass(frozen=True) MonthReport(year: int, month: int, income_cents: int, spent_cents: int, saved_cents: int, net_cents: int, prev_spent_cents: int, by_category: list[tuple[str, int]], top: list[Record], pots: list[Pot], pending: int)`; `parse_month_arg(arg: str | None, today: date) -> tuple[int, int]` (`None`/`""` -> current month; `"10"` -> that month of this year, or last year if it is in the future; `"2026-10"`; `ValueError` otherwise); `build_month_report(conn, year: int, month: int) -> MonthReport`; `render_month(r: MonthReport) -> str`.

Rules: totals from `eur_cents` of non-pending records; `saved` = save minus take; `net = income - spent - saved`; expenses without category grouped as `Uncategorized`; `by_category` sorted by amount desc then name; `top` = 5 largest expenses (amount desc, then date); `pending` = pending records in the month.

Render rules: month name and year; blank line; totals block, label `ljust(6)` + space + amount `rjust` to the widest of the four + ` EUR`, the Spent line adds two spaces and `▲ 6% vs Sep` / `▼ 6% vs Sep` (percent half-up of the change vs the previous month; omitted when previous spent is 0); blank line; category block, name `ljust` to the longest name, two spaces, amount `rjust` to the widest, two spaces, bar of `█` `ljust(12)` (largest = 12, others `round_half_up(12 * amount / largest)`, minimum 1), two spaces, percent of spent half-up; blank line; `Top expenses` then `DD.MM  amount  note`; blank line; `Savings` then `Name  total` plus ` / goal (pct%)` when a goal exists; when `pending > 0` a final line `Not counted: N pending (no rate). Use /rate to convert.` A month with no records renders `October 2026\n\nNo entries.`

- [ ] **Step 1: Failing tests.** `parse_month_arg` with today 1.11.2026: `None -> (2026, 11)`, `"10" -> (2026, 10)`, `"12" -> (2025, 12)`, `"2026-09" -> (2026, 9)`, `"13"` raises. Golden test: September expense 174500; October: income 300000 `salary` 01.10, expenses Housing 93000 `rent` 01.10, Groceries 42000 `billa` 03.10, Eating out 31000 `dinner` 10.10, Transport 19000 `ticket` 15.10, save 40000 to `emergency` 05.10 with an earlier September save 100000 and goal 1000000. `render_month(build_month_report(conn, 2026, 10))` equals:

```text
October 2026

Income 3,000.00 EUR
Spent  1,850.00 EUR  ▲ 6% vs Sep
Saved    400.00 EUR
Net      750.00 EUR

Housing     930.00  ████████████  50%
Groceries   420.00  █████         23%
Eating out  310.00  ████          17%
Transport   190.00  ██            10%

Top expenses
01.10  930.00  rent
03.10  420.00  billa
10.10  310.00  dinner
15.10  190.00  ticket

Savings
Emergency  1,400.00 / 10,000.00 (14%)
```

Plus: a pending USD expense in October is excluded from Spent and adds the line `Not counted: 1 pending (no rate). Use /rate to convert.`; an empty month renders `No entries.`
- [ ] **Step 2: Run** - FAIL. **Step 3: Implement.** **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: month report`

### Task 10: CSV export

**Files:** Create `app/finbot/export.py`, `app/tests/test_export.py`

**Interfaces:**
- Consumes: `ledger.all_records`.
- Produces: `export_csv(conn) -> bytes` (UTF-8, `csv` module, `lineterminator="\n"`, header `date,type,amount,currency,rate,amount_eur,category,note,pot`; amounts as `25.00` without thousands separator; empty string for missing rate, pending `amount_eur`, category, pot).

- [ ] **Step 1: Failing test:** records `25 coffee` (Eating out, 1.11), pending `25 usd book`, `save 200 emergency`, a deleted entry, and a note `lunch, work`. Expected bytes:

```text
date,type,amount,currency,rate,amount_eur,category,note,pot
2026-11-01,expense,25.00,EUR,,25.00,Eating out,coffee,
2026-11-01,expense,25.00,USD,,,,book,
2026-11-01,save,200.00,EUR,,200.00,,,emergency
2026-11-01,expense,12.00,EUR,,12.00,,"lunch, work",
```

- [ ] **Step 2: Run** - FAIL. **Step 3: Implement.** **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: csv export`

### Task 11: Reply texts

**Files:** Create `app/finbot/texts.py`, `app/tests/test_texts.py`

**Interfaces:**
- Consumes: `ledger.Record`, `savings.Pot`, `savings.PotMove`, `money.signed`, `money.format_cents`.
- Produces: `HELP: str`; `saved_text(r: Record) -> str`; `pot_text(pot: Pot, kind: str, amount_cents: int) -> str`; `removed_text(r: Record) -> str`; `NOTHING_TO_UNDO = "Nothing to undo."`; `rate_set_text(currency: str, rate: Decimal, converted: int) -> str`; `savings_text(pots: list[Pot], moves: dict[int, list[PotMove]]) -> str`; `last_text(records: list[Record]) -> str`; `as_pre(text: str) -> str` (`<pre>` + `html.escape` + `</pre>`).

Exact strings:
- `saved_text`: line 1 `Saved: {signed} {CUR}` + (for non-EUR converted: ` (≈ {signed eur} EUR at {rate})`) + ` · {note}` + (` → {category}` when set). If pending, line 2 `No {CUR} rate yet. Send /rate {cur} <EUR per 1 {CUR}> and I will convert it.` If no category, last line `New word "{keyword}" - pick a category:`.
- `pot_text`: `Emergency pot: +200.00 EUR · total 1,400.00 EUR` (take uses `-`).
- `removed_text`: `Removed: -25.00 EUR · coffee` (pot moves: `Removed: +200.00 EUR · emergency pot`).
- `rate_set_text`: `USD rate set: 0.92 EUR.` and, when converted > 0, ` Converted 1 pending entry.` / ` Converted 3 pending entries.`
- `savings_text`: per pot `Emergency: 1,400.00 EUR` + ` of 10,000.00 (14%)` when goal; then up to 5 lines `  05.10 +400.00`; no pots -> `No pots yet. Start one with: save 100 emergency`.
- `last_text`: numbered lines `1. 01.11 -25.00 EUR coffee → Eating out` (pot moves: `2. 01.11 +200.00 EUR emergency pot`); empty -> `No entries yet.`
- `HELP`: 8 lines showing `25 coffee`, `1200 uah taxi`, `+3000 salary`, `25 coffee yesterday`, `save 200 emergency`, `/rate usd 0.92`, `/month`, `/undo /last /savings /goal /export`.

- [ ] **Step 1: Failing tests** for each function with the exact strings above, including spec R11 examples `Saved: -25.00 EUR · coffee → Eating out` and `Saved: -1,200.00 UAH (≈ -26.40 EUR at 0.0220) · taxi → Transport`.
- [ ] **Step 2: Run** - FAIL. **Step 3: Implement.** **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: reply texts`

### Task 12: Telegram layer

**Files:** Create `app/finbot/bot/__init__.py`, `app/finbot/bot/access.py`, `app/finbot/bot/keyboards.py`, `app/finbot/bot/handlers.py`, `app/finbot/bot/app.py`, `app/tests/mocked_bot.py`, `app/tests/test_bot.py`

**Interfaces:**
- Consumes: everything from Tasks 3, 5-11.
- Produces: `class OwnerOnly(BaseMiddleware)` (`__init__(owner_id: int)`; handlers run only for that user in a private chat; otherwise nothing is called and nothing is sent); `class EntryCb(CallbackData, prefix="e")` with `action: str` (`cat`, `undo`, `del`) and `entry_id: int`; `class PickCb(CallbackData, prefix="p")` with `entry_id: int`, `category_id: int`; `entry_keyboard(entry_id: int) -> InlineKeyboardMarkup` (`[Change category] [Undo]`); `category_keyboard(entry_id: int, categories: list[Category]) -> InlineKeyboardMarkup` (3 per row); `last_keyboard(records: list[Record]) -> InlineKeyboardMarkup` (per record a row `[#n category] [#n delete]`, pot moves only `[#n delete]`); `router: Router`; `build_dispatcher(conn: sqlite3.Connection, owner_id: int, today: Callable[[], date]) -> Dispatcher` (conn and today passed as workflow data).

Behaviour: plain text -> `parse_entry` -> `add_transaction` or `apply_pot_entry` -> reply `saved_text` with `entry_keyboard`, or `category_keyboard` when uncategorized; `ParseError`/`SavingsError` -> reply its message. Callback `PickCb` -> `set_category`, edit the message to the new `saved_text` with `entry_keyboard`. `EntryCb cat` -> show `category_keyboard`. `EntryCb undo`/`del` -> `delete_entry`, edit to `removed_text`. Every callback is answered. Commands: `/start` `/help` -> `HELP`; `/undo`; `/last`; `/month [arg]` -> `as_pre(render_month(...))` with `parse_mode="HTML"`; `/rate <code> <value>` (`Use: /rate usd 0.92` on bad input); `/savings`; `/goal <pot> <amount>` (`Use: /goal emergency 10000`); `/export` -> document `finbot-export-YYYY-MM-DD.csv`.

`tests/mocked_bot.py`: a `MockedBot` with a session that records every API request and returns canned results, adapted from aiogram's own `tests/mocked_bot.py` (aiogram repo, branch `dev-3.x`). Tests feed `Update` objects through `dispatcher.feed_update`.

- [ ] **Step 1: Failing tests** (owner id 42, today 1.11.2026):
  - owner sends `25 coffee` -> one `SendMessage` whose text starts `Saved: -25.00 EUR · coffee` and ends `New word "coffee" - pick a category:`, keyboard has 12 category buttons, 1 entry in DB;
  - user 7 sends `25 coffee` -> zero requests, zero entries; owner in a group chat -> zero requests, zero entries;
  - `PickCb(entry_id=1, category_id=<Eating out>)` -> `EditMessageText` with `Saved: -25.00 EUR · coffee → Eating out`, `AnswerCallbackQuery` sent, keyword remembered;
  - `1200 uah taxi` -> reply contains `No UAH rate yet`; `/rate uah 0.022` -> `UAH rate set: 0.022 EUR. Converted 1 pending entry.`;
  - `/undo` twice after one entry -> `Removed: ...` then `Nothing to undo.`;
  - `1 200 taxi` -> `Write 1200 without spaces, e.g. 1200 taxi`, zero entries;
  - `take 999 emergency` after `save 200 emergency` -> the over-balance message, pot total unchanged;
  - `/month` -> `SendMessage` with `parse_mode == "HTML"` and text starting `<pre>November 2026`;
  - `/export` -> `SendDocument` with filename `finbot-export-2026-11-01.csv`;
  - every `callback_data` produced by the keyboards is at most 64 bytes.
- [ ] **Step 2: Run** `.venv/bin/pytest tests/test_bot.py -q` - FAIL.
- [ ] **Step 3: Implement.** Handlers stay thin: parse, call one domain function, reply with a `texts` function.
- [ ] **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: telegram handlers and owner-only access`

### Task 13: Daily job: backup and monthly summary

**Files:** Create `app/finbot/jobs.py`, `app/tests/test_jobs.py`

**Interfaces:**
- Consumes: `reports.build_month_report`, `reports.render_month`, `export.export_csv`, `texts.as_pre`; tests pass a `MockedBot` from `tests/mocked_bot.py`.
- Produces: `backup_db(conn, backup_dir: Path, today: date, keep: int = 14) -> Path` (`sqlite3` backup API to `finbot-YYYY-MM-DD.db`, then removes the oldest `finbot-*.db` beyond `keep`); `previous_month(today: date) -> tuple[int, int]`; `async send_monthly_summary(bot: Bot, conn, owner_id: int, today: date) -> bool`. The command-line entry is added in Task 14.

Rules: due when meta key `summary_sent:YYYY-MM` for the previous month is missing. A previous month with no records: set the key, send nothing, return False. Otherwise send `as_pre(render_month(...))` (HTML) and the CSV document `finbot-export-YYYY-MM-DD.csv`; set the key only after both calls succeed; return True.

- [ ] **Step 1: Failing tests:** `previous_month(date(2026, 11, 1)) == (2026, 10)` and `previous_month(date(2026, 1, 15)) == (2025, 12)`; backup creates `finbot-2026-11-01.db` readable by `sqlite3`; with 15 older backup files present only 14 files remain and the newest is kept; summary with October records -> True, 2 requests (`SendMessage`, `SendDocument`); called again -> False, no requests; empty October -> False, no requests, key set; when the mocked `SendDocument` raises, the key is not set and the next call sends again.
- [ ] **Step 2: Run** - FAIL. **Step 3: Implement.** **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `feat: daily backup and monthly summary`

### Task 14: Runner with IPv4 session

**Files:** Create `app/finbot/bot/session.py`, `app/finbot/__main__.py`, `app/tests/test_runner.py`; Modify `app/finbot/jobs.py` (add the command-line entry only)

**Interfaces:**
- Consumes: `config.load_settings`, `config.read_env_file`, `config.TZ`, `db.connect`, `build_dispatcher`, `jobs.backup_db`, `jobs.send_monthly_summary`.
- Produces: `build_bot(token: str) -> Bot` in `bot/session.py`, whose HTTP session connects over IPv4 only (`socket.AF_INET`). Both entry points build settings the same way: `os.environ` overlaid on `read_env_file(Path(".env"))` when the file exists. `main() -> None` in `__main__.py`: settings, `connect(settings.db_path)`, dispatcher with `today = lambda: datetime.now(TZ).date()`, `start_polling`. In `jobs.py`: `python -m finbot.jobs daily` runs `backup_db` then `send_monthly_summary` with today in Europe/Vienna, closes the bot session, exits 1 on any exception after logging it.

- [ ] **Step 1: Failing tests:** the session of `build_bot("1:x")` creates its connector with `family == socket.AF_INET` (read `aiogram/client/session/aiohttp.py` in the installed aiogram 3.31.0 first and assert on the attribute it actually uses for connector arguments; name it in the report); `python -m finbot.jobs` without the `daily` argument exits with code 2.
- [ ] **Step 2: Run** - FAIL. **Step 3: Implement.** **Step 4: Run** full checks - pass, and `.venv/bin/python -c "import finbot.__main__, finbot.jobs"` imports without error.
- [ ] **Step 5: Commit** `feat: polling runner, daily job entry, ipv4 session`

### Task 15: Deploy kit

**Files:** Create `app/deploy/finance-bot.service`, `app/deploy/finance-bot-daily.service`, `app/deploy/finance-bot-daily.timer`, `app/deploy/deploy.sh`, `app/tests/test_deploy_files.py`

**Interfaces:**
- Produces: unit `finance-bot.service` (`WorkingDirectory=/opt/finance-bot`, `EnvironmentFile=/opt/finance-bot/.env`, `ExecStart=/opt/finance-bot/.venv/bin/python -m finbot`, `Restart=always`, `RestartSec=5`); `finance-bot-daily.service` (`Type=oneshot`, `ExecStart=/opt/finance-bot/.venv/bin/python -m finbot.jobs daily`); `finance-bot-daily.timer` (`OnCalendar=*-*-* 09:00:00 Europe/Vienna`, `Persistent=true`); `deploy.sh` with only `--dry-run` as an optional argument.

`deploy.sh`, modeled on `~/Desktop/Projects/job-digest/scripts/deploy.sh` (read it first; do not run it): host from `FINBOT_HOST` (default `the server`); refuse to run with uncommitted changes; rsync `app/` to `/opt/finance-bot/` excluding `.env`, `data/`, `.venv/`, `__pycache__/`; on the server: back up `data/finbot.db` to `/opt/finance-bot-backups/<timestamp>/`, create or update the venv from `requirements.txt`, run `pytest -q` with dev requirements in a temporary venv, check `.env` has `BOT_TOKEN` and `OWNER_ID` keys without printing values, check `+x` on `deploy.sh`, install units, `daemon-reload`, restart `finance-bot.service`, enable the timer, print `systemctl is-active` and the rollback command. `--dry-run` prints every step and changes nothing.

- [ ] **Step 1: Failing tests:** unit files contain the exact lines above; `bash -n deploy/deploy.sh` exits 0; `deploy.sh` contains `--dry-run`, `--exclude .env`, `--exclude data/` and no token-like string.
- [ ] **Step 2: Run** - FAIL. **Step 3: Implement.** Do not run `deploy.sh` against the server. **Step 4: Run** full checks - pass.
- [ ] **Step 5: Commit** `chore: systemd units and deploy script`

---

## After the tasks (product owner, not developers)

1. **QA (stage 05, Thu 5.11):** one Sonnet QA pass on the whole phase: spec R1-R28, this Review Focus, `/code-review`, `/simplify` in report-only mode, extra scope. Findings to Misha.
2. **Local acceptance (Fri 6.11):** run `cd app && .venv/bin/python -m finbot` with the dev bot token in `app/.env`; Misha walks `stages/05_qa/references/acceptance-checklist-phase1.md`. Summary test: `python -m finbot.jobs daily` against a copy of the dev DB with a back-dated meta key cleared.
3. **Release (stage 06):** only after Misha's explicit approval: prod bot token entered by Misha into `/opt/finance-bot/.env`, `deploy.sh --dry-run`, `deploy.sh`, checks, release note.

## Self-review (writing-plans checklist, done 31.10.2026)

- Spec coverage: R1-R7 Task 3; R8-R10 Tasks 5, 8, 12; R11 Task 11; R12-R14 Tasks 6, 8, 11, 12; R15-R18 Tasks 7, 11, 12; R19-R20 Tasks 8, 12; R21-R22 Task 9; R23 Task 10; R24 Task 13; R25 Task 12; R26 Tasks 14, 15; R27 Tasks 13, 15; R28 Tasks 2, 4.
- Type consistency: `Entry`, `Record`, `Pot`, `PotMove`, `Category`, `MonthReport` names and fields are the same in every Interfaces block.
- Review Focus lines each have a test in the owning task.
