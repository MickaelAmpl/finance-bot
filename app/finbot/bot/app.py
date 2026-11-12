import logging
import sqlite3
from collections.abc import Callable
from datetime import date

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BotCommand

from finbot.bot.access import OwnerOnly
from finbot.bot.ai_handlers import AiState, create_ai_router
from finbot.bot.handlers import create_router
from finbot.texts import BOT_COMMANDS


async def _set_commands(bot: Bot) -> None:
    commands = [BotCommand(command=name, description=text) for name, text in BOT_COMMANDS]
    try:
        await bot.set_my_commands(commands, request_timeout=10)
    except TelegramAPIError:
        logging.exception("could not set the Telegram menu commands")


def build_dispatcher(
    conn: sqlite3.Connection,
    owner_id: int,
    today: Callable[[], date],
    ai: AiState | None = None,
) -> Dispatcher:
    dispatcher = Dispatcher(conn=conn, today=today, ai=ai)
    owner_only = OwnerOnly(owner_id)
    dispatcher.message.outer_middleware(owner_only)
    dispatcher.callback_query.outer_middleware(owner_only)
    dispatcher.include_router(create_ai_router())
    dispatcher.include_router(create_router())
    dispatcher.startup.register(_set_commands)
    return dispatcher
