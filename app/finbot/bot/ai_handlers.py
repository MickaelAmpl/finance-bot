import asyncio
import base64
import contextlib
import logging
import sqlite3
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Literal

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.types import CallbackQuery, Message
from aiogram.utils.chat_action import ChatActionSender
from anthropic import AsyncAnthropic
from anthropic.types import ContentBlockParam, UserMessageParam

from finbot.ai_memory import Memory
from finbot.ai_prompt import build_system_prompt
from finbot.assistant import UNAVAILABLE_MSG, Answer, Failure, Proposal, run_turn
from finbot.bot.keyboards import DraftCb, category_keyboard, draft_keyboard, entry_keyboard
from finbot.budgets import entry_budget
from finbot.categories import list_categories
from finbot.config import TZ
from finbot.drafts import (
    DraftClosed,
    cancel_draft,
    count_live_drafts,
    create_draft,
    save_draft,
    set_draft_message,
)
from finbot.ledger import Record
from finbot.texts import (
    AI_TOO_LONG,
    DRAFT_CANCEL_FAILED,
    DRAFT_CANCELLED,
    DRAFT_EARLIER_CLOSED,
    DRAFT_OTHER_OPEN,
    DRAFT_REPLACED,
    DRAFT_SAVE_FAILED,
    PHOTO_NEEDS_AI,
    PHOTO_UNREADABLE,
    draft_closed_text,
    draft_saved_text,
    draft_text,
    saved_text,
)

AI_TEXT_MAX = 1000
IMAGE_MAX_BYTES = 5 * 1024 * 1024
RECEIPT_MARK = "[receipt photo]"
IMAGE_TYPES = ("image/jpeg", "image/png", "image/webp")
_log = logging.getLogger("finbot.ai")


@dataclass
class AiState:
    client: AsyncAnthropic
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    memory: Memory = field(default_factory=Memory)


@dataclass(frozen=True)
class _Turn:
    content: list[ContentBlockParam]
    memory_text: str
    source: str


async def handle_ai_text(
    message: Message,
    bot: Bot,
    conn: sqlite3.Connection,
    today: Callable[[], date],
    ai: AiState,
) -> None:
    text = message.text or ""
    if len(text) > AI_TEXT_MAX:
        await message.answer(AI_TOO_LONG)
        return

    async def prepare() -> _Turn:
        return _Turn([{"type": "text", "text": text}], text, "text")

    await _ai_turn(message, bot, conn, today, ai, prepare)


async def handle_ai_photo(
    message: Message,
    bot: Bot,
    conn: sqlite3.Connection,
    today: Callable[[], date],
    ai: AiState | None,
) -> None:
    if ai is None:
        await message.answer(PHOTO_NEEDS_AI)
        return
    await _ai_turn(message, bot, conn, today, ai, lambda: _photo_turn(message, bot))


def is_receipt(message: Message) -> bool:
    if message.photo:
        return True
    document = message.document
    return (
        document is not None
        and document.mime_type in IMAGE_TYPES
        and (document.file_size or 0) <= IMAGE_MAX_BYTES
    )


async def _photo_turn(message: Message, bot: Bot) -> _Turn | None:
    file_id = _file_id(message)
    if file_id is None:
        await message.answer(PHOTO_UNREADABLE)
        return None
    try:
        buffer = await bot.download(file_id)
        data = b"" if buffer is None else buffer.read()
    except Exception as error:
        _log.error("photo download failed: %s", type(error).__name__)
        await message.answer(PHOTO_UNREADABLE)
        return None
    media_type = _media_type(data)
    if media_type is None:
        await message.answer(PHOTO_UNREADABLE)
        return None
    label = RECEIPT_MARK if not message.caption else f"{RECEIPT_MARK} {message.caption}"
    content: list[ContentBlockParam] = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": base64.b64encode(data).decode("ascii"),
            },
        },
        {"type": "text", "text": label},
    ]
    return _Turn(content, label, "photo")


async def _ai_turn(
    message: Message,
    bot: Bot,
    conn: sqlite3.Connection,
    today: Callable[[], date],
    ai: AiState,
    prepare: Callable[[], Awaitable[_Turn | None]],
) -> None:
    try:
        async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id), ai.lock:
            turn = await prepare()
            if turn is None:
                return
            await _run_turn(message, bot, conn, today, ai, turn)
    except Exception as error:
        _log.error("ai turn failed: %s", type(error).__name__)
        try:
            await message.answer(UNAVAILABLE_MSG)
        except TelegramAPIError as send_error:
            _log.error("ai failure reply failed: %s", type(send_error).__name__)


