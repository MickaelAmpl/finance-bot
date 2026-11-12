from aiogram.types import InlineKeyboardMarkup

from finbot.bot.keyboards import DraftCb, draft_keyboard


def _labels(markup: InlineKeyboardMarkup) -> list[list[str]]:
    return [[button.text for button in row] for row in markup.inline_keyboard]


def _data(markup: InlineKeyboardMarkup) -> list[list[str]]:
    return [[button.callback_data or "" for button in row] for row in markup.inline_keyboard]


def test_draft_cb_fits_telegram_limit_and_unpacks_back():
    packed = DraftCb(action="s", draft_id=999999).pack()

    assert len(packed.encode()) <= 64
    assert DraftCb.unpack(packed) == DraftCb(action="s", draft_id=999999)


def test_draft_keyboard_has_one_row_with_save_and_cancel():
    markup = draft_keyboard(5, 3)

    assert _labels(markup) == [["Save 3 entries", "Cancel"]]
    assert _data(markup) == [["d:s:5", "d:c:5"]]


def test_draft_keyboard_for_one_entry_says_save():
    assert _labels(draft_keyboard(7, 1)) == [["Save", "Cancel"]]
