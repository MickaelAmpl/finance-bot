import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

import pytest
from aiogram.exceptions import TelegramServerError
from aiogram.methods import SendDocument, SendMessage
from aiogram.types import BufferedInputFile

from finbot.budgets import set_budget
from finbot.categories import MAX_NAME_LENGTH, add_category, list_categories, rename_category
from finbot.export import export_csv
from finbot.jobs import backup_db, previous_month, send_monthly_summary
from finbot.ledger import add_transaction, set_category
from finbot.parser import parse_entry
from finbot.reports import build_month_report, render_month
from finbot.texts import as_pre
from tests.mocked_bot import MockedBot

OWNER_ID = 42
TODAY = date(2026, 11, 1)
OCTOBER_KEY = "summary_sent:2026-10"


def add_october_entry(conn: sqlite3.Connection) -> None:
    add_transaction(conn, parse_entry("12 coffee", date(2026, 10, 5)))


def fill_long_month(conn: sqlite3.Connection, on: date) -> None:
    """All 30 expense categories get a 30-character name, a budget and an entry with a long note."""
    seeded = list_categories(conn, "expense")
    for number in range(30):
        name = f"{number:02d} ".ljust(MAX_NAME_LENGTH, "c")
        category = (
            rename_category(conn, seeded[number].id, name)
            if number < len(seeded)
            else add_category(conn, name, "expense")
        )
        set_budget(conn, category, 100000, on.year, on.month)
        entry = parse_entry(f"{10 + number} item{number} {'n' * 90}", on)
        set_category(conn, add_transaction(conn, entry).id, category.id)


def is_marked(conn: sqlite3.Connection, key: str) -> bool:
    return conn.execute("SELECT 1 FROM meta WHERE key = ?", (key,)).fetchone() is not None


def entry_count(path: Path) -> int:
    with closing(sqlite3.connect(path)) as raw:
        return int(raw.execute("SELECT COUNT(*) FROM entries").fetchone()[0])


def test_previous_month_is_the_month_before() -> None:
    assert previous_month(date(2026, 11, 1)) == (2026, 10)
    assert previous_month(date(2026, 1, 15)) == (2025, 12)


def test_backup_writes_dated_copy_readable_by_sqlite(
    conn: sqlite3.Connection, tmp_path: Path
) -> None:
    add_october_entry(conn)
    backup_dir = tmp_path / "backups"

    path = backup_db(conn, backup_dir, TODAY)

    assert path == backup_dir / "finbot-2026-11-01.db"
    assert entry_count(path) == 1


def test_backup_on_the_same_day_overwrites_the_file(
    conn: sqlite3.Connection, tmp_path: Path
) -> None:
    backup_dir = tmp_path / "backups"
    backup_db(conn, backup_dir, TODAY)
    add_october_entry(conn)

    path = backup_db(conn, backup_dir, TODAY)

    assert [p.name for p in backup_dir.iterdir()] == ["finbot-2026-11-01.db"]
    assert entry_count(path) == 1