async def _run_turn(
    message: Message,
    bot: Bot,
    conn: sqlite3.Connection,
    today: Callable[[], date],
    ai: AiState,
    turn: _Turn,
) -> None:
    now = datetime.now(UTC)
    message_date = message.date.astimezone(TZ).date()
    system = build_system_prompt(conn, message_date)
    user: UserMessageParam = {"role": "user", "content": turn.content}
    outcome = await run_turn(
        ai.client,
        conn,
        system=system,
        history=ai.memory.history(now),
        user=user,
        source=turn.source,
        message_date=message_date,
        today=today(),
    )
    match outcome:
        case Proposal(entries=entries, replaces_open_draft=replaces):
            created, replaced = create_draft(conn, entries, turn.source, replaces, now)
            if replaced is not None:
                if replaced.message_id is not None:
                    with contextlib.suppress(TelegramAPIError):
                        await bot.edit_message_text(
                            text=DRAFT_REPLACED,
                            chat_id=message.chat.id,
                            message_id=replaced.message_id,
                            reply_markup=None,
                        )
                ai.memory.mark_draft(replaced.id, "[draft replaced]")
            text = draft_text(created.entries)
            if replaces and replaced is None and turn.source == "text":
                others = count_live_drafts(conn, now) > 1
                text += "\n" + (DRAFT_OTHER_OPEN if others else DRAFT_EARLIER_CLOSED)
            keyboard = draft_keyboard(created.id, len(created.entries))
            try:
                sent = await _retry_once(lambda: message.answer(text, reply_markup=keyboard))
            except TelegramAPIError:
                cancel_draft(conn, created.id, now)
                raise
            set_draft_message(conn, created.id, sent.message_id)
            ai.memory.add(turn.memory_text, text, now, created.id)
        case Answer(text=text):
            await message.answer(text)
            ai.memory.add(turn.memory_text, text, now)
        case Failure(reply=reply):
            await message.answer(reply)


async def on_draft_save(
    callback: CallbackQuery,
    callback_data: DraftCb,
    bot: Bot,
    conn: sqlite3.Connection,
    ai: AiState | None,
) -> None:
    try:
        records = save_draft(conn, callback_data.draft_id, datetime.now(UTC))
    except DraftClosed as closed:
        await callback.answer(draft_closed_text(closed.status))
        return
    except sqlite3.Error:
        await callback.answer(DRAFT_SAVE_FAILED)
        return
    except Exception as error:
        _log.error("draft save failed: %s", type(error).__name__)
        await callback.answer(DRAFT_SAVE_FAILED)
        return
    if ai is not None:
        ai.memory.mark_draft(callback_data.draft_id, "[draft saved]")
    try:
        await callback.answer()
    except TelegramAPIError as error:
        _log.error("callback answer failed: %s", type(error).__name__)
    chat_id = _chat_id(callback)
    for record in records:
        await _send_saved(bot, chat_id, conn, record)
    await _edit_draft(callback, draft_saved_text(len(records)))


async def on_draft_cancel(
    callback: CallbackQuery, callback_data: DraftCb, conn: sqlite3.Connection, ai: AiState | None
) -> None:
    try:
        cancel_draft(conn, callback_data.draft_id, datetime.now(UTC))
    except DraftClosed as closed:
        await callback.answer(draft_closed_text(closed.status))
        return
    except sqlite3.Error as error:
        _log.error("cancel failed: %s", type(error).__name__)
        await callback.answer(DRAFT_CANCEL_FAILED)
        return
    if ai is not None:
        ai.memory.mark_draft(callback_data.draft_id, "[draft cancelled]")
    try:
        await _edit_draft(callback, DRAFT_CANCELLED)
    finally:
        await callback.answer()


async def _send_saved(bot: Bot, chat_id: int, conn: sqlite3.Connection, record: Record) -> None:
    try:
        budget = entry_budget(conn, record)
    except sqlite3.Error as error:
        _log.error("budget read failed: %s", type(error).__name__)
        budget = None
    text = saved_text(record, budget)
    if record.category is None:
        try:
            keyboard = category_keyboard(record.id, list_categories(conn, record.kind))
        except sqlite3.Error as error:
            _log.error("category list failed: %s", type(error).__name__)
            keyboard = entry_keyboard(record.id)
    else:
        keyboard = entry_keyboard(record.id)
    try:
        await _retry_once(
            lambda: bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
        )
    except TelegramAPIError as error:
        _log.error("saved reply failed: %s", type(error).__name__)


async def _edit_draft(callback: CallbackQuery, text: str) -> None:
    if not isinstance(callback.message, Message):
        return
    try:
        await callback.message.edit_text(text, reply_markup=None)
    except TelegramAPIError as error:
        if "message is not modified" not in error.message:
            _log.error("draft edit failed: %s", type(error).__name__)


async def _retry_once[T](send: Callable[[], Awaitable[T]]) -> T:
    try:
        return await send()
    except TelegramRetryAfter as error:
        await asyncio.sleep(error.retry_after)
        return await send()


def _chat_id(callback: CallbackQuery) -> int:
    return callback.from_user.id if callback.message is None else callback.message.chat.id


def _file_id(message: Message) -> str | None:
    if message.photo:
        return message.photo[-1].file_id
    return None if message.document is None else message.document.file_id


def _media_type(data: bytes) -> Literal["image/jpeg", "image/png", "image/webp"] | None:
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG"):
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def create_ai_router() -> Router:
    router = Router()
    router.message.register(handle_ai_photo, is_receipt)
    router.callback_query.register(on_draft_save, DraftCb.filter(F.action == "s"))
    router.callback_query.register(on_draft_cancel, DraftCb.filter(F.action == "c"))
    return router
