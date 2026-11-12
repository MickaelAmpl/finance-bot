"""One paid live check of the AI before deploy. Run by hand: python -m finbot.livetest."""

import argparse
import asyncio
import logging
import sqlite3
import sys
from collections.abc import Callable
from contextlib import closing
from datetime import date, datetime
from pathlib import Path
from typing import NoReturn

import anthropic
from anthropic import AsyncAnthropic

from finbot.ai_memory import Memory
from finbot.ai_prompt import build_system_prompt
from finbot.assistant import Answer, Failure, Proposal, TurnResult, run_turn
from finbot.bot.session import redact_token_in_logs
from finbot.budgets import set_budget
from finbot.categories import Category, find_category, remember_keyword
from finbot.config import TZ, read_env_file
from finbot.db import connect
from finbot.ledger import add_transaction, records_between
from finbot.money import format_cents
from finbot.parser import Entry
from finbot.reports import build_month_report
from finbot.savings import apply_pot_entry, get_pot, set_goal
from finbot.texts import draft_text

TEXTS: tuple[str, ...] = (
    "вчера 25 на кофе с другом",
    "исправь: не 25, а 30",
    "300 грн такси",
    "в пятницу 40 продукты в Billa",
    "зарплата 3000",
    "50 баксов такси в аэропорт",
    "20 фунтов обед",
    "кино 15 и попкорн 7",
    "позавчера аптека 12,80",
    "+200 фриланс за сайт",
)
QUESTIONS: tuple[str, ...] = (
    "сколько я потратил в октябре?",
    "сколько на Eating out в ноябре и сколько осталось до лимита?",
    "how much did I spend on groceries from 1 to 15 October?",
    "сколько в копилке emergency?",
    "какой доход был в сентябре?",
)
MODEL_TIMEOUT = anthropic.Timeout(45.0, connect=5.0)
_LAST_SEED_DAY = date(2026, 11, 10)
# A word per expense, cycled; the amount doubles on the second pass through the list.
_WORDS = (
    "billa",
    "cafe",
    "uber",
    "cinema",
    "apteka",
    "zara",
    "netflix",
    "gift",
    "electric",
    "misc",
)
_EUROS = (80, 12, 18, 15, 9, 60, 13, 25, 70, 6)
_CATEGORY_OF = {
    "billa": "Groceries",
    "cafe": "Eating out",
    "uber": "Transport",
    "cinema": "Entertainment",
    "apteka": "Health",
    "zara": "Shopping",
    "netflix": "Subscriptions",
    "gift": "Gifts",
    "electric": "Utilities",
    "salary": "Salary",
    "freelance": "Freelance",
}
_INCOMES = (
    (date(2026, 9, 25), "salary", 3000),
    (date(2026, 10, 20), "freelance", 200),
    (date(2026, 10, 25), "salary", 3000),
)
# Some inside 01.10-15.10 and some after it, so the window differs from all of October.
_GROCERIES_OCT = (
    (date(2026, 10, 12), 45),
    (date(2026, 10, 14), 35),
    (date(2026, 10, 17), 50),
    (date(2026, 10, 19), 40),
)


def build_synthetic_db(path: Path, today: date) -> dict[str, str]:
    if path.exists():
        raise FileExistsError(f"{path} already exists. Pick a new --db path.")
    if today < _LAST_SEED_DAY:
        raise ValueError("The synthetic data runs to 10.11.2026; run this on or after that day.")
    with closing(connect(path)) as conn:
        _teach_keywords(conn)
        _seed(conn)
        return _expected(conn)


async def run(
    client: AsyncAnthropic, conn: sqlite3.Connection, today: date, emit: Callable[[str], None]
) -> int:
    expected = _expected(conn)
    memory = Memory()
    failures = 0
    for message in (*TEXTS, *QUESTIONS):
        now = datetime.now(TZ)
        emit(f"> {message}")
        result = await run_turn(
            client,
            conn,
            system=build_system_prompt(conn, today),
            history=memory.history(now),
            user={"role": "user", "content": message},
            source="text",
            message_date=today,
            today=today,
        )
        reply = _reply_text(result)
        emit(reply)
        # As in the bot: a failed turn is not kept in memory.
        if isinstance(result, Failure):
            failures += 1
        else:
            memory.add(message, reply, now)
        if message in expected:
            emit(f"expected: {expected[message]}")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="One paid live check of the AI.")
    parser.add_argument("--env", required=True, type=Path, help="the .env file with the key")
    parser.add_argument("--db", required=True, type=Path, help="a new database file to create")
    args = parser.parse_args()
    key = read_env_file(args.env).get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        _exit("No ANTHROPIC_API_KEY in that file.")
    refusal = _db_refusal(args.env, args.db)
    if refusal is not None:
        _exit(refusal)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    redact_token_in_logs(key)
    for name in ("anthropic", "httpx2", "httpcore2"):
        logging.getLogger(name).setLevel(logging.WARNING)
    today = datetime.now(TZ).date()
    try:
        build_synthetic_db(args.db, today)
    except ValueError as error:
        _exit(str(error))
    client = AsyncAnthropic(
        api_key=key,
        base_url="https://api.anthropic.com",
        timeout=MODEL_TIMEOUT,
        max_retries=2,
    )
    with closing(connect(args.db)) as conn:
        failed = asyncio.run(run(client, conn, today, _print_now))
    total = len(TEXTS) + len(QUESTIONS)
    print(f"failed turns: {failed} of {total}", flush=True)
    if failed:
        sys.exit(1)


