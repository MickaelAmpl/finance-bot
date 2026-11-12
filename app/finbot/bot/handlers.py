import asyncio
import re
import sqlite3
from collections.abc import Awaitable, Callable
from datetime import date

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import Command, CommandObject
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardMarkup, Message

from finbot.ai_routing import route
from finbot.bot.ai_handlers import AiState, handle_ai_text
from finbot.bot.keyboards import (
    ClearCb,
    EntryCb,
    PickCb,
    back_keyboard,
    category_keyboard,
    clear_keyboard,
    entry_keyboard,
    last_keyboard,
    record_keyboard,
)
from finbot.budgets import (
    BudgetError,
    entry_budget,
    list_budgets,
    remove_budget,
    set_budget,
)
from finbot.categories import (
    Category,
    CategoryError,
    add_category,
    find_category,
    is_valid_name,
    list_categories,
    rename_category,
)
from finbot.export import export_csv
from finbot.ledger import (
    add_transaction,
    clear_month,
    clearable_summary,
    delete_entry,
    get_record,
    last_records,
    set_category,
    undo_last,
)
from finbot.money import parse_amount
from finbot.parser import Entry, ParseError, parse_entries
from finbot.rates import RateError, check_rate, parse_rate, set_rate
from finbot.reports import build_month_report, parse_month_arg, render_month
from finbot.savings import (
    SavingsError,
    apply_pot_entry,
    list_pots,
    months_left,
    recent_moves,
    set_goal,
)
from finbot.texts import (
    ALREADY_DELETED,
    CLEAR_TOO_OLD,
    NOTHING_DELETED,
    NOTHING_TO_UNDO,
    as_pre,
    budget_removed_text,
    budget_set_text,
    budgets_text,
    category_added_text,
    category_list_text,
    category_renamed_text,
    category_unknown_text,
    clear_ask_text,
    clear_changed_text,
    clear_done_text,
    clear_nothing_text,
    entry_line,
    help_text,
    last_text,
    pot_text,
    rate_set_text,
    removed_text,
    saved_text,
    savings_text,
    split_report,
)

RATE_USAGE = "Use: /rate usd 0.92"
GOAL_USAGE = "Use: /goal emergency 10000 or /goal emergency 10000 12.2027"
CATEGORY_USAGE = "Use: /category add Rent or /category rename Rent Housing"
CATEGORY_ADD_USAGE = "Use: /category add Rent or /category add income Bonus"
CATEGORY_RENAME_USAGE = "Use: /category rename Rent Housing"
BUDGET_USAGE = "Use: /budget Rent 850.00 (0 removes it)"
GOAL_MONTH_PASSED = "That month has passed. Use this month or later, e.g. 12.2027"
GOAL_MONTH = re.compile(r"(0[1-9]|1[0-2])\.([0-9]{4})")
ZERO_AMOUNT = re.compile(r"0+([.,]0{1,2})?")
RATE_CODES = ("USD", "UAH")


async def on_help(message: Message, ai: AiState | None) -> None:
    await message.answer(help_text(ai is not None))


async def on_entry_text(
    message: Message,
    bot: Bot,
    conn: sqlite3.Connection,
    today: Callable[[], date],
    ai: AiState | None,
) -> None:
    text = message.text or ""
    if ai is not None and not text.startswith("/") and route(text, today()) == "ai":
        await handle_ai_text(message, bot, conn, today, ai)
        return
    try:
        entries = parse_entries(text, today())
    except ParseError as error:
        await message.answer(str(error))
        return
    # Save everything first, so a reply that fails to send never leaves later entries unsaved.
    replies: list[tuple[str, InlineKeyboardMarkup | None]] = []
    for number, entry in enumerate(entries, start=1):
        try:
            replies.append(_save_entry(conn, entry))
        except SavingsError as error:
            refusal = str(error) if len(entries) == 1 else f"Entry {number} not saved: {error}"
            replies.append((refusal, None))
    for text, keyboard in replies:
        try:
            await message.answer(text, reply_markup=keyboard)
        except TelegramRetryAfter as error:
            await asyncio.sleep(error.retry_after)
            await message.answer(text, reply_markup=keyboard)


