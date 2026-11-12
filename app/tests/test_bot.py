import asyncio
import csv
import io
import logging
import sqlite3
from contextlib import closing
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pytest
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.methods import (
    AnswerCallbackQuery,
    EditMessageReplyMarkup,
    EditMessageText,
    SendDocument,
    SendMessage,
    SetMyCommands,
    TelegramMethod,
)
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    Chat,
    InaccessibleMessage,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
    User,
)

from finbot.bot.app import build_dispatcher
from finbot.bot.keyboards import (
    ClearCb,
    EntryCb,
    PickCb,
    back_keyboard,
    category_keyboard,
    entry_keyboard,
    last_keyboard,
    record_keyboard,
)
from finbot.budgets import list_budgets
from finbot.categories import Category, add_category, category_for_keyword, list_categories
from finbot.db import connect
from finbot.ledger import Record, all_records, get_record
from finbot.reports import build_month_report, render_month
from finbot.savings import list_pots, set_goal
from finbot.texts import BOT_COMMANDS, CLEAR_TOO_OLD, HELP
from tests.mocked_bot import MockedBot
from tests.test_db import _make_version_1_database, _make_version_2_database
from tests.test_jobs import fill_long_month

OWNER_ID = 42
TODAY = date(2026, 11, 1)
NOW = datetime(2026, 11, 1, 10, 0)
RATE_USAGE = "Use: /rate usd 0.92"
GOAL_USAGE = "Use: /goal emergency 10000 or /goal emergency 10000 12.2027"
GOAL_MONTH_PASSED = "That month has passed. Use this month or later, e.g. 12.2027"
NOT_MODIFIED = "Bad Request: message is not modified"
BELOW_ZERO = "Emergency would go below zero. Delete the later take first."
USD_RATE_RANGE = (
    "That rate looks wrong: 1 USD should be between 0.5 and 2 EUR. Example: /rate usd 0.92"
)
UAH_RATE_RANGE = (
    "That rate looks wrong: 1 UAH should be between 0.005 and 0.1 EUR. Example: /rate uah 0.022"
)
CATEGORY_USAGE = "Use: /category add Rent or /category rename Rent Housing"
CATEGORY_ADD_USAGE = "Use: /category add Rent or /category add income Bonus"
CATEGORY_RENAME_USAGE = "Use: /category rename Rent Housing"
BUDGET_USAGE = "Use: /budget Rent 850.00 (0 removes it)"
SEED_EXPENSE = (
    "Groceries, Eating out, Transport, Housing, Utilities, Health, Shopping, Entertainment,"
    " Travel, Subscriptions, Gifts, Other"
)


def _chat(user_id: int, group: bool) -> Chat:
    if group:
        return Chat(id=-1001, type="supergroup")
    return Chat(id=user_id, type="private")


def text_update(text: str, *, user_id: int = OWNER_ID, group: bool = False) -> Update:
    return Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=NOW,
            chat=_chat(user_id, group),
            from_user=User(id=user_id, is_bot=False, first_name="Misha"),
            text=text,
        ),
    )


def callback_update(data: str, *, user_id: int = OWNER_ID, group: bool = False) -> Update:
    return Update(
        update_id=2,
        callback_query=CallbackQuery(
            id="callback-1",
            from_user=User(id=user_id, is_bot=False, first_name="Misha"),
            chat_instance="1",
            data=data,
            message=Message(
                message_id=7,
                date=NOW,
                chat=_chat(user_id, group),
                text="message",
            ),
        ),
    )


class Harness:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.bot = MockedBot()
        self.dispatcher = build_dispatcher(conn, OWNER_ID, lambda: TODAY)

    async def send(
        self, text: str, *, user_id: int = OWNER_ID, group: bool = False
    ) -> list[TelegramMethod[Any]]:
        self.bot.requests.clear()
        await self.dispatcher.feed_update(self.bot, text_update(text, user_id=user_id, group=group))
        return list(self.bot.requests)

    async def press(
        self, data: str, *, user_id: int = OWNER_ID, group: bool = False
    ) -> list[TelegramMethod[Any]]:
        self.bot.requests.clear()
        await self.dispatcher.feed_update(
            self.bot, callback_update(data, user_id=user_id, group=group)
        )
        return list(self.bot.requests)


@pytest.fixture
def harness(conn: sqlite3.Connection) -> Harness:
    return Harness(conn)


def of[T](requests: list[TelegramMethod[Any]], method: type[T]) -> list[T]:
    return [request for request in requests if isinstance(request, method)]


def buttons(markup: object) -> list[InlineKeyboardButton]:
    assert isinstance(markup, InlineKeyboardMarkup)
    return [button for row in markup.inline_keyboard for button in row]


def labels(markup: object) -> list[list[str]]:
    assert isinstance(markup, InlineKeyboardMarkup)
    return [[button.text for button in row] for row in markup.inline_keyboard]


def callback_data(markup: object, label: str) -> str:
    [button] = [b for b in buttons(markup) if b.text == label]
    assert button.callback_data is not None
    return button.callback_data


async def open_entry(harness: Harness, label: str) -> EditMessageText:
    [listing] = of(await harness.send("/last"), SendMessage)
    [view] = of(await harness.press(callback_data(listing.reply_markup, label)), EditMessageText)
    return view


def category(conn: sqlite3.Connection, name: str) -> Category:
    return next(c for c in list_categories(conn, "expense") if c.name == name)


def newest_id(conn: sqlite3.Connection) -> int:
    return all_records(conn)[-1].id


def is_soft_deleted(conn: sqlite3.Connection, entry_id: int) -> bool:
    row = conn.execute("SELECT deleted_at FROM entries WHERE id = ?", (entry_id,)).fetchone()
    return row["deleted_at"] is not None