def _print_now(line: str) -> None:
    print(line, flush=True)


def _db_refusal(env: Path, db: Path) -> str | None:
    if db.exists() or Path(f"{db}-wal").exists() or Path(f"{db}-shm").exists():
        return f"{db} (or its -wal or -shm file) already exists. Pick a new --db path."
    if env.resolve().parent in db.resolve().parents:
        return "Keep --db outside the folder of the .env file, e.g. --db live-check.db"
    return None


def _exit(message: str) -> NoReturn:
    print(message, file=sys.stderr)
    sys.exit(2)


def _reply_text(result: TurnResult) -> str:
    if isinstance(result, Proposal):
        return draft_text(result.entries)
    if isinstance(result, Answer):
        return result.text
    assert isinstance(result, Failure)
    return result.reply


def _teach_keywords(conn: sqlite3.Connection) -> None:
    for word, name in _CATEGORY_OF.items():
        remember_keyword(conn, word, _category(conn, name).id)


def _seed(conn: sqlite3.Connection) -> None:
    for month in (9, 10, 11):
        for index in range(20):
            word = _WORDS[index % 10]
            euros = _EUROS[index % 10] * (1 + index // 10)
            on = date(2026, month, index % 10 + 1)
            add_transaction(conn, Entry("expense", euros * 100, "EUR", word, word, None, on))
    for on, word, euros in _INCOMES:
        add_transaction(conn, Entry("income", euros * 100, "EUR", word, word, None, on))
    for on, euros in _GROCERIES_OCT:
        add_transaction(conn, Entry("expense", euros * 100, "EUR", "billa", "billa", None, on))
    # No USD or UAH rate is set, so these two stay pending.
    add_transaction(conn, Entry("expense", 1240, "USD", "hotel", "hotel", None, date(2026, 11, 3)))
    add_transaction(conn, Entry("expense", 30000, "UAH", "taxi", "uber", None, date(2026, 11, 5)))
    apply_pot_entry(conn, Entry("save", 30000, "EUR", "", "", "emergency", date(2026, 9, 15)))
    apply_pot_entry(conn, Entry("save", 20000, "EUR", "", "", "emergency", date(2026, 10, 15)))
    set_goal(conn, "emergency", 200000)
    set_budget(conn, _category(conn, "Eating out"), 30000, 2026, 11)


def _expected(conn: sqlite3.Connection) -> dict[str, str]:
    october = build_month_report(conn, 2026, 10)
    november = build_month_report(conn, 2026, 11)
    september = build_month_report(conn, 2026, 9)
    eating = next(b for b in november.budgets if b.category == "Eating out")
    pot = get_pot(conn, "emergency")
    assert pot is not None
    groceries = sum(
        r.eur_cents or 0
        for r in records_between(conn, date(2026, 10, 1), date(2026, 10, 15))
        if r.kind == "expense" and r.category == "Groceries" and not r.pending
    )
    answers = (
        f"October spent: {_eur(october.spent_cents)}",
        f"Eating out in November: {_eur(eating.spent_cents)} spent,"
        f" {_eur(eating.left_cents)} left of {_eur(eating.limit_cents)}",
        f"Groceries 01.10-15.10: {_eur(groceries)}",
        f"Pot emergency: {_eur(pot.total_cents)}",
        f"Income in September: {_eur(september.income_cents)}",
    )
    return dict(zip(QUESTIONS, answers, strict=True))


def _eur(cents: int) -> str:
    return f"{format_cents(cents)} EUR"


def _category(conn: sqlite3.Connection, name: str) -> Category:
    category = find_category(conn, name)
    assert category is not None, name
    return category


if __name__ == "__main__":
    main()