def _save_entry(conn: sqlite3.Connection, entry: Entry) -> tuple[str, InlineKeyboardMarkup | None]:
    if entry.kind in ("save", "take"):
        _, pot = apply_pot_entry(conn, entry)
        return pot_text(pot, entry.kind, entry.amount_cents, entry.on), None
    record = add_transaction(conn, entry)
    if record.category is None:
        keyboard = category_keyboard(record.id, list_categories(conn, record.kind))
    else:
        keyboard = entry_keyboard(record.id)
    return saved_text(record, entry_budget(conn, record)), keyboard


async def on_undo(message: Message, conn: sqlite3.Connection) -> None:
    try:
        record = undo_last(conn)
    except SavingsError as error:
        await message.answer(str(error))
        return
    await message.answer(NOTHING_TO_UNDO if record is None else removed_text(record))


async def on_last(message: Message, conn: sqlite3.Connection) -> None:
    text, keyboard = _last_view(conn)
    await message.answer(text, reply_markup=keyboard)


async def on_month(
    message: Message,
    conn: sqlite3.Connection,
    today: Callable[[], date],
    command: CommandObject,
) -> None:
    try:
        year, month = parse_month_arg(command.args, today())
    except ValueError as error:
        await message.answer(str(error))
        return
    report = build_month_report(conn, year, month)
    for piece in split_report(render_month(report)):
        await message.answer(as_pre(piece), parse_mode="HTML")


async def on_clear(
    message: Message,
    conn: sqlite3.Connection,
    today: Callable[[], date],
    command: CommandObject,
) -> None:
    try:
        year, month = parse_month_arg(command.args, today())
    except ValueError as error:
        await message.answer(str(error))
        return
    count, last_id = clearable_summary(conn, year, month)
    if count == 0:
        await message.answer(clear_nothing_text(year, month))
        return
    await message.answer(
        clear_ask_text(count, year, month),
        reply_markup=clear_keyboard(year, month, count, last_id),
    )


async def on_rate(
    message: Message,
    conn: sqlite3.Connection,
    today: Callable[[], date],
    command: CommandObject,
) -> None:
    parts = (command.args or "").split()
    if len(parts) != 2 or parts[0].upper() not in RATE_CODES:
        await message.answer(RATE_USAGE)
        return
    try:
        rate = parse_rate(parts[1])
    except ValueError:
        await message.answer(RATE_USAGE)
        return
    code = parts[0].upper()
    try:
        check_rate(code, rate)
    except RateError as error:
        await message.answer(str(error))
        return
    converted_ids = set_rate(conn, code, rate, today())
    records = (get_record(conn, entry_id) for entry_id in converted_ids)
    converted = [record for record in records if record is not None]
    await message.answer(rate_set_text(code, rate, converted))


async def on_savings(message: Message, conn: sqlite3.Connection, today: Callable[[], date]) -> None:
    pots = list_pots(conn)
    moves = {pot.id: recent_moves(conn, pot.id) for pot in pots}
    await message.answer(savings_text(pots, moves, today()))


async def on_goal(
    message: Message,
    conn: sqlite3.Connection,
    today: Callable[[], date],
    command: CommandObject,
) -> None:
    now = today()
    parts = (command.args or "").split()
    if len(parts) not in (2, 3) or not any(ch.isalpha() for ch in parts[0]) or len(parts[0]) > 30:
        await message.answer(GOAL_USAGE)
        return
    name, amount, *month_part = parts
    try:
        goal_cents = parse_amount(amount)
    except ValueError:
        await message.answer(GOAL_USAGE)
        return
    goal_month = None
    if month_part:
        match = GOAL_MONTH.fullmatch(month_part[0])
        if match is None:
            await message.answer(GOAL_USAGE)
            return
        month, year = match.groups()
        goal_month = f"{year}-{month}"
        if months_left(goal_month, now) < 1:
            await message.answer(GOAL_MONTH_PASSED)
            return
    try:
        pot = set_goal(conn, name, goal_cents, goal_month)
    except SavingsError as error:
        await message.answer(str(error))
        return
    await message.answer(savings_text([pot], {pot.id: recent_moves(conn, pot.id)}, now))


