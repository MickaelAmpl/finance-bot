import argparse
import asyncio
import logging
import os
import re
import sqlite3
import sys
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path

from aiogram import Bot
from aiogram.types import BufferedInputFile

from finbot.bot.session import build_bot, redact_token_in_logs
from finbot.config import TZ, load_settings, read_env_file
from finbot.db import connect
from finbot.export import export_csv
from finbot.reports import build_month_report, render_month
from finbot.texts import as_pre, split_report

_BACKUP_NAME = re.compile(r"finbot-\d{4}-\d{2}-\d{2}\.db")
ENV_FILE = Path(".env")


def backup_db(conn: sqlite3.Connection, backup_dir: Path, today: date, keep: int = 14) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    path = backup_dir / f"finbot-{today.isoformat()}.db"
    with closing(sqlite3.connect(path)) as dest:
        conn.backup(dest)
    backups = sorted(p for p in backup_dir.iterdir() if _BACKUP_NAME.fullmatch(p.name))
    for old in backups[: max(len(backups) - keep, 0)]:
        old.unlink()
    return path


def previous_month(today: date) -> tuple[int, int]:
    last_day = today.replace(day=1) - timedelta(days=1)
    return last_day.year, last_day.month


async def send_monthly_summary(
    bot: Bot, conn: sqlite3.Connection, owner_id: int, today: date
) -> bool:
    year, month = previous_month(today)
    key = f"summary_sent:{year}-{month:02d}"
    if conn.execute("SELECT 1 FROM meta WHERE key = ?", (key,)).fetchone() is not None:
        return False
    report = build_month_report(conn, year, month)
    has_entries = report.entries > 0
    if has_entries:
        # A send error raises before the key is written, so the next daily run retries.
        for piece in split_report(render_month(report)):
            await bot.send_message(owner_id, as_pre(piece), parse_mode="HTML")
        document = BufferedInputFile(
            export_csv(conn), filename=f"finbot-export-{today.isoformat()}.csv"
        )
        await bot.send_document(owner_id, document)
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (key, today.isoformat())
        )
    return has_entries


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m finbot.jobs")
    parser.add_argument("command", choices=["daily"])
    parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    try:
        settings = load_settings(
            {**read_env_file(ENV_FILE), **os.environ} if ENV_FILE.exists() else dict(os.environ)
        )
        redact_token_in_logs(settings.bot_token)
        conn = connect(settings.db_path)
        today = datetime.now(TZ).date()
        backup_db(conn, settings.backup_dir, today)

        async def send() -> None:
            async with build_bot(settings.bot_token) as bot:
                await send_monthly_summary(bot, conn, settings.owner_id, today)

        asyncio.run(send())
    except Exception:
        logging.exception("daily job failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