def rate_rows(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    rows = conn.execute("SELECT currency, eur_per_unit, set_on FROM rates ORDER BY id")
    return [tuple(row) for row in rows.fetchall()]


async def test_owner_entry_is_saved_and_asks_for_category(harness: Harness) -> None:
    requests = await harness.send("25 coffee")

    assert len(requests) == 1
    [request] = of(requests, SendMessage)
    assert request.text.startswith("Saved 01.11: -25.00 EUR · coffee")
    assert request.text.endswith('New word "coffee" - pick a category:')
    assert len(buttons(request.reply_markup)) == 12
    assert len(all_records(harness.conn)) == 1


async def test_other_user_gets_no_reply_and_nothing_is_stored(harness: Harness) -> None:
    assert await harness.send("25 coffee", user_id=7) == []
    assert all_records(harness.conn) == []


async def test_owner_in_group_chat_gets_no_reply_and_nothing_is_stored(harness: Harness) -> None:
    assert await harness.send("25 coffee", group=True) == []
    assert all_records(harness.conn) == []


async def test_picking_a_category_edits_the_message_and_remembers_the_word(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    eating_out = category(harness.conn, "Eating out")

    requests = await harness.press(
        PickCb(entry_id=newest_id(harness.conn), category_id=eating_out.id).pack()
    )

    [edit] = of(requests, EditMessageText)
    assert edit.text == "Saved 01.11: -25.00 EUR · coffee → Eating out"
    assert len(of(requests, AnswerCallbackQuery)) == 1
    assert category_for_keyword(harness.conn, "coffee", "expense") == eating_out


async def test_known_keyword_is_filed_under_its_category(harness: Harness) -> None:
    await harness.send("25 coffee")
    eating_out = category(harness.conn, "Eating out")
    await harness.press(PickCb(entry_id=newest_id(harness.conn), category_id=eating_out.id).pack())

    [request] = of(await harness.send("25 coffee"), SendMessage)

    assert request.text == "Saved 01.11: -25.00 EUR · coffee → Eating out"
    assert labels(request.reply_markup) == [["Change category", "Undo"]]


async def test_income_with_unknown_keyword_offers_income_categories(harness: Harness) -> None:
    [request] = of(await harness.send("+100 bonus"), SendMessage)

    assert [b.text for b in buttons(request.reply_markup)] == [
        "Salary",
        "Freelance",
        "Other income",
    ]


async def test_uah_entry_waits_for_rate_then_rate_converts_it(harness: Harness) -> None:
    [first] = of(await harness.send("1200 uah taxi"), SendMessage)
    assert "No UAH rate yet" in first.text

    [rate] = of(await harness.send("/rate uah 0.022"), SendMessage)

    assert rate.text == (
        "Saved: 1 UAH = 0.022 EUR.\n"
        "Converted 1 entry that was waiting for this rate:\n"
        "01.11 -1,200.00 UAH taxi = -26.40 EUR"
    )


async def test_undo_twice_removes_then_reports_nothing(harness: Harness) -> None:
    await harness.send("25 coffee")
    [first] = of(await harness.send("/undo"), SendMessage)
    [second] = of(await harness.send("/undo"), SendMessage)

    assert [first.text, second.text] == ["Removed 01.11: -25.00 EUR · coffee", "Nothing to undo."]
    assert all_records(harness.conn) == []


async def test_number_with_spaces_is_rejected_and_not_saved(harness: Harness) -> None:
    [request] = of(await harness.send("1 200 taxi"), SendMessage)

    assert request.text == "Write 1200 without spaces, e.g. 1200 taxi"
    assert all_records(harness.conn) == []


async def test_take_above_balance_is_refused_and_pot_unchanged(harness: Harness) -> None:
    await harness.send("save 200 emergency")
    [refusal] = of(await harness.send("take 999 emergency"), SendMessage)

    assert refusal.text == "Emergency has 200.00 EUR, cannot take 999.00"
    [pot] = list_pots(harness.conn)
    assert pot.total_cents == 20000


async def test_pot_move_reply_has_no_keyboard(harness: Harness) -> None:
    [request] = of(await harness.send("save 200 emergency"), SendMessage)

    assert request.text == "Emergency pot 01.11: +200.00 EUR · total 200.00 EUR"
    assert request.reply_markup is None


async def test_pot_move_reply_shows_the_entrys_own_date(harness: Harness) -> None:
    await harness.send("save 150 emergency")

    [request] = of(await harness.send("save 200 emergency 28.10"), SendMessage)

    assert request.text == "Emergency pot 28.10: +200.00 EUR · total 350.00 EUR"


@pytest.mark.parametrize("command", ["/start", "/help"])
async def test_start_and_help_show_help(harness: Harness, command: str) -> None:
    [request] = of(await harness.send(command), SendMessage)

    assert request.text == HELP


async def test_startup_sets_the_menu_commands(harness: Harness) -> None:
    await harness.dispatcher.emit_startup(bot=harness.bot)

    [request] = of(harness.bot.requests, SetMyCommands)
    assert [(c.command, c.description) for c in request.commands] == [
        ("month", "Report for this month"),
        ("last", "Last 10 entries: change or delete"),
        ("undo", "Delete the last entry"),
        ("savings", "Savings pots and goals"),
        ("goal", "Set a goal: /goal emergency 10000 12.2027"),
        ("budget", "Monthly limits: /budget Rent 850.00"),
        ("category", "Add or rename: /category add Rent"),
        ("clear", "Delete a month's entries (asks first)"),
        ("rate", "Set a rate: /rate usd 0.92"),
        ("export", "All entries as a CSV file"),
        ("help", "How to write entries"),
    ]
    assert request.scope is None


async def test_menu_update_has_a_10_second_request_timeout(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = harness.bot.mocked_session
    real_make_request = session.make_request
    timeouts: list[int | None] = []

    async def spy(bot: MockedBot, method: TelegramMethod[Any], timeout: int | None = None) -> Any:
        if isinstance(method, SetMyCommands):
            timeouts.append(timeout)
        return await real_make_request(bot, method, timeout=timeout)

    monkeypatch.setattr(session, "make_request", spy)

    await harness.dispatcher.emit_startup(bot=harness.bot)

    assert timeouts == [10]


async def test_startup_accepts_the_keyword_arguments_start_polling_passes(
    harness: Harness,
) -> None:
    # The same dictionary start_polling builds before it calls emit_startup.
    workflow_data = {
        "dispatcher": harness.dispatcher,
        "bots": [harness.bot],
        **harness.dispatcher.workflow_data,
    }
    assert {"conn", "today"} <= workflow_data.keys()

    await harness.dispatcher.emit_startup(bot=harness.bot, **workflow_data)

    [request] = of(harness.bot.requests, SetMyCommands)
    assert len(request.commands) == len(BOT_COMMANDS)


async def test_failed_menu_update_is_logged_and_startup_continues(
    harness: Harness, caplog: pytest.LogCaptureFixture
) -> None:
    harness.bot.add_result_for(
        SetMyCommands, ok=False, error_code=400, description="Bad Request: test"
    )

    await harness.dispatcher.emit_startup(bot=harness.bot)

    assert len(of(harness.bot.requests, SetMyCommands)) == 1
    assert any(record.levelno == logging.ERROR and record.exc_info for record in caplog.records)


async def test_last_lists_entries_with_one_button_per_entry(harness: Harness) -> None:
    await harness.send("25 coffee")
    await harness.send("save 200 emergency")
    await harness.send("1200 uah taxi")
    await harness.send("+3000 salary")

    [request] = of(await harness.send("/last"), SendMessage)

    assert request.text == (
        "1. 01.11 +3,000.00 EUR salary\n"
        "2. 01.11 -1,200.00 UAH (no rate yet) taxi\n"
        "3. 01.11 +200.00 EUR emergency pot\n"
        "4. 01.11 -25.00 EUR coffee"
    )
    assert labels(request.reply_markup) == [
        ["1. salary +3,000.00 EUR"],
        ["2. taxi -1,200.00 UAH"],
        ["3. emergency pot +200.00 EUR"],
        ["4. coffee -25.00 EUR"],
    ]


async def test_last_when_empty_has_no_keyboard(harness: Harness) -> None:
    [request] = of(await harness.send("/last"), SendMessage)

    assert request.text == "No entries yet."
    assert request.reply_markup is None


async def test_last_shows_pending_and_converted_foreign_entries(harness: Harness) -> None:
    await harness.send("25 usd book")
    await harness.send("1200 uah taxi")
    await harness.send("/rate uah 0.022")

    [listing] = of(await harness.send("/last"), SendMessage)

    assert listing.text == (
        "1. 01.11 -1,200.00 UAH (≈ -26.40 EUR) taxi\n2. 01.11 -25.00 USD (no rate yet) book"
    )


async def test_savings_shows_pot_total_and_moves(harness: Harness) -> None:
    await harness.send("save 200 emergency")
    await harness.send("save 50 emergency")

    [request] = of(await harness.send("/savings"), SendMessage)

    assert request.text == "Emergency: 250.00 EUR\n  01.11 +50.00\n  01.11 +200.00"


async def test_goal_sets_the_target(harness: Harness) -> None:
    await harness.send("save 200 emergency")

    [request] = of(await harness.send("/goal emergency 10000"), SendMessage)

    assert request.text.startswith("Emergency: 200.00 EUR of 10,000.00 (2%)")
    [pot] = list_pots(harness.conn)
    assert pot.goal_cents == 1_000_000


@pytest.mark.parametrize(
    "command",
    [
        "/goal",
        "/goal emergency",
        "/goal emergency abc",
        "/goal 200 5000",
        "/goal emergency 10000 2027",
        "/goal emergency 10000 12.27",
        "/goal emergency 10000 12/2027",
        "/goal emergency 10000 1.2027",
        "/goal emergency 10000 13.2027",
        "/goal emergency 10000 00.2027",
        "/goal emergency 10000 2027.12",
        "/goal emergency 10000 12.2027 extra",
    ],
)
async def test_goal_usage_for_missing_or_bad_input(harness: Harness, command: str) -> None:
    [request] = of(await harness.send(command), SendMessage)

    assert request.text == GOAL_USAGE


async def test_goal_with_a_month_shows_the_monthly_amount(harness: Harness) -> None:
    await harness.send("save 300 emergency")

    [request] = of(await harness.send("/goal emergency 10000 12.2027"), SendMessage)

    assert request.text == (
        "Emergency: 300.00 EUR of 10,000.00 (3%) · by 12.2027: 692.86 EUR a month\n  01.11 +300.00"
    )
    [pot] = list_pots(harness.conn)
    assert (pot.goal_cents, pot.goal_month) == (1_000_000, "2027-12")


async def test_goal_without_a_month_clears_the_month(harness: Harness) -> None:
    await harness.send("save 300 emergency")
    await harness.send("/goal emergency 10000 12.2027")

    [request] = of(await harness.send("/goal emergency 5000"), SendMessage)

    assert request.text == "Emergency: 300.00 EUR of 5,000.00 (6%)\n  01.11 +300.00"
    [pot] = list_pots(harness.conn)
    assert (pot.goal_cents, pot.goal_month) == (500_000, None)


async def test_goal_for_this_month_is_allowed(harness: Harness) -> None:
    await harness.send("save 300 emergency")

    [request] = of(await harness.send("/goal emergency 10000 11.2026"), SendMessage)

    assert request.text.startswith(
        "Emergency: 300.00 EUR of 10,000.00 (3%) · by 11.2026: 9,700.00 EUR a month"
    )
    [pot] = list_pots(harness.conn)
    assert pot.goal_month == "2026-11"


async def test_goal_for_an_earlier_month_number_in_a_later_year_is_allowed(
    harness: Harness,
) -> None:
    await harness.send("save 300 emergency")

    [request] = of(await harness.send("/goal emergency 10000 03.2027"), SendMessage)

    assert request.text.startswith(
        "Emergency: 300.00 EUR of 10,000.00 (3%) · by 03.2027: 1,940.00 EUR a month"
    )
    [pot] = list_pots(harness.conn)
    assert pot.goal_month == "2027-03"


@pytest.mark.parametrize("month", ["10.2026", "01.2020"])
async def test_goal_for_a_month_that_has_passed_is_refused_and_stores_nothing(
    harness: Harness, month: str
) -> None:
    await harness.send("save 300 emergency")

    [request] = of(await harness.send(f"/goal emergency 10000 {month}"), SendMessage)

    assert request.text == GOAL_MONTH_PASSED
    [pot] = list_pots(harness.conn)
    assert (pot.goal_cents, pot.goal_month) == (None, None)


async def test_goal_already_reached_says_so(harness: Harness) -> None:
    await harness.send("save 300 emergency")

    [request] = of(await harness.send("/goal emergency 200 12.2027"), SendMessage)

    assert request.text.startswith("Emergency: 300.00 EUR of 200.00 (150%) · goal reached")


async def test_savings_shows_the_monthly_amount_for_a_goal_with_a_month(harness: Harness) -> None:
    await harness.send("save 300 emergency")
    await harness.send("/goal emergency 10000 12.2027")

    [request] = of(await harness.send("/savings"), SendMessage)

    assert request.text == (
        "Emergency: 300.00 EUR of 10,000.00 (3%) · by 12.2027: 692.86 EUR a month\n  01.11 +300.00"
    )


async def test_savings_says_when_the_goal_month_has_passed(harness: Harness) -> None:
    await harness.send("save 300 emergency")
    set_goal(harness.conn, "emergency", 1_000_000, "2026-10")

    [request] = of(await harness.send("/savings"), SendMessage)

    assert request.text == (
        "Emergency: 300.00 EUR of 10,000.00 (3%) · 10.2026 has passed\n  01.11 +300.00"
    )


async def test_goal_for_unknown_pot_is_refused(harness: Harness) -> None:
    [request] = of(await harness.send("/goal nope 100"), SendMessage)

    assert request.text == "No pot named nope yet. Start it with: save 100 nope"


async def test_goal_with_pot_name_over_30_letters_is_usage(harness: Harness) -> None:
    [request] = of(await harness.send("/goal " + "a" * 31 + " 5000"), SendMessage)

    assert request.text == GOAL_USAGE


async def test_goal_for_pot_with_30_letter_name_sets_the_target(harness: Harness) -> None:
    name = "a" * 30
    await harness.send(f"save 100 {name}")

    [request] = of(await harness.send(f"/goal {name} 5000"), SendMessage)

    assert request.text.startswith(f"{name.capitalize()}: 100.00 EUR of 5,000.00 (2%)")
    [pot] = list_pots(harness.conn)
    assert pot.goal_cents == 500_000


@pytest.mark.parametrize(
    "command",
    ["/rate", "/rate usd", "/rate eur 1", "/rate gbp 1", "/rate usd abc", "/rate usd 0"],
)
async def test_rate_usage_for_missing_or_bad_input(harness: Harness, command: str) -> None:
    [request] = of(await harness.send(command), SendMessage)

    assert request.text == RATE_USAGE


async def test_rate_code_is_accepted_in_any_case(harness: Harness) -> None:
    [request] = of(await harness.send("/rate USD 0.92"), SendMessage)

    assert request.text == "Saved: 1 USD = 0.92 EUR."


@pytest.mark.parametrize(
    ("command", "message"),
    [
        ("/rate usd 092", USD_RATE_RANGE),
        ("/rate usd 0.4", USD_RATE_RANGE),
        ("/rate usd 2.01", USD_RATE_RANGE),
        ("/rate uah 0.000001", UAH_RATE_RANGE),
        ("/rate uah 0.2", UAH_RATE_RANGE),
    ],
)
async def test_rate_outside_the_range_is_refused_and_not_stored(
    harness: Harness, command: str, message: str
) -> None:
    await harness.send("/rate usd 0.93")
    stored = rate_rows(harness.conn)

    [request] = of(await harness.send(command), SendMessage)

    assert request.text == message
    assert rate_rows(harness.conn) == stored


@pytest.mark.parametrize(
    ("command", "reply"),
    [
        ("/rate usd 0.5", "Saved: 1 USD = 0.5 EUR."),
        ("/rate usd 2", "Saved: 1 USD = 2 EUR."),
        ("/rate uah 0.005", "Saved: 1 UAH = 0.005 EUR."),
        ("/rate uah 0.1", "Saved: 1 UAH = 0.1 EUR."),
    ],
)
async def test_rate_at_the_range_limits_is_accepted(
    harness: Harness, command: str, reply: str
) -> None:
    [request] = of(await harness.send(command), SendMessage)

    assert request.text == reply


async def test_rate_command_stores_the_rate_with_todays_date(harness: Harness) -> None:
    await harness.send("/rate usd 0.92")

    assert rate_rows(harness.conn) == [("USD", "0.92", "2026-11-01")]


async def test_rate_command_converts_the_pending_entry_in_the_database(harness: Harness) -> None:
    await harness.send("1200 uah taxi")
    entry_id = newest_id(harness.conn)

    await harness.send("/rate uah 0.022")

    row = harness.conn.execute(
        "SELECT eur_cents, rate FROM entries WHERE id = ?", (entry_id,)
    ).fetchone()
    assert (row["eur_cents"], row["rate"]) == (2640, "0.022")


async def test_rate_reply_lists_the_pending_entry_it_converted(harness: Harness) -> None:
    await harness.send("25 usd book")
    entry_id = newest_id(harness.conn)

    [rate] = of(await harness.send("/rate usd 0.92"), SendMessage)

    assert rate.text == (
        "Saved: 1 USD = 0.92 EUR.\n"
        "Converted 1 entry that was waiting for this rate:\n"
        "01.11 -25.00 USD book = -23.00 EUR"
    )
    row = harness.conn.execute(
        "SELECT eur_cents, rate FROM entries WHERE id = ?", (entry_id,)
    ).fetchone()
    assert (row["eur_cents"], row["rate"]) == (2300, "0.92")


@pytest.mark.parametrize("command", ["/month 10", "/month 2026-10"])
async def test_month_argument_selects_the_month(harness: Harness, command: str) -> None:
    [request] = of(await harness.send(command), SendMessage)

    assert request.parse_mode == "HTML"
    assert request.text.startswith("<pre>October 2026")


async def test_month_with_bad_argument_is_plain_text(harness: Harness) -> None:
    [request] = of(await harness.send("/month 13"), SendMessage)

    assert request.text == "Use a month like /month 10 or /month 2026-10"
    assert request.parse_mode != "HTML"


async def test_month_report_is_sent_as_html_pre_block(harness: Harness) -> None:
    [request] = of(await harness.send("/month"), SendMessage)

    assert request.parse_mode == "HTML"
    assert request.text.startswith("<pre>November 2026")


async def test_long_month_report_is_sent_as_several_pre_blocks_in_order(
    harness: Harness,
) -> None:
    fill_long_month(harness.conn, TODAY)
    text = render_month(build_month_report(harness.conn, 2026, 11))
    assert len(text) > 4000

    requests = of(await harness.send("/month"), SendMessage)

    assert len(requests) >= 2
    assert all(request.parse_mode == "HTML" for request in requests)
    assert all(len(request.text) < 4096 for request in requests)
    assert all(request.text.startswith("<pre>") for request in requests)
    assert all(request.text.endswith("</pre>") for request in requests)
    assert requests[0].text.startswith("<pre>November 2026")
    shown = [request.text.removeprefix("<pre>").removesuffix("</pre>") for request in requests]
    assert "\n\n".join(shown) == text


async def test_export_is_sent_as_csv_document(harness: Harness) -> None:
    [request] = of(await harness.send("/export"), SendDocument)

    assert isinstance(request.document, BufferedInputFile)
    assert request.document.filename == "finbot-export-2026-11-01.csv"


async def test_change_category_shows_expense_categories_three_per_row(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)

    [edit] = of(
        await harness.press(EntryCb(action="cat", entry_id=entry_id).pack()),
        EditMessageReplyMarkup,
    )

    rows = labels(edit.reply_markup)
    assert [len(row) for row in rows] == [3, 3, 3, 3]
    assert [name for row in rows for name in row] == [
        c.name for c in list_categories(harness.conn, "expense")
    ]


async def test_undo_button_removes_the_entry(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)

    requests = await harness.press(EntryCb(action="undo", entry_id=entry_id).pack())

    assert len(of(requests, AnswerCallbackQuery)) == 1
    [edit] = of(requests, EditMessageText)
    assert edit.text == "Removed 01.11: -25.00 EUR · coffee"
    assert edit.reply_markup is None
    assert is_soft_deleted(harness.conn, entry_id)


async def test_delete_button_in_the_record_view_removes_the_entry_and_offers_back(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    view = await open_entry(harness, "1. coffee -25.00 EUR")

    requests = await harness.press(callback_data(view.reply_markup, "Delete"))

    assert len(of(requests, AnswerCallbackQuery)) == 1
    [edit] = of(requests, EditMessageText)
    assert edit.text == "Removed 01.11: -25.00 EUR · coffee"
    assert labels(edit.reply_markup) == [["Back to list"]]
    assert EntryCb.unpack(callback_data(edit.reply_markup, "Back to list")) == EntryCb(
        action="back", entry_id=0
    )
    assert is_soft_deleted(harness.conn, entry_id)


async def test_undo_button_from_the_first_confirmation_removes_only_that_entry(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    first_id = newest_id(harness.conn)
    eating_out = category(harness.conn, "Eating out")
    [confirmed] = of(
        await harness.press(PickCb(entry_id=first_id, category_id=eating_out.id).pack()),
        EditMessageText,
    )
    undo = callback_data(confirmed.reply_markup, "Undo")
    await harness.send("30 coffee")
    second_id = newest_id(harness.conn)

    await harness.press(undo)

    assert is_soft_deleted(harness.conn, first_id)
    assert not is_soft_deleted(harness.conn, second_id)


async def test_confirmation_undo_button_is_an_undo_action_for_its_entry(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    eating_out = category(harness.conn, "Eating out")
    [confirmed] = of(
        await harness.press(PickCb(entry_id=entry_id, category_id=eating_out.id).pack()),
        EditMessageText,
    )

    undo = EntryCb.unpack(callback_data(confirmed.reply_markup, "Undo"))

    assert undo == EntryCb(action="undo", entry_id=entry_id)


async def test_delete_button_in_the_record_view_removes_only_its_own_entry(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    coffee_id = newest_id(harness.conn)
    await harness.send("30 taxi")
    taxi_id = newest_id(harness.conn)
    view = await open_entry(harness, "2. coffee -25.00 EUR")

    await harness.press(callback_data(view.reply_markup, "Delete"))

    assert is_soft_deleted(harness.conn, coffee_id)
    assert not is_soft_deleted(harness.conn, taxi_id)


async def test_last_buttons_carry_each_records_own_id(harness: Harness) -> None:
    await harness.send("25 coffee")
    coffee_id = newest_id(harness.conn)
    await harness.send("30 taxi")
    taxi_id = newest_id(harness.conn)
    [listing] = of(await harness.send("/last"), SendMessage)

    unpacked = {
        label: EntryCb.unpack(callback_data(listing.reply_markup, label))
        for label in ("1. taxi -30.00 EUR", "2. coffee -25.00 EUR")
    }

    assert unpacked == {
        "1. taxi -30.00 EUR": EntryCb(action="open", entry_id=taxi_id),
        "2. coffee -25.00 EUR": EntryCb(action="open", entry_id=coffee_id),
    }


async def test_new_word_keyboard_carries_the_real_entry_id_and_categories(
    harness: Harness,
) -> None:
    [request] = of(await harness.send("25 taxi"), SendMessage)
    entry_id = newest_id(harness.conn)
    categories = list_categories(harness.conn, "expense")

    picks = [PickCb.unpack(callback_data(request.reply_markup, c.name)) for c in categories]

    assert picks == [PickCb(entry_id=entry_id, category_id=c.id) for c in categories]


async def test_picking_transport_from_the_new_word_keyboard_sets_transport(
    harness: Harness,
) -> None:
    [request] = of(await harness.send("25 taxi"), SendMessage)
    transport = category(harness.conn, "Transport")

    [edit] = of(
        await harness.press(callback_data(request.reply_markup, "Transport")), EditMessageText
    )

    assert edit.text == "Saved 01.11: -25.00 EUR · taxi → Transport"
    assert category_for_keyword(harness.conn, "taxi", "expense") == transport


@pytest.mark.parametrize(("user_id", "group"), [(7, False), (OWNER_ID, True)])
async def test_callbacks_from_others_are_ignored(
    harness: Harness, user_id: int, group: bool
) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)

    requests = await harness.press(
        EntryCb(action="del", entry_id=entry_id).pack(), user_id=user_id, group=group
    )

    assert requests == []
    assert get_record(harness.conn, entry_id) is not None


async def test_queued_failure_raises_the_aiogram_error(harness: Harness) -> None:
    harness.bot.add_result_for(
        SendDocument, ok=False, error_code=400, description="Bad Request: boom"
    )

    with pytest.raises(TelegramBadRequest) as error:
        await harness.send("/export")

    assert error.value.message == "Bad Request: boom"


async def test_stale_undo_callback_says_nothing_to_undo(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    undo = EntryCb(action="undo", entry_id=entry_id).pack()
    await harness.press(undo)

    requests = await harness.press(undo)

    [answer] = of(requests, AnswerCallbackQuery)
    assert answer.text == "Nothing to undo."
    assert of(requests, EditMessageText) == []


async def test_pick_change_and_delete_on_a_deleted_entry_say_already_deleted(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    await harness.send("/undo")
    eating_out = category(harness.conn, "Eating out")

    pick = await harness.press(PickCb(entry_id=entry_id, category_id=eating_out.id).pack())
    change = await harness.press(EntryCb(action="cat", entry_id=entry_id).pack())
    delete = await harness.press(EntryCb(action="del", entry_id=entry_id).pack())

    for requests in (pick, change, delete):
        assert [a.text for a in of(requests, AnswerCallbackQuery)] == ["Already deleted."]
        assert of(requests, EditMessageText) == []
        assert of(requests, EditMessageReplyMarkup) == []


async def test_change_category_on_a_pot_move_answers_without_text(harness: Harness) -> None:
    await harness.send("save 200 emergency")
    entry_id = newest_id(harness.conn)

    requests = await harness.press(EntryCb(action="cat", entry_id=entry_id).pack())

    assert [a.text for a in of(requests, AnswerCallbackQuery)] == [None]
    assert of(requests, EditMessageReplyMarkup) == []


async def test_pick_with_unknown_category_is_still_answered(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)

    with pytest.raises(sqlite3.IntegrityError):
        await harness.press(PickCb(entry_id=entry_id, category_id=9999).pack())

    assert len(of(harness.bot.requests, AnswerCallbackQuery)) == 1


async def test_unknown_callback_action_is_answered(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)

    requests = await harness.press(EntryCb(action="zzz", entry_id=entry_id).pack())

    assert len(of(requests, AnswerCallbackQuery)) == 1
    assert of(requests, EditMessageText) == []
    assert get_record(harness.conn, entry_id) is not None


async def test_repicking_the_same_category_is_not_an_error(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    pick = PickCb(entry_id=entry_id, category_id=category(harness.conn, "Eating out").id).pack()
    await harness.press(pick)
    harness.bot.add_result_for(EditMessageText, ok=False, error_code=400, description=NOT_MODIFIED)

    requests = await harness.press(pick)

    assert len(of(requests, AnswerCallbackQuery)) == 1


async def test_change_category_twice_is_not_an_error(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    change = EntryCb(action="cat", entry_id=entry_id).pack()
    await harness.press(change)
    harness.bot.add_result_for(
        EditMessageReplyMarkup, ok=False, error_code=400, description=NOT_MODIFIED
    )

    requests = await harness.press(change)

    assert len(of(requests, AnswerCallbackQuery)) == 1


async def test_other_edit_errors_still_raise_and_callback_is_answered(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    harness.bot.add_result_for(
        EditMessageText,
        ok=False,
        error_code=400,
        description="Bad Request: message to edit not found",
    )

    with pytest.raises(TelegramBadRequest):
        await harness.press(
            PickCb(entry_id=entry_id, category_id=category(harness.conn, "Eating out").id).pack()
        )

    assert len(of(harness.bot.requests, AnswerCallbackQuery)) == 1


async def test_keyboard_callback_data_fits_telegram_limit(harness: Harness) -> None:
    big_id = 10**9
    expense = Record(
        id=big_id,
        kind="expense",
        amount_cents=100,
        currency="EUR",
        rate=None,
        eur_cents=100,
        category=None,
        pot=None,
        keyword="taxi",
        note="taxi",
        on=TODAY,
    )
    pot_move = replace(expense, kind="save", pot="emergency")
    markups = [
        entry_keyboard(big_id),
        category_keyboard(big_id, list_categories(harness.conn, "expense")),
        last_keyboard([expense, pot_move]),
        record_keyboard(expense),
        back_keyboard(),
    ]

    for markup in markups:
        for button in buttons(markup):
            assert button.callback_data is not None
            assert len(button.callback_data.encode()) <= 64


@pytest.mark.parametrize(
    ("note", "shown"),
    [("a" * 20, "a" * 20), ("a" * 21, "a" * 20), ("a" * 40, "a" * 20)],
)
def test_last_button_label_is_cut_to_20_characters(note: str, shown: str) -> None:
    record = Record(
        id=1,
        kind="expense",
        amount_cents=4200,
        currency="EUR",
        rate=None,
        eur_cents=4200,
        category=None,
        pot=None,
        keyword="dm",
        note=note,
        on=TODAY,
    )

    assert labels(last_keyboard([record])) == [[f"1. {shown} -42.00 EUR"]]


async def test_open_shows_the_record_with_change_category_delete_and_back(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    [listing] = of(await harness.send("/last"), SendMessage)

    requests = await harness.press(callback_data(listing.reply_markup, "1. coffee -25.00 EUR"))

    assert len(of(requests, AnswerCallbackQuery)) == 1
    [edit] = of(requests, EditMessageText)
    assert edit.text == "01.11 -25.00 EUR coffee"
    assert labels(edit.reply_markup) == [["Change category", "Delete"], ["Back to list"]]
    assert EntryCb.unpack(callback_data(edit.reply_markup, "Change category")) == EntryCb(
        action="cat", entry_id=entry_id
    )
    assert EntryCb.unpack(callback_data(edit.reply_markup, "Delete")) == EntryCb(
        action="del", entry_id=entry_id
    )
    assert EntryCb.unpack(callback_data(edit.reply_markup, "Back to list")) == EntryCb(
        action="back", entry_id=0
    )
    assert not is_soft_deleted(harness.conn, entry_id)


async def test_open_income_offers_change_category(harness: Harness) -> None:
    await harness.send("+3000 salary")

    view = await open_entry(harness, "1. salary +3,000.00 EUR")

    assert view.text == "01.11 +3,000.00 EUR salary"
    assert labels(view.reply_markup) == [["Change category", "Delete"], ["Back to list"]]


async def test_open_pot_move_has_no_change_category_button(harness: Harness) -> None:
    await harness.send("save 200 emergency")

    view = await open_entry(harness, "1. emergency pot +200.00 EUR")

    assert view.text == "01.11 +200.00 EUR emergency pot"
    assert labels(view.reply_markup) == [["Delete"], ["Back to list"]]


async def test_open_of_a_deleted_record_says_already_deleted_and_changes_nothing(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    [listing] = of(await harness.send("/last"), SendMessage)
    await harness.send("/undo")

    requests = await harness.press(callback_data(listing.reply_markup, "1. coffee -25.00 EUR"))

    [answer] = of(requests, AnswerCallbackQuery)
    assert answer.text == "Already deleted."
    assert of(requests, EditMessageText) == []
    assert of(requests, EditMessageReplyMarkup) == []


async def test_back_restores_the_current_list(harness: Harness) -> None:
    await harness.send("25 coffee")
    await harness.send("30 taxi")
    view = await open_entry(harness, "1. taxi -30.00 EUR")

    requests = await harness.press(callback_data(view.reply_markup, "Back to list"))

    assert len(of(requests, AnswerCallbackQuery)) == 1
    [edit] = of(requests, EditMessageText)
    assert edit.text == "1. 01.11 -30.00 EUR taxi\n2. 01.11 -25.00 EUR coffee"
    assert labels(edit.reply_markup) == [["1. taxi -30.00 EUR"], ["2. coffee -25.00 EUR"]]


async def test_back_after_delete_lists_the_remaining_entries(harness: Harness) -> None:
    await harness.send("25 coffee")
    await harness.send("30 taxi")
    view = await open_entry(harness, "1. taxi -30.00 EUR")
    [removed] = of(await harness.press(callback_data(view.reply_markup, "Delete")), EditMessageText)

    [edit] = of(
        await harness.press(callback_data(removed.reply_markup, "Back to list")), EditMessageText
    )

    assert edit.text == "1. 01.11 -25.00 EUR coffee"
    assert labels(edit.reply_markup) == [["1. coffee -25.00 EUR"]]


async def test_back_with_no_entries_left_shows_no_entries_and_no_keyboard(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    view = await open_entry(harness, "1. coffee -25.00 EUR")
    [removed] = of(await harness.press(callback_data(view.reply_markup, "Delete")), EditMessageText)

    requests = await harness.press(callback_data(removed.reply_markup, "Back to list"))

    [edit] = of(requests, EditMessageText)
    assert edit.text == "No entries yet."
    assert edit.reply_markup is None
    assert len(of(requests, AnswerCallbackQuery)) == 1


async def test_change_category_from_the_record_view_shows_the_categories(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    view = await open_entry(harness, "1. coffee -25.00 EUR")

    [edit] = of(
        await harness.press(callback_data(view.reply_markup, "Change category")),
        EditMessageReplyMarkup,
    )

    assert [name for row in labels(edit.reply_markup) for name in row] == [
        c.name for c in list_categories(harness.conn, "expense")
    ]


async def test_delete_of_an_already_deleted_record_says_already_deleted(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    view = await open_entry(harness, "1. coffee -25.00 EUR")
    delete = callback_data(view.reply_markup, "Delete")
    await harness.press(delete)

    requests = await harness.press(delete)

    [answer] = of(requests, AnswerCallbackQuery)
    assert answer.text == "Already deleted."
    assert of(requests, EditMessageText) == []


@pytest.mark.parametrize("action", ["open", "back"])
async def test_open_and_back_ignore_message_not_modified(harness: Harness, action: str) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    harness.bot.add_result_for(EditMessageText, ok=False, error_code=400, description=NOT_MODIFIED)

    requests = await harness.press(EntryCb(action=action, entry_id=entry_id).pack())

    assert len(of(requests, EditMessageText)) == 1
    assert len(of(requests, AnswerCallbackQuery)) == 1


@pytest.mark.parametrize("action", ["open", "back"])
async def test_open_and_back_answer_the_callback_when_the_edit_fails(
    harness: Harness, action: str
) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    harness.bot.add_result_for(
        EditMessageText, ok=False, error_code=400, description="Bad Request: boom"
    )

    with pytest.raises(TelegramBadRequest):
        await harness.press(EntryCb(action=action, entry_id=entry_id).pack())

    assert len(of(harness.bot.requests, AnswerCallbackQuery)) == 1


async def test_buttons_already_sent_in_the_chat_keep_working(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    eating_out = category(harness.conn, "Eating out")

    change = await harness.press(f"e:cat:{entry_id}")
    pick = await harness.press(f"p:{entry_id}:{eating_out.id}")
    delete = await harness.press(f"e:del:{entry_id}")

    assert len(of(change, EditMessageReplyMarkup)) == 1
    [saved] = of(pick, EditMessageText)
    assert saved.text == "Saved 01.11: -25.00 EUR · coffee → Eating out"
    [removed] = of(delete, EditMessageText)
    assert removed.text == "Removed 01.11: -25.00 EUR · coffee"
    assert labels(removed.reply_markup) == [["Back to list"]]
    assert is_soft_deleted(harness.conn, entry_id)


async def test_old_undo_data_still_removes_the_entry_without_back(harness: Harness) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)

    [edit] = of(await harness.press(f"e:undo:{entry_id}"), EditMessageText)

    assert edit.reply_markup is None
    assert is_soft_deleted(harness.conn, entry_id)


async def save_and_take(harness: Harness) -> tuple[int, int]:
    await harness.send("save 100 emergency")
    save_id = newest_id(harness.conn)
    await harness.send("take 80 emergency")
    return save_id, newest_id(harness.conn)


async def test_undo_refuses_a_save_that_would_take_a_pot_below_zero(harness: Harness) -> None:
    old_save_id, _ = await save_and_take(harness)
    # A pot that is already below zero, as the old delete rule could leave it.
    with harness.conn:
        harness.conn.execute("UPDATE entries SET deleted_at = 'x' WHERE id = ?", (old_save_id,))
    await harness.send("save 10 emergency")
    newest = newest_id(harness.conn)

    [reply] = of(await harness.send("/undo"), SendMessage)

    assert reply.text == BELOW_ZERO
    assert not is_soft_deleted(harness.conn, newest)


@pytest.mark.parametrize("action", ["undo", "del"])
async def test_delete_callbacks_refuse_a_save_that_the_takes_already_used(
    harness: Harness, action: str
) -> None:
    save_id, _ = await save_and_take(harness)

    requests = await harness.press(EntryCb(action=action, entry_id=save_id).pack())

    [answer] = of(requests, AnswerCallbackQuery)
    assert answer.text == BELOW_ZERO
    assert of(requests, EditMessageText) == []
    assert not is_soft_deleted(harness.conn, save_id)


async def test_delete_callback_allows_a_save_that_leaves_exactly_zero(harness: Harness) -> None:
    save_id, _ = await save_and_take(harness)
    await harness.send("save 80 emergency")

    requests = await harness.press(EntryCb(action="del", entry_id=save_id).pack())

    [edit] = of(requests, EditMessageText)
    assert edit.text == "Removed 01.11: +100.00 EUR · emergency pot"
    assert is_soft_deleted(harness.conn, save_id)
    [pot] = list_pots(harness.conn)
    assert pot.total_cents == 0


async def test_delete_callback_still_removes_a_take(harness: Harness) -> None:
    _, take_id = await save_and_take(harness)

    requests = await harness.press(EntryCb(action="del", entry_id=take_id).pack())

    [edit] = of(requests, EditMessageText)
    assert edit.text == "Removed 01.11: -80.00 EUR · emergency pot"
    [pot] = list_pots(harness.conn)
    assert pot.total_cents == 10000


async def test_refused_delete_in_the_record_view_leaves_the_savings_unchanged(
    harness: Harness,
) -> None:
    await save_and_take(harness)
    view = await open_entry(harness, "2. emergency pot +100.00 EUR")

    requests = await harness.press(callback_data(view.reply_markup, "Delete"))

    [answer] = of(requests, AnswerCallbackQuery)
    assert answer.text == BELOW_ZERO
    assert of(requests, EditMessageText) == []
    [savings] = of(await harness.send("/savings"), SendMessage)
    assert savings.text == "Emergency: 20.00 EUR\n  01.11 -80.00\n  01.11 +100.00"


async def test_record_view_change_category_and_pick_ends_in_the_saved_reply(
    harness: Harness,
) -> None:
    await harness.send("25 coffee")
    entry_id = newest_id(harness.conn)
    view = await open_entry(harness, "1. coffee -25.00 EUR")
    [picker] = of(
        await harness.press(callback_data(view.reply_markup, "Change category")),
        EditMessageReplyMarkup,
    )

    requests = await harness.press(callback_data(picker.reply_markup, "Groceries"))

    [edit] = of(requests, EditMessageText)
    assert edit.text == "Saved 01.11: -25.00 EUR · coffee → Groceries"
    assert labels(edit.reply_markup) == [["Change category", "Undo"]]
    assert EntryCb.unpack(callback_data(edit.reply_markup, "Undo")) == EntryCb(
        action="undo", entry_id=entry_id
    )
    record = get_record(harness.conn, entry_id)
    assert record is not None
    assert record.category == "Groceries"


async def test_goal_savings_and_month_work_on_a_database_upgraded_from_version_1(
    tmp_path: Path,
) -> None:
    path = tmp_path / "v1.db"
    _make_version_1_database(path)
    with closing(connect(path)) as conn:
        harness = Harness(conn)

        [goal] = of(await harness.send("/goal emergency 10000 12.2027"), SendMessage)
        [savings] = of(await harness.send("/savings"), SendMessage)
        [month] = of(await harness.send("/month 10"), SendMessage)

    expected = (
        "Emergency: 300.00 EUR of 10,000.00 (3%) · by 12.2027: 692.86 EUR a month\n  31.10 +300.00"
    )
    assert goal.text == expected
    assert savings.text == expected
    assert month.text.startswith("<pre>October 2026")
    assert "coffee" in month.text or "Eating out" in month.text


def category_names(conn: sqlite3.Connection, kind: str) -> list[str]:
    return [c.name for c in list_categories(conn, kind)]


async def reply_to(harness: Harness, text: str) -> str:
    [request] = of(await harness.send(text), SendMessage)
    assert request.parse_mode != "HTML"
    return request.text


async def test_category_without_words_lists_both_kinds_in_position_order(
    harness: Harness,
) -> None:
    assert await reply_to(harness, "/category") == (
        f"Expense: {SEED_EXPENSE}\n"
        "Income: Salary, Freelance, Other income\n"
        "Add: /category add Rent · Rename: /category rename Rent Housing"
    )


async def test_category_list_shows_added_and_renamed_categories(harness: Harness) -> None:
    await harness.send("/category add Rent")
    await harness.send("/category add income Bonus")
    await harness.send("/category rename Salary Pay")

    assert await reply_to(harness, "/category") == (
        f"Expense: {SEED_EXPENSE}, Rent\n"
        "Income: Pay, Freelance, Other income, Bonus\n"
        "Add: /category add Rent · Rename: /category rename Rent Housing"
    )


async def test_category_add_creates_an_expense_category_last_in_its_kind(
    harness: Harness,
) -> None:
    assert await reply_to(harness, "/category add Rent") == "Added expense category Rent."

    assert category_names(harness.conn, "expense")[-2:] == ["Other", "Rent"]
    assert category_names(harness.conn, "income") == ["Salary", "Freelance", "Other income"]


async def test_category_add_income_creates_an_income_category_last_in_its_kind(
    harness: Harness,
) -> None:
    assert await reply_to(harness, "/category add income Bonus") == "Added income category Bonus."

    assert category_names(harness.conn, "income") == [
        "Salary",
        "Freelance",
        "Other income",
        "Bonus",
    ]
    assert category_names(harness.conn, "expense")[-1] == "Other"


async def test_category_add_accepts_the_words_in_any_case(harness: Harness) -> None:
    assert await reply_to(harness, "/category ADD Income Bonus") == "Added income category Bonus."


async def test_category_add_trims_and_collapses_spaces_in_the_name(harness: Harness) -> None:
    assert await reply_to(harness, "/category add   Pet    food  ") == (
        "Added expense category Pet food."
    )


async def test_category_add_keeps_a_name_with_html_characters_as_plain_text(
    harness: Harness,
) -> None:
    assert await reply_to(harness, "/category add R&D <1>") == "Added expense category R&D <1>."


async def test_category_add_accepts_a_30_character_name_in_another_alphabet(
    harness: Harness,
) -> None:
    name = "К" * 30
    assert await reply_to(harness, f"/category add {name}") == f"Added expense category {name}."


async def test_new_expense_category_is_the_last_button_for_a_new_word(harness: Harness) -> None:
    await harness.send("/category add Rent")

    [request] = of(await harness.send("900 landlord"), SendMessage)

    assert [b.text for b in buttons(request.reply_markup)][-2:] == ["Other", "Rent"]
    assert len(buttons(request.reply_markup)) == 13
    for button in buttons(request.reply_markup):
        assert button.callback_data is not None
        assert len(button.callback_data.encode()) <= 64


async def test_picking_a_new_category_files_the_entry_and_the_word(harness: Harness) -> None:
    await harness.send("/category add Rent")
    [request] = of(await harness.send("900 landlord"), SendMessage)

    [edit] = of(await harness.press(callback_data(request.reply_markup, "Rent")), EditMessageText)

    assert edit.text == "Saved 01.11: -900.00 EUR · landlord → Rent"
    known = category_for_keyword(harness.conn, "landlord", "expense")
    assert known is not None
    assert known.name == "Rent"


async def test_new_income_category_is_the_last_button_for_a_new_income_word(
    harness: Harness,
) -> None:
    await harness.send("/category add income Bonus")

    [request] = of(await harness.send("+500 xmas"), SendMessage)

    assert [b.text for b in buttons(request.reply_markup)] == [
        "Salary",
        "Freelance",
        "Other income",
        "Bonus",
    ]


@pytest.mark.parametrize(
    ("setup", "command", "existing"),
    [
        ("/category add Rent", "/category add Rent", "Rent"),
        ("/category add Rent", "/category add rent", "Rent"),
        ("/category add Rent", "/category add income RENT", "Rent"),
        ("/category add income Bonus", "/category add bonus", "Bonus"),
        (
            "/category add Кафе",
            "/category add кафе",
            "Кафе",
        ),
        ("/category", "/category add groceries", "Groceries"),
        ("/category", "/category add income eating out", "Eating out"),
        ("/category", "/category add Salary", "Salary"),
    ],
)
async def test_category_add_refuses_a_name_that_exists_in_either_kind_in_any_case(
    harness: Harness, setup: str, command: str, existing: str
) -> None:
    await harness.send(setup)
    before = (category_names(harness.conn, "expense"), category_names(harness.conn, "income"))

    assert await reply_to(harness, command) == f"There is already a category {existing}."

    assert (
        category_names(harness.conn, "expense"),
        category_names(harness.conn, "income"),
    ) == before


@pytest.mark.parametrize(
    "command",
    [
        "/category add",
        "/category add income",
        "/category add Income",
        f"/category add {'a' * 31}",
        f"/category add income {'a' * 31}",
        "/category add 2026",
        "/category add income 12 34",
        "/category add /rent",
        "/category add income /bonus",
        "/category add !!!",
        "/category add Uncategorized",
        "/category add income UNCATEGORIZED",
    ],
)
async def test_category_add_with_a_bad_or_missing_name_shows_the_usage(
    harness: Harness, command: str
) -> None:
    assert await reply_to(harness, command) == CATEGORY_ADD_USAGE

    assert len(category_names(harness.conn, "expense")) == 12
    assert len(category_names(harness.conn, "income")) == 3


async def test_category_add_allows_the_30th_expense_category_and_refuses_the_31st(
    harness: Harness,
) -> None:
    for number in range(17):
        add_category(harness.conn, f"Extra {number}", "expense")
    assert len(category_names(harness.conn, "expense")) == 29

    assert await reply_to(harness, "/category add Thirtieth") == (
        "Added expense category Thirtieth."
    )
    assert await reply_to(harness, "/category add Thirty first") == (
        "Up to 30 expense categories. Rename one instead: /category rename Old New"
    )

    assert len(category_names(harness.conn, "expense")) == 30
    assert await reply_to(harness, "/category add income Bonus") == "Added income category Bonus."


async def test_category_add_refuses_the_31st_income_category(harness: Harness) -> None:
    for number in range(27):
        add_category(harness.conn, f"Extra {number}", "income")
    assert len(category_names(harness.conn, "income")) == 30

    assert await reply_to(harness, "/category add income Bonus") == (
        "Up to 30 income categories. Rename one instead: /category rename Old New"
    )

    assert len(category_names(harness.conn, "income")) == 30


async def test_category_rename_takes_a_two_word_old_name(harness: Harness) -> None:
    assert await reply_to(harness, "/category rename Eating out Food") == (
        "Renamed Eating out to Food."
    )

    assert category_names(harness.conn, "expense")[:3] == ["Groceries", "Food", "Transport"]


async def test_category_rename_matches_the_old_name_in_any_case_and_shows_it_as_stored(
    harness: Harness,
) -> None:
    assert await reply_to(harness, "/category rename eating OUT Food") == (
        "Renamed Eating out to Food."
    )


async def test_category_rename_takes_the_longest_leading_run_that_matches(
    harness: Harness,
) -> None:
    await harness.send("/category add Eating")

    assert await reply_to(harness, "/category rename Eating out Food") == (
        "Renamed Eating out to Food."
    )

    assert "Eating" in category_names(harness.conn, "expense")


async def test_category_rename_takes_the_rest_of_the_line_as_the_new_name(
    harness: Harness,
) -> None:
    assert await reply_to(harness, "/category rename Other Misc  stuff") == (
        "Renamed Other to Misc stuff."
    )

    assert category_names(harness.conn, "expense")[-1] == "Misc stuff"


async def test_category_rename_works_for_an_income_category(harness: Harness) -> None:
    assert await reply_to(harness, "/category rename Salary Pay") == "Renamed Salary to Pay."

    assert category_names(harness.conn, "income") == ["Pay", "Freelance", "Other income"]


async def test_category_rename_can_change_only_the_case(harness: Harness) -> None:
    assert await reply_to(harness, "/category rename groceries GROCERIES") == (
        "Renamed Groceries to GROCERIES."
    )

    assert category_names(harness.conn, "expense")[0] == "GROCERIES"


@pytest.mark.parametrize(
    "command",
    ["/category rename Eating Food", "/category rename Nope Food", "/category rename Nope"],
)
async def test_category_rename_with_an_unknown_old_name_points_to_the_list(
    harness: Harness, command: str
) -> None:
    word = command.split()[2]

    assert await reply_to(harness, command) == f"No category named {word}. See /category"

    assert category_names(harness.conn, "expense")[1] == "Eating out"


@pytest.mark.parametrize(
    ("command", "existing"),
    [
        ("/category rename Eating out Groceries", "Groceries"),
        ("/category rename Eating out groceries", "Groceries"),
        ("/category rename Eating out salary", "Salary"),
        ("/category rename Salary eating out", "Eating out"),
    ],
)
async def test_category_rename_refuses_a_name_another_category_has(
    harness: Harness, command: str, existing: str
) -> None:
    assert await reply_to(harness, command) == f"There is already a category {existing}."

    assert len(category_names(harness.conn, "expense")) == 12
    assert category_names(harness.conn, "expense")[1] == "Eating out"
    assert category_names(harness.conn, "income")[0] == "Salary"


@pytest.mark.parametrize(
    "command",
    [
        "/category rename",
        "/category rename Eating out",
        "/category rename Eating out 2026",
        "/category rename Eating out /food",
        f"/category rename Eating out {'a' * 31}",
        "/category rename Eating out Uncategorized",
        "/category rename Eating out uncategorized",
    ],
)
async def test_category_rename_with_a_bad_or_missing_new_name_shows_the_usage(
    harness: Harness, command: str
) -> None:
    assert await reply_to(harness, command) == CATEGORY_RENAME_USAGE

    assert category_names(harness.conn, "expense")[1] == "Eating out"


async def test_renamed_category_keeps_its_word_and_entries_and_shows_in_the_month_report(
    harness: Harness,
) -> None:
    [first] = of(await harness.send("25 coffee"), SendMessage)
    await harness.press(callback_data(first.reply_markup, "Eating out"))
    await harness.send("/category rename Eating out Food")

    kept = category_for_keyword(harness.conn, "coffee", "expense")
    assert kept is not None
    assert kept.name == "Food"
    [second] = of(await harness.send("30 coffee"), SendMessage)
    assert second.text == "Saved 01.11: -30.00 EUR · coffee → Food"
    [month] = of(await harness.send("/month"), SendMessage)
    assert "Food" in month.text
    assert "Eating out" not in month.text


@pytest.mark.parametrize(
    "command",
    ["/category delete Other", "/category remove Other", "/category Other", "/category add2 Rent"],
)
async def test_category_with_any_other_words_shows_the_usage_and_deletes_nothing(
    harness: Harness, command: str
) -> None:
    assert await reply_to(harness, command) == CATEGORY_USAGE

    assert len(category_names(harness.conn, "expense")) == 12
    assert len(category_names(harness.conn, "income")) == 3


async def test_category_from_another_user_gets_no_reply_and_adds_nothing(
    harness: Harness,
) -> None:
    assert await harness.send("/category add Rent", user_id=7) == []
    assert len(category_names(harness.conn, "expense")) == 12


ZERO_WIDTH_SPACE = "\u200b"


@pytest.mark.parametrize(
    "command",
    [
        f"/category add Rent{ZERO_WIDTH_SPACE}",
        f"/category add income Re{ZERO_WIDTH_SPACE}nt",
        f"/category add RENT{ZERO_WIDTH_SPACE}\u200f",
    ],
)
async def test_category_add_sees_through_invisible_characters_when_checking_for_a_duplicate(
    harness: Harness, command: str
) -> None:
    await harness.send("/category add Rent")

    assert await reply_to(harness, command) == "There is already a category Rent."

    assert len(category_names(harness.conn, "expense")) == 13
    assert len(category_names(harness.conn, "income")) == 3


async def test_category_add_stores_a_name_without_invisible_characters(
    harness: Harness,
) -> None:
    assert await reply_to(harness, f"/category add Pet{ZERO_WIDTH_SPACE} food") == (
        "Added expense category Pet food."
    )

    assert category_names(harness.conn, "expense")[-1] == "Pet food"


@pytest.mark.parametrize(
    "command",
    [
        f"/category add {ZERO_WIDTH_SPACE}",
        f"/category add income {ZERO_WIDTH_SPACE}\u200f",
        f"/category add \ufeff{ZERO_WIDTH_SPACE}",
    ],
)
async def test_category_add_with_only_invisible_characters_shows_the_usage(
    harness: Harness, command: str
) -> None:
    assert await reply_to(harness, command) == CATEGORY_ADD_USAGE

    assert len(category_names(harness.conn, "expense")) == 12
    assert len(category_names(harness.conn, "income")) == 3


async def test_category_rename_cleans_the_new_name_and_sees_through_it_for_a_duplicate(
    harness: Harness,
) -> None:
    assert await reply_to(harness, f"/category rename Eating out Groceries{ZERO_WIDTH_SPACE}") == (
        "There is already a category Groceries."
    )
    assert await reply_to(harness, f"/category rename Eating out Fo{ZERO_WIDTH_SPACE}od") == (
        "Renamed Eating out to Food."
    )
    assert category_names(harness.conn, "expense")[1] == "Food"
    assert await reply_to(harness, f"/category rename Food {ZERO_WIDTH_SPACE}") == (
        CATEGORY_RENAME_USAGE
    )


async def test_category_rename_cuts_a_long_unknown_name_in_the_reply(harness: Harness) -> None:
    assert await reply_to(harness, f"/category rename {'a' * 100} Food") == (
        f"No category named {'a' * 30}. See /category"
    )


async def file_under(harness: Harness, text: str, category_name: str) -> None:
    [first] = of(await harness.send(text), SendMessage)
    await harness.press(callback_data(first.reply_markup, category_name))


async def with_rent(harness: Harness) -> None:
    """A Rent category whose word "rent" files new entries under it."""
    add_category(harness.conn, "Rent", "expense")
    await file_under(harness, "1 rent", "Rent")
    await harness.send("/undo")


def budget_rows(harness: Harness) -> list[tuple[str, int]]:
    return [(b.category, b.limit_cents) for b in list_budgets(harness.conn, 2026, 11)]


async def test_budget_sets_a_limit_and_shows_the_month_so_far(harness: Harness) -> None:
    add_category(harness.conn, "Rent", "expense")

    assert await reply_to(harness, "/budget Rent 850.00") == (
        "Rent: 850.00 EUR a month. November: spent 0.00, left 850.00."
    )

    assert budget_rows(harness) == [("Rent", 85000)]


async def test_budget_matches_the_category_in_any_case_and_shows_it_as_stored(
    harness: Harness,
) -> None:
    assert await reply_to(harness, "/budget eating OUT 300,50") == (
        "Eating out: 300.50 EUR a month. November: spent 0.00, left 300.50."
    )


async def test_budget_again_replaces_the_limit(harness: Harness) -> None:
    await harness.send("/budget Housing 800")
    await harness.send("/budget Housing 900")

    assert budget_rows(harness) == [("Housing", 90000)]


async def test_budget_set_counts_what_is_already_spent_this_month(harness: Harness) -> None:
    await with_rent(harness)
    await harness.send("800 rent")

    assert await reply_to(harness, "/budget Rent 850.00") == (
        "Rent: 850.00 EUR a month. November: spent 800.00, left 50.00."
    )
    assert await reply_to(harness, "/budget Rent 700") == (
        "Rent: 700.00 EUR a month. November: spent 800.00, over by 100.00."
    )


async def test_budget_zero_removes_the_budget(harness: Harness) -> None:
    await harness.send("/budget Housing 800")
    await harness.send("/budget Eating out 300")

    assert await reply_to(harness, "/budget housing 0") == "Housing: budget removed."

    assert budget_rows(harness) == [("Eating out", 30000)]


@pytest.mark.parametrize("zero", ["0", "00", "0.0", "0,00"])
async def test_budget_any_spelling_of_zero_removes_it(harness: Harness, zero: str) -> None:
    await harness.send("/budget Housing 800")

    assert await reply_to(harness, f"/budget Housing {zero}") == "Housing: budget removed."

    assert budget_rows(harness) == []


async def test_budget_zero_without_a_budget_says_there_is_none(harness: Harness) -> None:
    assert await reply_to(harness, "/budget Housing 0") == "Housing has no budget."


@pytest.mark.parametrize("amount", ["1000", "0"])
async def test_budget_for_an_income_category_is_refused(harness: Harness, amount: str) -> None:
    assert await reply_to(harness, f"/budget salary {amount}") == (
        "Budgets are for expense categories."
    )

    assert budget_rows(harness) == []


async def test_budget_for_an_unknown_category_points_to_the_list(harness: Harness) -> None:
    assert await reply_to(harness, "/budget Rnt 850.00") == "No category named Rnt. See /category"
    assert await reply_to(harness, "/budget Rent 0") == "No category named Rent. See /category"
    assert await reply_to(harness, f"/budget {'a' * 100} 5") == (
        f"No category named {'a' * 30}. See /category"
    )

    assert budget_rows(harness) == []


@pytest.mark.parametrize(
    "command",
    [
        "/budget Housing",
        "/budget 850.00",
        "/budget Housing abc",
        "/budget Housing 12.345",
        "/budget Housing -5",
        "/budget Housing 100 usd",
        "/budget Housing 10000000.01",
        "/budget Housing 1,000.50",
    ],
)
async def test_budget_with_a_bad_shape_or_amount_shows_the_usage(
    harness: Harness, command: str
) -> None:
    assert await reply_to(harness, command) == BUDGET_USAGE

    assert budget_rows(harness) == []


async def test_budget_without_words_and_without_budgets_says_how_to_set_one(
    harness: Harness,
) -> None:
    assert await reply_to(harness, "/budget") == "No budgets yet. Set one: /budget Rent 850.00"


async def test_budget_without_words_lists_this_month_in_position_order(
    harness: Harness,
) -> None:
    await with_rent(harness)
    await file_under(harness, "320 pizza", "Eating out")
    await harness.send("800 rent")
    await harness.send("/budget Rent 850.00")
    await harness.send("/budget Eating out 300")

    assert await reply_to(harness, "/budget") == (
        "Budgets, November 2026:\n"
        "Eating out: 320.00 of 300.00 · over by 20.00\n"
        "Rent: 800.00 of 850.00 · 50.00 left"
    )


async def test_budget_list_shows_zero_left_at_the_limit(harness: Harness) -> None:
    await file_under(harness, "300 pizza", "Eating out")
    await harness.send("/budget Eating out 300")

    assert (await reply_to(harness, "/budget")).endswith("Eating out: 300.00 of 300.00 · 0.00 left")


async def test_budget_list_counts_only_the_current_month(harness: Harness) -> None:
    await file_under(harness, "300 pizza 31.10", "Eating out")
    await harness.send("/budget Eating out 300")

    assert (await reply_to(harness, "/budget")).endswith("Eating out: 0.00 of 300.00 · 300.00 left")


async def test_budget_from_another_user_gets_no_reply_and_sets_nothing(harness: Harness) -> None:
    assert await harness.send("/budget Housing 800", user_id=7) == []
    assert budget_rows(harness) == []


async def test_saved_reply_in_a_budgeted_category_ends_with_the_budget_line(
    harness: Harness,
) -> None:
    await with_rent(harness)
    await harness.send("/budget Rent 850.00")

    [request] = of(await harness.send("800 rent"), SendMessage)

    assert request.text == (
        "Saved 01.11: -800.00 EUR · rent → Rent\nRent: 800.00 of 850.00 in November · 50.00 left"
    )
    assert labels(request.reply_markup) == [["Change category", "Undo"]]


async def test_saved_reply_says_over_by_when_the_entry_passes_the_limit(harness: Harness) -> None:
    await with_rent(harness)
    await harness.send("/budget Rent 850.00")
    await harness.send("800 rent")

    [request] = of(await harness.send("100 rent"), SendMessage)

    assert request.text.endswith("Rent: 900.00 of 850.00 in November · over by 50.00")


async def test_saved_reply_for_a_back_dated_entry_uses_the_month_of_that_entry(
    harness: Harness,
) -> None:
    await with_rent(harness)
    await harness.send("/budget Rent 850.00")
    await harness.send("800 rent")

    [request] = of(await harness.send("100 rent 31.10"), SendMessage)

    assert request.text == (
        "Saved 31.10: -100.00 EUR · rent → Rent\nRent: 100.00 of 850.00 in October · 750.00 left"
    )


async def test_saved_reply_without_a_budget_is_unchanged(harness: Harness) -> None:
    await with_rent(harness)
    await harness.send("/budget Eating out 300")

    [request] = of(await harness.send("800 rent"), SendMessage)

    assert request.text == "Saved 01.11: -800.00 EUR · rent → Rent"


async def test_pending_entry_gets_no_budget_line(harness: Harness) -> None:
    await with_rent(harness)
    await harness.send("/budget Rent 850.00")

    [request] = of(await harness.send("800 usd rent"), SendMessage)

    assert "of 850.00" not in request.text
    assert request.text.splitlines()[-1].startswith("No USD rate yet.")


async def test_income_and_pot_moves_get_no_budget_line(harness: Harness) -> None:
    await harness.send("/budget Housing 800")

    [income] = of(await harness.send("+3000 salary"), SendMessage)
    [pot] = of(await harness.send("save 200 emergency"), SendMessage)

    assert "of 800.00" not in income.text
    assert pot.text == "Emergency pot 01.11: +200.00 EUR · total 200.00 EUR"


async def test_picking_a_budgeted_category_redraws_the_reply_with_the_budget_line(
    harness: Harness,
) -> None:
    await harness.send("/budget Eating out 300")
    [first] = of(await harness.send("100 pizza"), SendMessage)
    assert "of 300.00" not in first.text

    requests = await harness.press(callback_data(first.reply_markup, "Eating out"))

    [edit] = of(requests, EditMessageText)
    assert edit.text == (
        "Saved 01.11: -100.00 EUR · pizza → Eating out\n"
        "Eating out: 100.00 of 300.00 in November · 200.00 left"
    )
    assert labels(edit.reply_markup) == [["Change category", "Undo"]]
    assert len(of(requests, AnswerCallbackQuery)) == 1


async def test_picking_a_category_without_a_budget_leaves_no_budget_line(
    harness: Harness,
) -> None:
    await harness.send("/budget Eating out 300")
    [first] = of(await harness.send("100 pizza"), SendMessage)

    [edit] = of(
        await harness.press(callback_data(first.reply_markup, "Transport")), EditMessageText
    )

    assert edit.text == "Saved 01.11: -100.00 EUR · pizza → Transport"


async def test_changing_the_category_redraws_the_budget_line_for_the_new_category(
    harness: Harness,
) -> None:
    await with_rent(harness)
    await harness.send("/budget Rent 850.00")
    await harness.send("/budget Eating out 300")
    [saved] = of(await harness.send("100 rent"), SendMessage)
    [picker] = of(
        await harness.press(callback_data(saved.reply_markup, "Change category")),
        EditMessageReplyMarkup,
    )

    requests = await harness.press(callback_data(picker.reply_markup, "Eating out"))

    [edit] = of(requests, EditMessageText)
    assert edit.text == (
        "Saved 01.11: -100.00 EUR · rent → Eating out\n"
        "Eating out: 100.00 of 300.00 in November · 200.00 left"
    )
    assert len(of(requests, AnswerCallbackQuery)) == 1


async def test_picking_a_category_for_a_back_dated_entry_uses_the_month_of_that_entry(
    harness: Harness,
) -> None:
    await harness.send("/budget Eating out 300")
    await file_under(harness, "50 pizza", "Eating out")
    [first] = of(await harness.send("100 coffee 31.10"), SendMessage)

    [edit] = of(
        await harness.press(callback_data(first.reply_markup, "Eating out")), EditMessageText
    )

    assert edit.text == (
        "Saved 31.10: -100.00 EUR · coffee → Eating out\n"
        "Eating out: 100.00 of 300.00 in October · 200.00 left"
    )


async def test_month_report_lists_the_budgets_after_the_categories(harness: Harness) -> None:
    await with_rent(harness)
    await file_under(harness, "320 pizza", "Eating out")
    await harness.send("800 rent")
    await harness.send("/budget Rent 850.00")
    await harness.send("/budget Eating out 300")

    [month] = of(await harness.send("/month"), SendMessage)

    assert (
        "\n\nBudgets\n"
        "Eating out: 320.00 of 300.00 · over by 20.00\n"
        "Rent: 800.00 of 850.00 · 50.00 left\n\n"
        "Top expenses"
    ) in month.text


async def test_month_report_without_budgets_has_no_budgets_block(harness: Harness) -> None:
    await file_under(harness, "320 pizza", "Eating out")

    [month] = of(await harness.send("/month"), SendMessage)

    assert "Budgets" not in month.text


async def test_budget_works_on_a_database_upgraded_from_version_2(tmp_path: Path) -> None:
    path = tmp_path / "v2.db"
    _make_version_2_database(path)
    with closing(connect(path)) as conn:
        harness = Harness(conn)

        [reply] = of(await harness.send("/budget Eating out 300"), SendMessage)

    assert reply.text == "Eating out: 300.00 EUR a month. November: spent 0.00, left 300.00."


OCTOBER_ASK = "Delete all 2 expenses and incomes of October 2026? Savings stay."


async def clear_prompt(harness: Harness, command: str = "/clear") -> SendMessage:
    [prompt] = of(await harness.send(command), SendMessage)
    return prompt


async def seed_clearable_month(harness: Harness) -> list[int]:
    """Two November entries (one expense, one income) beside an October one and a pot."""
    await harness.send("9 coffee 31.10")
    await harness.send("10 coffee")
    await harness.send("+3000 salary")
    november = [r.id for r in all_records(harness.conn) if r.on == TODAY]
    await harness.send("save 200 emergency")
    await harness.send("take 50 emergency")
    return november


def deletion_stamps(conn: sqlite3.Connection) -> list[tuple[int, str | None]]:
    rows = conn.execute("SELECT id, deleted_at FROM entries ORDER BY id").fetchall()
    return [(row["id"], row["deleted_at"]) for row in rows]


async def test_clear_asks_before_deleting_the_current_month(harness: Harness) -> None:
    await seed_clearable_month(harness)
    before = all_records(harness.conn)

    prompt = await clear_prompt(harness)

    assert prompt.text == "Delete all 2 expenses and incomes of November 2026? Savings stay."
    assert labels(prompt.reply_markup) == [["Delete 2 entries", "Cancel"]]
    assert all_records(harness.conn) == before


async def test_clear_buttons_carry_action_month_count_and_last_id_within_64_bytes(
    harness: Harness,
) -> None:
    november = await seed_clearable_month(harness)

    prompt = await clear_prompt(harness)

    delete, cancel = (button.callback_data for button in buttons(prompt.reply_markup))
    assert delete is not None
    assert cancel is not None
    shown = {"year": 2026, "month": 11, "count": 2, "last_id": november[-1]}
    assert ClearCb.unpack(delete) == ClearCb(action="yes", **shown)
    assert ClearCb.unpack(cancel) == ClearCb(action="no", **shown)
    assert max(len(delete.encode()), len(cancel.encode())) <= 64
    biggest = ClearCb(action="yes", year=2026, month=11, count=999999, last_id=10**9)
    assert len(biggest.pack().encode()) <= 64


@pytest.mark.parametrize("command", ["/clear 10", "/clear 2026-10"])
async def test_clear_month_argument_selects_the_month(harness: Harness, command: str) -> None:
    await harness.send("9 coffee 31.10")
    await harness.send("8 tea 01.10")
    await harness.send("10 coffee")

    prompt = await clear_prompt(harness, command)

    assert prompt.text == OCTOBER_ASK
    assert labels(prompt.reply_markup) == [["Delete 2 entries", "Cancel"]]


async def test_clear_with_one_entry_uses_the_singular(harness: Harness) -> None:
    await harness.send("10 coffee")

    prompt = await clear_prompt(harness)

    assert prompt.text == "Delete all 1 expense or income of November 2026? Savings stay."
    assert labels(prompt.reply_markup) == [["Delete 1 entry", "Cancel"]]


async def test_clear_of_a_month_with_only_pot_moves_has_nothing_to_clear(
    harness: Harness,
) -> None:
    await harness.send("9 coffee 31.10")
    await harness.send("save 200 emergency")

    prompt = await clear_prompt(harness)

    assert prompt.text == "Nothing to clear in November 2026."
    assert prompt.reply_markup is None
    assert len(all_records(harness.conn)) == 2


async def test_clear_with_a_bad_month_shows_the_month_error(harness: Harness) -> None:
    await harness.send("10 coffee")

    prompt = await clear_prompt(harness, "/clear 13")

    assert prompt.text == "Use a month like /month 10 or /month 2026-10"
    assert prompt.reply_markup is None
    assert len(all_records(harness.conn)) == 1


async def test_confirm_soft_deletes_the_months_expenses_and_incomes_and_reports(
    harness: Harness,
) -> None:
    november = await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)

    requests = await harness.press(callback_data(prompt.reply_markup, "Delete 2 entries"))

    [edit] = of(requests, EditMessageText)
    assert edit.text == "Deleted 2 entries of November 2026. /undo will not bring them back."
    assert edit.reply_markup is None
    assert len(of(requests, AnswerCallbackQuery)) == 1
    assert all(is_soft_deleted(harness.conn, entry_id) for entry_id in november)
    rows = harness.conn.execute("SELECT id FROM entries").fetchall()
    assert set(november) <= {row["id"] for row in rows}


async def test_confirm_leaves_other_months_and_the_savings_pot_alone(harness: Harness) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)

    await harness.press(callback_data(prompt.reply_markup, "Delete 2 entries"))

    assert [(r.kind, r.on.isoformat()) for r in all_records(harness.conn)] == [
        ("expense", "2026-10-31"),
        ("save", "2026-11-01"),
        ("take", "2026-11-01"),
    ]
    [pot] = list_pots(harness.conn)
    assert pot.total_cents == 15000


async def test_cleared_expenses_drop_out_of_the_budget_and_the_month_report(
    harness: Harness,
) -> None:
    await file_under(harness, "320 pizza", "Eating out")
    await harness.send("/budget Eating out 300")
    prompt = await clear_prompt(harness)

    await harness.press(callback_data(prompt.reply_markup, "Delete 1 entry"))

    [budget] = list_budgets(harness.conn, 2026, 11)
    assert budget.spent_cents == 0
    [month] = of(await harness.send("/month"), SendMessage)
    assert month.text == "<pre>November 2026\n\nNo entries.</pre>"


async def test_cancel_deletes_nothing_and_removes_the_buttons(harness: Harness) -> None:
    await seed_clearable_month(harness)
    before = all_records(harness.conn)
    prompt = await clear_prompt(harness)

    requests = await harness.press(callback_data(prompt.reply_markup, "Cancel"))

    [edit] = of(requests, EditMessageText)
    assert edit.text == "Nothing deleted."
    assert edit.reply_markup is None
    assert len(of(requests, AnswerCallbackQuery)) == 1
    assert all_records(harness.conn) == before


async def test_confirm_refuses_when_entries_were_added_after_the_question(
    harness: Harness,
) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)
    await harness.send("5 tea")
    await harness.send("6 bus")
    before = all_records(harness.conn)

    requests = await harness.press(callback_data(prompt.reply_markup, "Delete 2 entries"))

    [edit] = of(requests, EditMessageText)
    assert edit.text == "November 2026 changed since you asked. Send /clear again."
    assert edit.reply_markup is None
    assert len(of(requests, AnswerCallbackQuery)) == 1
    assert all_records(harness.conn) == before


async def test_confirm_refuses_when_an_entry_was_removed_after_the_question(
    harness: Harness,
) -> None:
    await harness.send("10 coffee")
    await harness.send("5 tea")
    prompt = await clear_prompt(harness)
    await harness.send("/undo")
    before = all_records(harness.conn)

    requests = await harness.press(callback_data(prompt.reply_markup, "Delete 2 entries"))

    [edit] = of(requests, EditMessageText)
    assert edit.text == "November 2026 changed since you asked. Send /clear again."
    assert all_records(harness.conn) == before


async def test_second_press_after_the_delete_keeps_a_newer_entry(harness: Harness) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)
    confirm = callback_data(prompt.reply_markup, "Delete 2 entries")
    await harness.press(confirm)
    await harness.send("5 tea")
    kept = newest_id(harness.conn)

    requests = await harness.press(confirm)

    [edit] = of(requests, EditMessageText)
    assert edit.text == "November 2026 changed since you asked. Send /clear again."
    assert len(of(requests, AnswerCallbackQuery)) == 1
    assert not is_soft_deleted(harness.conn, kept)


async def test_second_press_keeps_new_entries_even_when_there_are_as_many_as_before(
    harness: Harness,
) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)
    confirm = callback_data(prompt.reply_markup, "Delete 2 entries")
    await harness.press(confirm)
    await harness.send("5 tea")
    await harness.send("6 bus")
    kept = [r.id for r in all_records(harness.conn) if r.kind == "expense" and r.on == TODAY]

    [edit] = of(await harness.press(confirm), EditMessageText)

    assert edit.text == "November 2026 changed since you asked. Send /clear again."
    assert len(kept) == 2
    assert not any(is_soft_deleted(harness.conn, entry_id) for entry_id in kept)


async def test_a_second_open_question_is_refused_after_the_first_was_used(
    harness: Harness,
) -> None:
    await harness.send("10 coffee")
    await harness.send("5 tea")
    first = await clear_prompt(harness)
    second = await clear_prompt(harness)
    await harness.press(callback_data(first.reply_markup, "Delete 2 entries"))
    await harness.send("7 bus")
    await harness.send("8 taxi")
    kept = [r.id for r in all_records(harness.conn)]

    [edit] = of(
        await harness.press(callback_data(second.reply_markup, "Delete 2 entries")),
        EditMessageText,
    )

    assert edit.text == "November 2026 changed since you asked. Send /clear again."
    assert len(kept) == 2
    assert not any(is_soft_deleted(harness.conn, entry_id) for entry_id in kept)


async def test_confirm_refuses_after_an_undo_and_a_new_entry_leave_the_same_count(
    harness: Harness,
) -> None:
    await harness.send("10 coffee")
    await harness.send("5 tea")
    prompt = await clear_prompt(harness)
    await harness.send("/undo")
    await harness.send("7 bus")
    before = all_records(harness.conn)

    [edit] = of(
        await harness.press(callback_data(prompt.reply_markup, "Delete 2 entries")),
        EditMessageText,
    )

    assert edit.text == "November 2026 changed since you asked. Send /clear again."
    assert len(before) == 2
    assert all_records(harness.conn) == before


async def test_second_press_with_nothing_new_deletes_nothing_and_asks_again(
    harness: Harness,
) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)
    confirm = callback_data(prompt.reply_markup, "Delete 2 entries")
    await harness.press(confirm)
    after_first = deletion_stamps(harness.conn)

    [edit] = of(await harness.press(confirm), EditMessageText)

    assert edit.text == "November 2026 changed since you asked. Send /clear again."
    assert deletion_stamps(harness.conn) == after_first


@pytest.mark.parametrize("label", ["Delete 2 entries", "Cancel"])
async def test_clear_buttons_ignore_message_not_modified(harness: Harness, label: str) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)
    harness.bot.add_result_for(EditMessageText, ok=False, error_code=400, description=NOT_MODIFIED)

    requests = await harness.press(callback_data(prompt.reply_markup, label))

    assert len(of(requests, EditMessageText)) == 1
    assert len(of(requests, AnswerCallbackQuery)) == 1


@pytest.mark.parametrize("label", ["Delete 2 entries", "Cancel"])
async def test_clear_buttons_answer_the_callback_when_the_edit_fails(
    harness: Harness, label: str
) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)
    harness.bot.add_result_for(
        EditMessageText, ok=False, error_code=400, description="Bad Request: boom"
    )

    with pytest.raises(TelegramBadRequest):
        await harness.press(callback_data(prompt.reply_markup, label))

    assert len(of(harness.bot.requests, AnswerCallbackQuery)) == 1


async def press_old_question(harness: Harness, data: str) -> list[TelegramMethod[Any]]:
    """Press a button on a message that Telegram no longer shows to the bot (older than 48 h)."""
    update = Update(
        update_id=2,
        callback_query=CallbackQuery(
            id="callback-1",
            from_user=User(id=OWNER_ID, is_bot=False, first_name="Misha"),
            chat_instance="1",
            data=data,
            message=InaccessibleMessage(chat=_chat(OWNER_ID, False), message_id=7),
        ),
    )
    harness.bot.requests.clear()
    await harness.dispatcher.feed_update(harness.bot, update)
    return list(harness.bot.requests)


async def test_confirm_on_a_message_that_is_too_old_deletes_nothing_and_says_so(
    harness: Harness,
) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)
    before = all_records(harness.conn)

    requests = await press_old_question(
        harness, callback_data(prompt.reply_markup, "Delete 2 entries")
    )

    [answer] = of(requests, AnswerCallbackQuery)
    assert answer.text == CLEAR_TOO_OLD == "This question is too old. Send /clear again."
    assert of(requests, EditMessageText) == []
    assert all_records(harness.conn) == before
    assert all(stamp is None for _, stamp in deletion_stamps(harness.conn))


async def test_cancel_on_a_message_that_is_too_old_is_answered_and_changes_nothing(
    harness: Harness,
) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)
    before = all_records(harness.conn)

    requests = await press_old_question(harness, callback_data(prompt.reply_markup, "Cancel"))

    assert len(of(requests, AnswerCallbackQuery)) == 1
    assert of(requests, EditMessageText) == []
    assert all_records(harness.conn) == before


@pytest.mark.parametrize(
    ("year", "month"), [(2026, 13), (2026, 0), (2026, -1), (0, 11), (10000, 11), (-2026, 11)]
)
async def test_forged_confirm_data_deletes_nothing_and_is_answered_quietly(
    harness: Harness, year: int, month: int
) -> None:
    await seed_clearable_month(harness)
    before = all_records(harness.conn)
    forged = ClearCb(action="yes", year=year, month=month, count=2, last_id=3).pack()

    requests = await harness.press(forged)

    [answer] = of(requests, AnswerCallbackQuery)
    assert answer.text is None
    assert of(requests, EditMessageText) == []
    assert all_records(harness.conn) == before


async def test_another_users_press_of_a_real_confirm_button_is_ignored(harness: Harness) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)
    before = all_records(harness.conn)

    requests = await harness.press(
        callback_data(prompt.reply_markup, "Delete 2 entries"), user_id=7
    )

    assert requests == []
    assert all_records(harness.conn) == before


async def test_saved_reply_budget_line_shows_the_new_name_after_a_category_rename(
    harness: Harness,
) -> None:
    await harness.send("/budget Eating out 300")
    await file_under(harness, "25 coffee", "Eating out")
    await harness.send("/category rename Eating out Food")

    [saved] = of(await harness.send("30 coffee"), SendMessage)

    assert saved.text == (
        "Saved 01.11: -30.00 EUR · coffee → Food\nFood: 55.00 of 300.00 in November · 245.00 left"
    )


async def test_old_buttons_of_a_cleared_entry_say_it_is_gone(harness: Harness) -> None:
    [saved] = of(await harness.send("10 coffee"), SendMessage)
    pick = callback_data(saved.reply_markup, "Transport")
    [filed] = of(await harness.press(pick), EditMessageText)
    change = callback_data(filed.reply_markup, "Change category")
    undo = callback_data(filed.reply_markup, "Undo")
    [listing] = of(await harness.send("/last"), SendMessage)
    open_ = callback_data(listing.reply_markup, "1. coffee -10.00 EUR")
    [view] = of(await harness.press(open_), EditMessageText)
    delete = callback_data(view.reply_markup, "Delete")
    prompt = await clear_prompt(harness)
    await harness.press(callback_data(prompt.reply_markup, "Delete 1 entry"))
    assert all_records(harness.conn) == []

    for data in (open_, change, delete, pick):
        requests = await harness.press(data)
        assert [a.text for a in of(requests, AnswerCallbackQuery)] == ["Already deleted."]
        assert of(requests, EditMessageText) == []
        assert of(requests, EditMessageReplyMarkup) == []
    requests = await harness.press(undo)
    assert [a.text for a in of(requests, AnswerCallbackQuery)] == ["Nothing to undo."]
    assert of(requests, EditMessageText) == []


async def test_export_after_clear_has_no_cleared_rows(harness: Harness) -> None:
    await seed_clearable_month(harness)
    prompt = await clear_prompt(harness)
    await harness.press(callback_data(prompt.reply_markup, "Delete 2 entries"))

    [export] = of(await harness.send("/export"), SendDocument)

    assert isinstance(export.document, BufferedInputFile)
    rows = csv.DictReader(io.StringIO(export.document.data.decode()))
    assert [(row["date"], row["type"], row["note"]) for row in rows] == [
        ("2026-10-31", "expense", "coffee"),
        ("2026-11-01", "save", ""),
        ("2026-11-01", "take", ""),
    ]


async def test_three_lines_are_three_entries_each_with_its_own_reply_and_keyboard(
    harness: Harness,
) -> None:
    requests = await harness.send("25 coffee\n30 taxi\n40 pizza")

    replies = of(requests, SendMessage)
    assert [r.text.split("\n")[0] for r in replies] == [
        "Saved 01.11: -25.00 EUR · coffee",
        "Saved 01.11: -30.00 EUR · taxi",
        "Saved 01.11: -40.00 EUR · pizza",
    ]
    records = all_records(harness.conn)
    assert [r.note for r in records] == ["coffee", "taxi", "pizza"]
    for reply, record in zip(replies, records, strict=True):
        [first, *_] = buttons(reply.reply_markup)
        assert first.callback_data is not None
        assert PickCb.unpack(first.callback_data).entry_id == record.id


async def test_the_comma_form_shows_the_budget_line_on_the_entry_that_has_one(
    harness: Harness,
) -> None:
    await with_rent(harness)
    await harness.send("/budget Rent 850.00")

    replies = of(await harness.send("800 rent, 30 taxi"), SendMessage)

    assert replies[0].text == (
        "Saved 01.11: -800.00 EUR · rent → Rent\nRent: 800.00 of 850.00 in November · 50.00 left"
    )
    assert labels(replies[0].reply_markup) == [["Change category", "Undo"]]
    assert "850.00" not in replies[1].text
    assert replies[1].text.startswith("Saved 01.11: -30.00 EUR · taxi")


async def test_two_entries_of_one_budgeted_category_show_the_spent_amount_growing(
    harness: Harness,
) -> None:
    await with_rent(harness)
    await harness.send("/budget Rent 850.00")

    first, second = of(await harness.send("100 rent\n50 rent"), SendMessage)

    assert first.text.endswith("Rent: 100.00 of 850.00 in November · 750.00 left")
    assert second.text.endswith("Rent: 150.00 of 850.00 in November · 700.00 left")


async def test_one_bad_part_gives_one_reply_and_saves_nothing(harness: Harness) -> None:
    requests = await harness.send("25 coffee\n1 200 taxi\n30 lunch")

    [reply] = of(requests, SendMessage)
    assert reply.text == (
        'Nothing saved. Entry 2 "1 200 taxi": Write 1200 without spaces, e.g. 1200 taxi'
    )
    assert all_records(harness.conn) == []


async def test_more_than_ten_entries_save_nothing(harness: Harness) -> None:
    requests = await harness.send("\n".join(f"{number} item" for number in range(1, 12)))

    [reply] = of(requests, SendMessage)
    assert reply.text == (
        "Up to 10 entries in one message. Nothing saved: send them in two messages."
    )
    assert all_records(harness.conn) == []


async def test_a_refused_take_in_the_middle_does_not_stop_the_other_entries(
    harness: Harness,
) -> None:
    await harness.send("save 200 emergency")

    replies = of(await harness.send("25 coffee\ntake 999 emergency\n30 taxi"), SendMessage)

    assert [r.text.split("\n")[0] for r in replies] == [
        "Saved 01.11: -25.00 EUR · coffee",
        "Entry 2 not saved: Emergency has 200.00 EUR, cannot take 999.00",
        "Saved 01.11: -30.00 EUR · taxi",
    ]
    assert replies[1].reply_markup is None
    assert [r.note for r in all_records(harness.conn) if r.kind == "expense"] == [
        "coffee",
        "taxi",
    ]
    [pot] = list_pots(harness.conn)
    assert pot.total_cents == 20000


async def test_pot_moves_in_one_message_answer_with_the_pot_text(harness: Harness) -> None:
    replies = of(await harness.send("save 200 emergency, take 50 emergency"), SendMessage)

    assert [r.text for r in replies] == [
        "Emergency pot 01.11: +200.00 EUR · total 200.00 EUR",
        "Emergency pot 01.11: -50.00 EUR · total 150.00 EUR",
    ]
    assert [r.reply_markup for r in replies] == [None, None]


async def test_undo_of_the_second_reply_removes_only_the_second_entry(harness: Harness) -> None:
    await with_rent(harness)
    first, second, third = of(await harness.send("10 rent\n20 rent\n30 rent"), SendMessage)
    first_id, second_id, third_id = (r.id for r in all_records(harness.conn))

    requests = await harness.press(callback_data(second.reply_markup, "Undo"))

    assert len(of(requests, AnswerCallbackQuery)) == 1
    assert not is_soft_deleted(harness.conn, first_id)
    assert is_soft_deleted(harness.conn, second_id)
    assert not is_soft_deleted(harness.conn, third_id)
    assert (
        callback_data(first.reply_markup, "Undo")
        == EntryCb(action="undo", entry_id=first_id).pack()
    )
    assert (
        callback_data(third.reply_markup, "Undo")
        == EntryCb(action="undo", entry_id=third_id).pack()
    )


async def test_every_entry_is_saved_even_when_the_first_reply_fails_to_send(
    harness: Harness,
) -> None:
    harness.bot.add_result_for(SendMessage, ok=False, error_code=400, description="Bad Request")

    with pytest.raises(TelegramBadRequest):
        await harness.send("25 coffee\n30 taxi\n40 pizza")

    assert [r.note for r in all_records(harness.conn)] == ["coffee", "taxi", "pizza"]


def flood_control_on_send(
    harness: Harness, monkeypatch: pytest.MonkeyPatch, *, nth: int, times: int
) -> list[float]:
    """Telegram answers 429 to the nth send (and to its retries, `times` in all)."""
    session = harness.bot.mocked_session
    real = session.make_request
    sleeps: list[float] = []
    sends = 0
    refused = 0

    async def make_request(
        bot: Any, method: TelegramMethod[Any], timeout: int | None = None
    ) -> Any:
        nonlocal sends, refused
        if isinstance(method, SendMessage):
            sends += 1
            if sends >= nth and refused < times:
                refused += 1
                raise TelegramRetryAfter(method, "Too Many Requests: retry after 3", 3)
        return await real(bot, method, timeout)

    async def sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr(session, "make_request", make_request)
    monkeypatch.setattr(asyncio, "sleep", sleep)
    return sleeps


async def test_a_reply_that_hits_flood_control_is_sent_again_after_the_wait(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    sleeps = flood_control_on_send(harness, monkeypatch, nth=2, times=1)

    replies = of(await harness.send("25 coffee\n30 taxi\n40 pizza"), SendMessage)

    assert [r.text.split("\n")[0] for r in replies] == [
        "Saved 01.11: -25.00 EUR · coffee",
        "Saved 01.11: -30.00 EUR · taxi",
        "Saved 01.11: -40.00 EUR · pizza",
    ]
    assert sleeps == [3]


async def test_a_second_flood_control_error_on_the_same_reply_is_raised(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    sleeps = flood_control_on_send(harness, monkeypatch, nth=2, times=2)

    with pytest.raises(TelegramRetryAfter):
        await harness.send("25 coffee\n30 taxi\n40 pizza")

    assert sleeps == [3]
    assert [r.note for r in all_records(harness.conn)] == ["coffee", "taxi", "pizza"]