async def on_budget(
    message: Message,
    conn: sqlite3.Connection,
    today: Callable[[], date],
    command: CommandObject,
) -> None:
    now = today()
    words = (command.args or "").split()
    if not words:
        reply = budgets_text(list_budgets(conn, now.year, now.month), now)
    else:
        reply = _change_budget(conn, words, now)
    await message.answer(reply)


def _change_budget(conn: sqlite3.Connection, words: list[str], now: date) -> str:
    if len(words) < 2:
        return BUDGET_USAGE
    *name_words, amount = words
    try:
        cents = 0 if ZERO_AMOUNT.fullmatch(amount) else parse_amount(amount)
    except ValueError:
        return BUDGET_USAGE
    name = " ".join(name_words)
    found = find_category(conn, name)
    if found is None:
        return category_unknown_text(name)
    try:
        if cents == 0:
            remove_budget(conn, found)
            return budget_removed_text(found.name)
        return budget_set_text(set_budget(conn, found, cents, now.year, now.month), now)
    except BudgetError as error:
        return str(error)


async def on_category(message: Message, conn: sqlite3.Connection, command: CommandObject) -> None:
    words = (command.args or "").split()
    if not words:
        reply = category_list_text(
            list_categories(conn, "expense"), list_categories(conn, "income")
        )
    elif words[0].lower() == "add":
        reply = _add_category(conn, words[1:])
    elif words[0].lower() == "rename":
        reply = _rename_category(conn, words[1:])
    else:
        reply = CATEGORY_USAGE
    await message.answer(reply)


def _add_category(conn: sqlite3.Connection, words: list[str]) -> str:
    kind = "expense"
    if words and words[0].lower() == "income":
        kind, words = "income", words[1:]
    name = " ".join(words)
    if not is_valid_name(name):
        return CATEGORY_ADD_USAGE
    try:
        return category_added_text(add_category(conn, name, kind))
    except CategoryError as error:
        return str(error)


def _rename_category(conn: sqlite3.Connection, words: list[str]) -> str:
    if not words:
        return CATEGORY_RENAME_USAGE
    found = _leading_category(conn, words)
    if found is None:
        return category_unknown_text(words[0])
    old, rest = found
    new_name = " ".join(rest)
    if not is_valid_name(new_name):
        return CATEGORY_RENAME_USAGE
    try:
        renamed = rename_category(conn, old.id, new_name)
    except CategoryError as error:
        return str(error)
    return category_renamed_text(old.name, renamed.name)


def _leading_category(
    conn: sqlite3.Connection, words: list[str]
) -> tuple[Category, list[str]] | None:
    # Category names can have several words, so the longest leading run that matches one wins.
    for length in range(len(words), 0, -1):
        category = find_category(conn, " ".join(words[:length]))
        if category is not None:
            return category, words[length:]
    return None


async def on_export(message: Message, conn: sqlite3.Connection, today: Callable[[], date]) -> None:
    filename = f"finbot-export-{today().isoformat()}.csv"
    await message.answer_document(BufferedInputFile(export_csv(conn), filename=filename))


def _last_view(conn: sqlite3.Connection) -> tuple[str, InlineKeyboardMarkup | None]:
    records = last_records(conn)
    return last_text(records), last_keyboard(records) if records else None


async def _ignore_unchanged(edit: Awaitable[object]) -> None:
    # Re-picking the value already shown leaves the message unchanged, and Telegram refuses that.
    try:
        await edit
    except TelegramBadRequest as error:
        if "message is not modified" not in error.message:
            raise


async def on_pick_category(
    callback: CallbackQuery, callback_data: PickCb, conn: sqlite3.Connection
) -> None:
    text: str | None = None
    try:
        if get_record(conn, callback_data.entry_id) is None:
            text = ALREADY_DELETED
            return
        record = set_category(conn, callback_data.entry_id, callback_data.category_id)
        if isinstance(callback.message, Message):
            await _ignore_unchanged(
                callback.message.edit_text(
                    saved_text(record, entry_budget(conn, record)),
                    reply_markup=entry_keyboard(record.id),
                )
            )
    finally:
        await callback.answer(text)


