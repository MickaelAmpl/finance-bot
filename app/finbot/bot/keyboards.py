from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from finbot.categories import Category
from finbot.ledger import Record
from finbot.texts import clear_button_text, last_button_text, save_button_text

CATEGORY_COLUMNS = 3


class DraftCb(CallbackData, prefix="d"):
    action: str
    draft_id: int


class EntryCb(CallbackData, prefix="e"):
    action: str
    entry_id: int


class PickCb(CallbackData, prefix="p"):
    entry_id: int
    category_id: int


class ClearCb(CallbackData, prefix="c"):
    action: str
    year: int
    month: int
    count: int
    last_id: int


def entry_keyboard(entry_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Change category",
                    callback_data=EntryCb(action="cat", entry_id=entry_id).pack(),
                ),
                InlineKeyboardButton(
                    text="Undo",
                    callback_data=EntryCb(action="undo", entry_id=entry_id).pack(),
                ),
            ]
        ]
    )


def category_keyboard(entry_id: int, categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category.name,
            callback_data=PickCb(entry_id=entry_id, category_id=category.id).pack(),
        )
    builder.adjust(CATEGORY_COLUMNS)
    return builder.as_markup()


def last_keyboard(records: list[Record]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for number, record in enumerate(records, start=1):
        builder.button(
            text=last_button_text(number, record),
            callback_data=EntryCb(action="open", entry_id=record.id).pack(),
        )
    builder.adjust(1)
    return builder.as_markup()


def record_keyboard(record: Record) -> InlineKeyboardMarkup:
    row: list[InlineKeyboardButton] = []
    if record.kind in ("expense", "income"):
        row.append(
            InlineKeyboardButton(
                text="Change category",
                callback_data=EntryCb(action="cat", entry_id=record.id).pack(),
            )
        )
    row.append(
        InlineKeyboardButton(
            text="Delete",
            callback_data=EntryCb(action="del", entry_id=record.id).pack(),
        )
    )
    return InlineKeyboardMarkup(inline_keyboard=[row, [_back_button()]])


def clear_keyboard(year: int, month: int, count: int, last_id: int) -> InlineKeyboardMarkup:
    shown = {"year": year, "month": month, "count": count, "last_id": last_id}
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=clear_button_text(count),
                    callback_data=ClearCb(action="yes", **shown).pack(),
                ),
                InlineKeyboardButton(
                    text="Cancel",
                    callback_data=ClearCb(action="no", **shown).pack(),
                ),
            ]
        ]
    )


def draft_keyboard(draft_id: int, count: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=save_button_text(count),
                    callback_data=DraftCb(action="s", draft_id=draft_id).pack(),
                ),
                InlineKeyboardButton(
                    text="Cancel",
                    callback_data=DraftCb(action="c", draft_id=draft_id).pack(),
                ),
            ]
        ]
    )


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[_back_button()]])


def _back_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="Back to list",
        callback_data=EntryCb(action="back", entry_id=0).pack(),
    )