def test_backup_keeps_only_the_newest_fourteen(conn: sqlite3.Connection, tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    for day in range(1, 16):
        (backup_dir / f"finbot-2026-10-{day:02d}.db").write_bytes(b"old")

    backup_db(conn, backup_dir, TODAY)

    expected = [f"finbot-2026-10-{day:02d}.db" for day in range(3, 16)]
    assert sorted(p.name for p in backup_dir.iterdir()) == [*expected, "finbot-2026-11-01.db"]


def test_backup_retention_never_touches_other_files(
    conn: sqlite3.Connection, tmp_path: Path
) -> None:
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    for day in range(1, 16):
        (backup_dir / f"finbot-2026-10-{day:02d}.db").write_bytes(b"old")
    others = ["notes.txt", "finbot-manual.db", "finbot-2026-10-01.db-wal"]
    for name in others:
        (backup_dir / name).write_bytes(b"keep me")

    backup_db(conn, backup_dir, TODAY)

    dated = [f"finbot-2026-10-{day:02d}.db" for day in range(3, 16)]
    assert sorted(p.name for p in backup_dir.iterdir()) == sorted(
        [*dated, "finbot-2026-11-01.db", *others]
    )


async def test_summary_sends_report_then_csv_and_marks_the_month(conn: sqlite3.Connection) -> None:
    add_october_entry(conn)
    bot = MockedBot()

    sent = await send_monthly_summary(bot, conn, OWNER_ID, TODAY)

    assert sent is True
    message, document = bot.requests
    assert isinstance(message, SendMessage)
    assert message.chat_id == OWNER_ID
    assert message.parse_mode == "HTML"
    assert message.text == as_pre(render_month(build_month_report(conn, 2026, 10)))
    assert isinstance(document, SendDocument)
    assert document.chat_id == OWNER_ID
    payload = document.document
    assert isinstance(payload, BufferedInputFile)
    assert payload.filename == "finbot-export-2026-11-01.csv"
    assert payload.data == export_csv(conn)
    assert is_marked(conn, OCTOBER_KEY)


async def test_second_run_for_the_same_month_sends_nothing(conn: sqlite3.Connection) -> None:
    add_october_entry(conn)
    bot = MockedBot()
    await send_monthly_summary(bot, conn, OWNER_ID, TODAY)
    requests_before = len(bot.requests)

    again = await send_monthly_summary(bot, conn, OWNER_ID, TODAY)

    assert again is False
    assert len(bot.requests) == requests_before


async def test_missed_days_still_send_the_summary_once(conn: sqlite3.Connection) -> None:
    add_october_entry(conn)
    bot = MockedBot()

    assert await send_monthly_summary(bot, conn, OWNER_ID, date(2026, 11, 4)) is True
    assert await send_monthly_summary(bot, conn, OWNER_ID, date(2026, 11, 5)) is False
    assert len(bot.requests) == 2


async def test_empty_month_marks_it_and_sends_nothing(conn: sqlite3.Connection) -> None:
    bot = MockedBot()

    sent = await send_monthly_summary(bot, conn, OWNER_ID, TODAY)

    assert sent is False
    assert bot.requests == []
    assert is_marked(conn, OCTOBER_KEY)


async def test_failed_document_send_propagates_and_is_retried(conn: sqlite3.Connection) -> None:
    add_october_entry(conn)
    bot = MockedBot()
    bot.add_result_for(SendDocument, ok=False, error_code=500, description="boom")

    with pytest.raises(TelegramServerError):
        await send_monthly_summary(bot, conn, OWNER_ID, TODAY)
    assert not is_marked(conn, OCTOBER_KEY)

    assert await send_monthly_summary(bot, conn, OWNER_ID, TODAY) is True
    assert is_marked(conn, OCTOBER_KEY)
    assert [type(r) for r in bot.requests] == [
        SendMessage,
        SendDocument,
        SendMessage,
        SendDocument,
    ]


async def test_summary_includes_the_budgets_block(conn: sqlite3.Connection) -> None:
    rent = add_category(conn, "Rent", "expense")
    entry = add_transaction(conn, parse_entry("800 rent", date(2026, 10, 5)))
    set_category(conn, entry.id, rent.id)
    set_budget(conn, rent, 85000, 2026, 10)
    bot = MockedBot()

    await send_monthly_summary(bot, conn, OWNER_ID, TODAY)

    [message, _] = bot.requests
    assert isinstance(message, SendMessage)
    assert "\n\nBudgets\nRent: 800.00 of 850.00 · 50.00 left\n\n" in message.text


async def test_long_summary_sends_every_piece_then_the_csv_and_marks_the_month_once(
    conn: sqlite3.Connection,
) -> None:
    fill_long_month(conn, date(2026, 10, 5))
    text = render_month(build_month_report(conn, 2026, 10))
    assert len(text) > 4000
    bot = MockedBot()

    sent = await send_monthly_summary(bot, conn, OWNER_ID, TODAY)

    assert sent is True
    *requests, document = bot.requests
    messages = [r for r in requests if isinstance(r, SendMessage)]
    assert len(messages) == len(requests) >= 2
    assert isinstance(document, SendDocument)
    assert all(m.parse_mode == "HTML" and m.chat_id == OWNER_ID for m in messages)
    assert all(len(m.text) < 4096 for m in messages)
    shown = [m.text.removeprefix("<pre>").removesuffix("</pre>") for m in messages]
    assert "\n\n".join(shown) == text
    marks = conn.execute("SELECT value FROM meta WHERE key LIKE 'summary_sent:%'").fetchall()
    assert [row["value"] for row in marks] == [TODAY.isoformat()]


async def test_failed_second_piece_propagates_sends_no_csv_and_is_retried(
    conn: sqlite3.Connection,
) -> None:
    fill_long_month(conn, date(2026, 10, 5))
    bot = MockedBot()
    bot.add_result_for(SendMessage, ok=True)
    bot.add_result_for(SendMessage, ok=False, error_code=500, description="boom")

    with pytest.raises(TelegramServerError):
        await send_monthly_summary(bot, conn, OWNER_ID, TODAY)
    assert not is_marked(conn, OCTOBER_KEY)
    assert [type(r) for r in bot.requests] == [SendMessage, SendMessage]

    assert await send_monthly_summary(bot, conn, OWNER_ID, TODAY) is True
    assert is_marked(conn, OCTOBER_KEY)
    assert isinstance(bot.requests[-1], SendDocument)