async def on_change_category(
    callback: CallbackQuery, callback_data: EntryCb, conn: sqlite3.Connection
) -> None:
    text: str | None = None
    try:
        record = get_record(conn, callback_data.entry_id)
        if record is None:
            text = ALREADY_DELETED
            return
        if record.kind not in ("expense", "income"):
            return
        if isinstance(callback.message, Message):
            keyboard = category_keyboard(record.id, list_categories(conn, record.kind))
            await _ignore_unchanged(callback.message.edit_reply_markup(reply_markup=keyboard))
    finally:
        await callback.answer(text)


async def on_delete_entry(
    callback: CallbackQuery, callback_data: EntryCb, conn: sqlite3.Connection
) -> None:
    text: str | None = None
    try:
        record = delete_entry(conn, callback_data.entry_id)
        if record is None:
            text = ALREADY_DELETED if callback_data.action == "del" else NOTHING_TO_UNDO
        elif isinstance(callback.message, Message):
            keyboard = back_keyboard() if callback_data.action == "del" else None
            await _ignore_unchanged(
                callback.message.edit_text(removed_text(record), reply_markup=keyboard)
            )
    except SavingsError as error:
        text = str(error)
    finally:
        await callback.answer(text)


async def on_open_entry(
    callback: CallbackQuery, callback_data: EntryCb, conn: sqlite3.Connection
) -> None:
    text: str | None = None
    try:
        record = get_record(conn, callback_data.entry_id)
        if record is None:
            text = ALREADY_DELETED
        elif isinstance(callback.message, Message):
            await _ignore_unchanged(
                callback.message.edit_text(entry_line(record), reply_markup=record_keyboard(record))
            )
    finally:
        await callback.answer(text)


async def on_back_to_list(callback: CallbackQuery, conn: sqlite3.Connection) -> None:
    try:
        if isinstance(callback.message, Message):
            text, keyboard = _last_view(conn)
            await _ignore_unchanged(callback.message.edit_text(text, reply_markup=keyboard))
    finally:
        await callback.answer()


async def on_clear_confirm(
    callback: CallbackQuery, callback_data: ClearCb, conn: sqlite3.Connection
) -> None:
    text: str | None = None
    try:
        if not isinstance(callback.message, Message):
            text = CLEAR_TOO_OLD
            return
        year, month = callback_data.year, callback_data.month
        try:
            deleted = clear_month(conn, year, month, callback_data.count, callback_data.last_id)
        except ValueError:
            return  # forged data: not a real month
        reply = (
            clear_changed_text(year, month)
            if deleted is None
            else clear_done_text(deleted, year, month)
        )
        await _ignore_unchanged(callback.message.edit_text(reply, reply_markup=None))
    finally:
        await callback.answer(text)


async def on_clear_cancel(callback: CallbackQuery) -> None:
    try:
        if isinstance(callback.message, Message):
            await _ignore_unchanged(callback.message.edit_text(NOTHING_DELETED, reply_markup=None))
    finally:
        await callback.answer()


async def on_unknown_callback(callback: CallbackQuery) -> None:
    await callback.answer()


def create_router() -> Router:
    router = Router()
    router.message.register(on_help, Command("start", "help"))
    router.message.register(on_undo, Command("undo"))
    router.message.register(on_last, Command("last"))
    router.message.register(on_month, Command("month"))
    router.message.register(on_rate, Command("rate"))
    router.message.register(on_savings, Command("savings"))
    router.message.register(on_goal, Command("goal"))
    router.message.register(on_export, Command("export"))
    router.message.register(on_budget, Command("budget"))
    router.message.register(on_category, Command("category"))
    router.message.register(on_clear, Command("clear"))
    router.message.register(on_entry_text, F.text)
    router.callback_query.register(on_pick_category, PickCb.filter())
    router.callback_query.register(on_change_category, EntryCb.filter(F.action == "cat"))
    router.callback_query.register(on_delete_entry, EntryCb.filter(F.action.in_(("undo", "del"))))
    router.callback_query.register(on_open_entry, EntryCb.filter(F.action == "open"))
    router.callback_query.register(on_back_to_list, EntryCb.filter(F.action == "back"))
    router.callback_query.register(on_clear_confirm, ClearCb.filter(F.action == "yes"))
    router.callback_query.register(on_clear_cancel, ClearCb.filter(F.action == "no"))
    router.callback_query.register(on_unknown_callback)
    return router
