import asyncio
import base64
import json
import logging
import sqlite3
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from typing import Any

import pytest
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.methods import (
    AnswerCallbackQuery,
    EditMessageText,
    GetFile,
    SendMessage,
    TelegramMethod,
)
from aiogram.types import (
    CallbackQuery,
    Chat,
    Document,
    InaccessibleMessage,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    PhotoSize,
    Update,
    User,
)

from finbot.ai_memory import Memory
from finbot.assistant import KEY_MSG, UNAVAILABLE_MSG
from finbot.bot.ai_handlers import AiState
from finbot.bot.app import build_dispatcher
from finbot.bot.keyboards import DraftCb
from finbot.budgets import entry_budget
from finbot.drafts import get_draft
from finbot.ledger import Record, all_records
from finbot.texts import (
    AI_TOO_LONG,
    DRAFT_CANCEL_FAILED,
    DRAFT_CANCELLED,
    DRAFT_EARLIER_CLOSED,
    DRAFT_OTHER_OPEN,
    DRAFT_REPLACED,
    DRAFT_SAVE_FAILED,
    HELP,
    PHOTO_NEEDS_AI,
    PHOTO_UNREADABLE,
    help_text,
)
from tests.fake_anthropic import FakeAnthropic, api_error, text_reply, tool_reply
from tests.mocked_bot import MockedBot

OWNER_ID = 42
TODAY = date(2026, 11, 1)
NOW = datetime(2026, 11, 1, 9, 0, tzinfo=UTC)  # 10:00 in Vienna
LATE_EVENING = datetime(2026, 10, 31, 22, 59, tzinfo=UTC)  # 23:59 in Vienna on 31.10
PRIVATE = Chat(id=OWNER_ID, type="private")
JPEG = b"\xff\xd8\xff" + b"jpeg-data"
PNG = b"\x89PNG\r\n\x1a\n" + b"png-data"


def entry(
    amount: str = "25",
    category: str = "Eating out",
    note: str = "кофе с другом",
    on: str = "2026-10-31",
    kind: str = "expense",
) -> dict[str, Any]:
    return {
        "kind": kind,
        "amount": amount,
        "currency": "EUR",
        "category": category,
        "note": note,
        "date": on,
    }


def propose(*entries: dict[str, Any], replaces: bool = False) -> dict[str, Any]:
    return {"entries": list(entries), "replaces_open_draft": replaces}


def text_update(text: str, *, when: datetime = NOW) -> Update:
    return Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=when,
            chat=PRIVATE,
            from_user=User(id=OWNER_ID, is_bot=False, first_name="Misha"),
            text=text,
        ),
    )


def photo_update(file_id: str, *, caption: str | None = None) -> Update:
    sizes = [
        PhotoSize(file_id="small", file_unique_id="s", width=90, height=90),
        PhotoSize(file_id=file_id, file_unique_id="big", width=800, height=600),
    ]
    return Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=NOW,
            chat=PRIVATE,
            from_user=User(id=OWNER_ID, is_bot=False, first_name="Misha"),
            photo=sizes,
            caption=caption,
        ),
    )


def document_update(file_id: str, *, mime: str, size: int) -> Update:
    document = Document(file_id=file_id, file_unique_id="d", mime_type=mime, file_size=size)
    return Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=NOW,
            chat=PRIVATE,
            from_user=User(id=OWNER_ID, is_bot=False, first_name="Misha"),
            document=document,
        ),
    )


def callback_update(data: str, *, inaccessible: bool = False, chat_id: int = OWNER_ID) -> Update:
    chat = Chat(id=chat_id, type="private")
    message: Message | InaccessibleMessage
    if inaccessible:
        message = InaccessibleMessage(chat=chat, message_id=7)
    else:
        message = Message(message_id=7, date=NOW, chat=chat, text="draft")
    return Update(
        update_id=2,
        callback_query=CallbackQuery(
            id="callback-1",
            from_user=User(id=OWNER_ID, is_bot=False, first_name="Misha"),
            chat_instance="1",
            data=data,
            message=message,
        ),
    )


class Harness:
    def __init__(self, conn: Any, fake: FakeAnthropic | None = None) -> None:
        self.conn = conn
        self.fake = fake
        self.bot = MockedBot()
        self.ai = None if fake is None else AiState(client=fake.client)
        self.dispatcher = build_dispatcher(conn, OWNER_ID, lambda: TODAY, ai=self.ai)

    def memory(self) -> Memory:
        assert self.ai is not None
        return self.ai.memory

    async def run(self, *updates: Update) -> list[TelegramMethod[Any]]:
        self.bot.requests.clear()
        await asyncio.gather(*(self.dispatcher.feed_update(self.bot, u) for u in updates))
        return list(self.bot.requests)

    async def send(self, text: str) -> list[TelegramMethod[Any]]:
        return await self.run(text_update(text))

    async def press(self, data: str) -> list[TelegramMethod[Any]]:
        return await self.run(callback_update(data))


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


def draft_request(requests: list[TelegramMethod[Any]]) -> SendMessage:
    [request] = of(requests, SendMessage)
    return request


async def draft_with(harness: Harness, text: str = "вчера 25 на кофе с другом") -> SendMessage:
    return draft_request(await harness.send(text))


def age_draft(conn: Any, draft_id: int, hours: int) -> None:
    created = datetime.now(UTC) - timedelta(hours=hours)
    conn.execute("UPDATE drafts SET created_at = ? WHERE id = ?", (created.isoformat(), draft_id))
    conn.commit()


@pytest.fixture
def conn(tmp_path: Any) -> Any:
    from finbot.db import connect

    c = connect(tmp_path / "t.db")
    yield c
    c.close()


@pytest.mark.parametrize("command", ["/start", "/help"])
async def test_ai_off_help_has_no_ai_lines(conn: Any, command: str) -> None:
    harness = Harness(conn)

    [request] = of(await harness.send(command), SendMessage)

    assert request.text == HELP


async def test_ai_off_free_text_asks_for_an_amount(conn: Any) -> None:
    harness = Harness(conn)

    [request] = of(await harness.send("coffee with a friend yesterday"), SendMessage)

    assert request.text == "Start with the amount, e.g. 25 coffee"
    assert all_records(conn) == []


async def test_ai_off_photo_needs_the_ai(conn: Any) -> None:
    harness = Harness(conn)
    harness.bot.add_file("photo-1", JPEG)

    [request] = of(await harness.run(photo_update("photo-1")), SendMessage)

    assert request.text == PHOTO_NEEDS_AI


async def test_ai_off_amount_text_is_saved_as_today(conn: Any) -> None:
    harness = Harness(conn)

    [request] = of(await harness.send("25 coffee"), SendMessage)

    assert request.text.startswith("Saved 01.11: -25.00 EUR · coffee")
    assert len(all_records(conn)) == 1


async def test_ai_on_help_has_the_ai_lines(conn: Any) -> None:
    harness = Harness(conn, FakeAnthropic())

    [request] = of(await harness.send("/help"), SendMessage)

    assert request.text == help_text(True)


async def test_ai_on_amount_text_is_saved_by_the_parser_without_a_request(conn: Any) -> None:
    fake = FakeAnthropic()
    harness = Harness(conn, fake)

    [request] = of(await harness.send("25 coffee"), SendMessage)

    assert request.text.startswith("Saved 01.11: -25.00 EUR · coffee")
    assert fake.requests == []
    assert len(all_records(conn)) == 1


async def test_ai_on_free_text_becomes_a_draft_with_save_and_cancel(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)

    request = await draft_with(harness)

    assert len(fake.requests) == 1
    assert request.text == "Draft:\n1. -25.00 EUR · Eating out · кофе с другом · 31.10.2026"
    assert labels(request.reply_markup) == [["Save", "Cancel"]]
    draft = get_draft(conn, 1)
    assert draft is not None
    assert draft.status == "open"
    assert draft.message_id == 100
    assert all_records(conn) == []


async def test_save_writes_the_entry_and_edits_the_draft(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)

    requests = await harness.press(callback_data(draft.reply_markup, "Save"))

    [answer] = of(requests, AnswerCallbackQuery)
    assert answer.text is None
    [saved] = of(requests, SendMessage)
    assert saved.text == "Saved 31.10: -25.00 EUR · кофе с другом → Eating out"
    assert labels(saved.reply_markup) == [["Change category", "Undo"]]
    [edit] = of(requests, EditMessageText)
    assert edit.text == "Saved."
    assert edit.reply_markup is None
    [record] = all_records(conn)
    assert record.category == "Eating out"
    assert record.keyword == ""


async def test_save_reply_shows_the_budget_line_when_a_budget_exists(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    await harness.send("/budget Eating out 200")
    draft = await draft_with(harness)

    [saved] = of(await harness.press(callback_data(draft.reply_markup, "Save")), SendMessage)

    assert saved.text == (
        "Saved 31.10: -25.00 EUR · кофе с другом → Eating out\n"
        "Eating out: 25.00 of 200.00 in October · 175.00 left"
    )


async def test_three_entry_draft_saves_three_entries(conn: Any) -> None:
    fake = FakeAnthropic(
        tool_reply(
            (
                "tu_1",
                "propose_entries",
                propose(
                    entry(amount="25", note="coffee"),
                    entry(amount="10", note="tea"),
                    entry(amount="7", note="bun"),
                ),
            )
        )
    )
    harness = Harness(conn, fake)
    draft = await draft_with(harness, "coffee 25, tea 10, bun 7 yesterday")
    assert labels(draft.reply_markup) == [["Save 3 entries", "Cancel"]]

    requests = await harness.press(callback_data(draft.reply_markup, "Save 3 entries"))

    assert len(of(requests, SendMessage)) == 3
    [edit] = of(requests, EditMessageText)
    assert edit.text == "Saved 3 entries."
    assert len(all_records(conn)) == 3


async def test_entry_without_category_asks_for_one(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry(category="")))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)

    [saved] = of(await harness.press(callback_data(draft.reply_markup, "Save")), SendMessage)

    assert saved.text == "Saved 31.10: -25.00 EUR · кофе с другом\nPick a category:"
    assert len(buttons(saved.reply_markup)) == 12


async def test_cancel_then_save_says_already_cancelled(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)

    requests = await harness.press(callback_data(draft.reply_markup, "Cancel"))

    [edit] = of(requests, EditMessageText)
    assert edit.text == DRAFT_CANCELLED
    assert edit.reply_markup is None
    assert [a.text for a in of(requests, AnswerCallbackQuery)] == [None]
    [late] = of(await harness.press(callback_data(draft.reply_markup, "Save")), AnswerCallbackQuery)
    assert late.text == "Already cancelled."
    assert all_records(conn) == []


async def test_save_twice_in_a_row_says_already_saved(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)
    save = callback_data(draft.reply_markup, "Save")
    await harness.press(save)

    [again] = of(await harness.press(save), AnswerCallbackQuery)

    assert again.text == "Already saved."
    assert len(all_records(conn)) == 1


async def test_two_saves_at_once_write_one_set_of_entries(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)
    save = callback_data(draft.reply_markup, "Save")

    requests = await harness.run(callback_update(save), callback_update(save))

    answers = sorted(a.text or "" for a in of(requests, AnswerCallbackQuery))
    assert answers == ["", "Already saved."]
    assert len(all_records(conn)) == 1


async def test_draft_older_than_48_hours_expires(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)
    age_draft(conn, 1, hours=49)

    [answer] = of(
        await harness.press(callback_data(draft.reply_markup, "Save")), AnswerCallbackQuery
    )

    assert answer.text == "This draft is too old. Nothing saved. Send it again."
    stored = get_draft(conn, 1)
    assert stored is not None
    assert stored.status == "expired"
    assert all_records(conn) == []


async def test_unknown_draft_id_says_gone(conn: Any) -> None:
    harness = Harness(conn, FakeAnthropic())

    [answer] = of(
        await harness.press(DraftCb(action="s", draft_id=999).pack()), AnswerCallbackQuery
    )

    assert answer.text == "This draft is gone."


async def test_save_on_inaccessible_message_still_saves(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)

    requests = await harness.run(
        callback_update(callback_data(draft.reply_markup, "Save"), inaccessible=True)
    )

    assert len(of(requests, AnswerCallbackQuery)) == 1
    assert len(all_records(conn)) == 1


async def test_corrected_draft_replaces_the_open_one(conn: Any) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", propose(entry()))),
        tool_reply(("tu_2", "propose_entries", propose(entry(amount="30"), replaces=True))),
    )
    harness = Harness(conn, fake)
    first = await draft_with(harness)
    old_save = callback_data(first.reply_markup, "Save")

    requests = await harness.send("no, 30 instead")

    [replaced] = of(requests, EditMessageText)
    assert replaced.text == DRAFT_REPLACED
    assert replaced.reply_markup is None
    assert len(of(requests, SendMessage)) == 1
    old = get_draft(conn, 1)
    assert old is not None
    assert old.status == "replaced"
    [late] = of(await harness.press(old_save), AnswerCallbackQuery)
    assert late.text == "Replaced by a newer draft."
    assert len(fake.requests) == 2
    history = harness.memory().history(datetime.now(UTC))
    assert any("[draft replaced]" in str(item["content"]) for item in history)
    [new_draft] = of(requests, SendMessage)
    assert new_draft.text == "Draft:\n1. -30.00 EUR · Eating out · кофе с другом · 31.10.2026"


async def test_question_is_answered_from_the_tools_with_no_parse_mode(conn: Any) -> None:
    fake = FakeAnthropic(
        tool_reply(
            ("tu_1", "list_entries", {"start": "2026-11-01", "end": "2026-11-30"}),
        ),
        text_reply("You spent 0.00 EUR on eating out."),
    )
    harness = Harness(conn, fake)

    [request] = of(
        await harness.send("how much did I spend on eating out this month?"), SendMessage
    )

    assert request.text == "You spent 0.00 EUR on eating out."
    assert not isinstance(request.parse_mode, str)
    assert len(fake.requests) == 2
    roles = [item["role"] for item in harness.memory().history(datetime.now(UTC))]
    assert roles == ["user", "assistant"]


async def test_text_over_1000_characters_is_refused_without_a_request(conn: Any) -> None:
    fake = FakeAnthropic()
    harness = Harness(conn, fake)

    [request] = of(await harness.send("a" * 1001), SendMessage)

    assert request.text == AI_TOO_LONG
    assert fake.requests == []


async def test_rejected_key_says_so_and_remembers_nothing(conn: Any) -> None:
    fake = FakeAnthropic(api_error(401, "invalid x-api-key", "authentication_error"))
    harness = Harness(conn, fake)

    [request] = of(await harness.send("how much on coffee?"), SendMessage)

    assert request.text == KEY_MSG
    assert len(fake.requests) == 1
    assert harness.memory().history(datetime.now(UTC)) == []


async def test_jpeg_photo_is_sent_as_an_image_block_with_the_caption(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry(note="lunch")))))
    harness = Harness(conn, fake)
    harness.bot.add_file("photo-1", JPEG)

    requests = await harness.run(photo_update("photo-1", caption="lunch"))

    assert len(fake.requests) == 1
    content = fake.requests[0]["messages"][-1]["content"]
    assert content[0] == {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": base64.b64encode(JPEG).decode(),
        },
    }
    assert content[1] == {"type": "text", "text": "[receipt photo] lunch"}
    assert "bot42:TEST" not in json.dumps(fake.requests[0])
    assert len(of(requests, SendMessage)) == 1


async def test_png_sent_as_a_document_is_an_image_block(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    harness.bot.add_file("doc-1", PNG)

    await harness.run(document_update("doc-1", mime="image/png", size=len(PNG)))

    content = fake.requests[0]["messages"][-1]["content"]
    assert content[0]["source"]["media_type"] == "image/png"
    assert content[1] == {"type": "text", "text": "[receipt photo]"}


async def test_bytes_that_are_no_image_are_unreadable(conn: Any) -> None:
    fake = FakeAnthropic()
    harness = Harness(conn, fake)
    harness.bot.add_file("photo-1", b"hello")

    [request] = of(await harness.run(photo_update("photo-1")), SendMessage)

    assert request.text == PHOTO_UNREADABLE
    assert fake.requests == []


async def test_failed_download_is_unreadable(conn: Any) -> None:
    fake = FakeAnthropic()
    harness = Harness(conn, fake)
    harness.bot.add_result_for(
        GetFile, ok=False, error_code=400, description="Bad Request: file is too big"
    )

    [request] = of(await harness.run(photo_update("photo-1")), SendMessage)

    assert request.text == PHOTO_UNREADABLE
    assert fake.requests == []


async def test_image_document_over_5_mb_gets_no_reply(conn: Any) -> None:
    fake = FakeAnthropic()
    harness = Harness(conn, fake)

    requests = await harness.run(document_update("doc-1", mime="image/jpeg", size=6 * 1024 * 1024))

    assert requests == []
    assert fake.requests == []


async def test_two_texts_at_once_run_one_after_another(conn: Any) -> None:
    fake = FakeAnthropic(text_reply("First answer"), text_reply("Second answer"))
    harness = Harness(conn, fake)

    await harness.run(
        text_update("how much on coffee?"),
        Update(
            update_id=3,
            message=Message(
                message_id=3,
                date=NOW,
                chat=PRIVATE,
                from_user=User(id=OWNER_ID, is_bot=False, first_name="Misha"),
                text="how much on taxi?",
            ),
        ),
    )

    first, second = fake.requests
    assert len(first["messages"]) == 1
    assert len(second["messages"]) == 3
    first_text = first["messages"][0]["content"][0]["text"]
    assert second["messages"][0] == {"role": "user", "content": first_text}
    assert second["messages"][1]["content"] == "First answer"
    roles = [item["role"] for item in harness.memory().history(datetime.now(UTC))]
    assert roles == ["user", "assistant", "user", "assistant"]


async def test_late_message_is_dated_in_vienna(conn: Any) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", propose(entry(on="2026-11-01")))),
        text_reply("Which day?"),
    )
    harness = Harness(conn, fake)

    await harness.run(text_update("shoes 25 yesterday", when=LATE_EVENING))

    assert len(fake.requests) == 2
    assert "Saturday 2026-10-31" in fake.requests[0]["system"]
    [result] = fake.requests[1]["messages"][-1]["content"]
    assert result["content"] == "entry 1: 2026-11-01 is after the message date"
    assert result["is_error"] is True


async def test_unexpected_error_in_a_turn_replies_and_logs_the_class_only(
    conn: Any, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def broken(*_args: Any, **_kwargs: Any) -> str:
        raise RuntimeError("boom with secret words")

    monkeypatch.setattr("finbot.bot.ai_handlers.build_system_prompt", broken)
    fake = FakeAnthropic()
    harness = Harness(conn, fake)
    caplog.set_level(logging.DEBUG)

    [request] = of(await harness.send("how much on coffee?"), SendMessage)

    assert request.text == UNAVAILABLE_MSG
    assert fake.requests == []
    records = [r for r in caplog.records if r.name == "finbot.ai"]
    assert [r.getMessage() for r in records] == ["ai turn failed: RuntimeError"]
    assert records[0].levelno == logging.ERROR


FAILURES: dict[str, Callable[[TelegramMethod[Any]], Exception]] = {
    "429": lambda m: TelegramRetryAfter(m, "Too Many Requests: retry after 0", 0),
    "400": lambda m: TelegramBadRequest(m, "Bad Request: chat not found"),
    "not modified": lambda m: TelegramBadRequest(m, "Bad Request: message is not modified"),
    "too old": lambda m: TelegramBadRequest(
        m, "Bad Request: query is too old and response timeout expired or query ID is invalid"
    ),
}


def script(
    harness: Harness,
    monkeypatch: pytest.MonkeyPatch,
    method_class: type[TelegramMethod[Any]],
    outcomes: list[str | None],
) -> None:
    """The next calls of method_class fail as named in FAILURES, or go through (None)."""
    session = harness.bot.mocked_session
    real = session.make_request
    queue = list(outcomes)

    async def make_request(
        bot: Any, method: TelegramMethod[Any], timeout: int | None = None
    ) -> Any:
        if isinstance(method, method_class) and queue:
            failure = queue.pop(0)
            if failure is not None:
                session.requests.append(method)
                raise FAILURES[failure](method)
        return await real(bot, method, timeout)

    monkeypatch.setattr(session, "make_request", make_request)


async def test_sqlite_error_on_save_says_could_not_save(
    conn: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)

    def broken(*_args: Any, **_kwargs: Any) -> None:
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr("finbot.bot.ai_handlers.save_draft", broken)
    [answer] = of(
        await harness.press(callback_data(draft.reply_markup, "Save")), AnswerCallbackQuery
    )

    assert answer.text == DRAFT_SAVE_FAILED
    assert all_records(conn) == []
    stored = get_draft(conn, 1)
    assert stored is not None
    assert stored.status == "open"


async def test_save_and_cancel_are_remembered(conn: Any) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", propose(entry()))),
        tool_reply(("tu_2", "propose_entries", propose(entry(amount="9", note="tea")))),
    )
    harness = Harness(conn, fake)
    saved = await draft_with(harness)
    cancelled = await draft_with(harness, "вчера 9 чай")

    await harness.press(callback_data(saved.reply_markup, "Save"))
    await harness.press(callback_data(cancelled.reply_markup, "Cancel"))

    texts = [str(item["content"]) for item in harness.memory().history(datetime.now(UTC))]
    assert any("[draft saved]" in text for text in texts)
    assert any("[draft cancelled]" in text for text in texts)


async def test_flood_control_on_a_saved_reply_is_retried_and_all_replies_go_out(
    conn: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = FakeAnthropic(
        tool_reply(
            (
                "tu_1",
                "propose_entries",
                propose(
                    entry(amount="25", note="coffee"),
                    entry(amount="10", note="tea"),
                    entry(amount="7", note="bun"),
                ),
            )
        )
    )
    harness = Harness(conn, fake)
    draft = await draft_with(harness, "coffee 25, tea 10, bun 7 yesterday")
    script(harness, monkeypatch, SendMessage, [None, "429"])

    requests = await harness.press(callback_data(draft.reply_markup, "Save 3 entries"))

    texts = [r.text for r in of(requests, SendMessage)]
    assert len(texts) == 4
    assert len(set(texts)) == 3
    assert [e.text for e in of(requests, EditMessageText)] == ["Saved 3 entries."]
    assert len(all_records(conn)) == 3


async def test_failed_reply_is_skipped_and_the_rest_still_go_out(
    conn: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = FakeAnthropic(
        tool_reply(
            (
                "tu_1",
                "propose_entries",
                propose(
                    entry(amount="25", note="coffee"),
                    entry(amount="10", note="tea"),
                    entry(amount="7", note="bun"),
                ),
            )
        )
    )
    harness = Harness(conn, fake)
    draft = await draft_with(harness, "coffee 25, tea 10, bun 7 yesterday")
    script(harness, monkeypatch, SendMessage, [None, "400"])

    requests = await harness.press(callback_data(draft.reply_markup, "Save 3 entries"))

    texts = [r.text for r in of(requests, SendMessage)]
    assert len(texts) == 3
    assert "Saved 3 entries." in [e.text for e in of(requests, EditMessageText)]
    assert len(all_records(conn)) == 3


async def test_edit_not_modified_still_remembers_and_answers_once(
    conn: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)
    script(harness, monkeypatch, EditMessageText, ["not modified"])

    requests = await harness.press(callback_data(draft.reply_markup, "Save"))

    assert len(of(requests, AnswerCallbackQuery)) == 1
    assert len(all_records(conn)) == 1
    texts = [str(item["content"]) for item in harness.memory().history(datetime.now(UTC))]
    assert any("[draft saved]" in text for text in texts)


async def test_draft_that_cannot_be_sent_is_cancelled_and_replied_unavailable(
    conn: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    script(harness, monkeypatch, SendMessage, ["400"])

    requests = await harness.send("вчера 25 на кофе с другом")

    texts = [r.text for r in of(requests, SendMessage)]
    assert texts == [
        "Draft:\n1. -25.00 EUR · Eating out · кофе с другом · 31.10.2026",
        UNAVAILABLE_MSG,
    ]
    stored = get_draft(conn, 1)
    assert stored is not None
    assert stored.status == "cancelled"
    assert len(fake.requests) == 1


async def test_draft_send_flood_control_is_retried(
    conn: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    script(harness, monkeypatch, SendMessage, ["429"])

    requests = await harness.send("вчера 25 на кофе с другом")
    draft = of(requests, SendMessage)[-1]

    assert len(of(requests, SendMessage)) == 2
    assert labels(draft.reply_markup) == [["Save", "Cancel"]]
    stored = get_draft(conn, 1)
    assert stored is not None
    assert stored.status == "open"
    assert stored.message_id is not None


async def test_failed_catch_all_reply_raises_nothing(
    conn: Any, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def broken(*_args: Any, **_kwargs: Any) -> str:
        raise RuntimeError("boom")

    monkeypatch.setattr("finbot.bot.ai_handlers.build_system_prompt", broken)
    fake = FakeAnthropic()
    harness = Harness(conn, fake)
    script(harness, monkeypatch, SendMessage, ["400"])
    caplog.set_level(logging.DEBUG)

    requests = await harness.send("how much on coffee?")

    assert len(of(requests, SendMessage)) == 1
    assert fake.requests == []
    messages = [r.getMessage() for r in caplog.records if r.name == "finbot.ai"]
    assert "ai failure reply failed: TelegramBadRequest" in messages


async def test_two_photos_at_once_are_answered_in_arrival_order(conn: Any) -> None:
    fake = FakeAnthropic(text_reply("First answer"), text_reply("Second answer"))
    harness = Harness(conn, fake)
    harness.bot.add_file("photo-1", JPEG)
    harness.bot.add_file("photo-2", PNG)

    await harness.run(
        photo_update("photo-1", caption="first"), photo_update("photo-2", caption="second")
    )

    first, second = fake.requests
    assert first["messages"][-1]["content"][1]["text"] == "[receipt photo] first"
    assert second["messages"][0] == {"role": "user", "content": "[receipt photo] first"}
    assert second["messages"][1]["content"] == "First answer"
    assert second["messages"][2]["content"][1]["text"] == "[receipt photo] second"
    roles = [item["role"] for item in harness.memory().history(datetime.now(UTC))]
    assert roles == ["user", "assistant", "user", "assistant"]


async def test_save_from_an_inaccessible_message_replies_to_its_chat(conn: Any) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)

    requests = await harness.run(
        callback_update(callback_data(draft.reply_markup, "Save"), inaccessible=True, chat_id=777)
    )

    [saved] = of(requests, SendMessage)
    assert saved.chat_id == 777


async def test_missing_file_is_unreadable_and_logged(
    conn: Any, caplog: pytest.LogCaptureFixture
) -> None:
    fake = FakeAnthropic()
    harness = Harness(conn, fake)
    caplog.set_level(logging.DEBUG)

    [request] = of(await harness.run(photo_update("photo-404")), SendMessage)

    assert request.text == PHOTO_UNREADABLE
    assert fake.requests == []
    messages = [r.getMessage() for r in caplog.records if r.name == "finbot.ai"]
    assert any(m.startswith("photo download failed: ") for m in messages)


async def test_ai_on_slash_command_never_reaches_the_model(conn: Any) -> None:
    fake = FakeAnthropic()
    harness = Harness(conn, fake)

    [request] = of(await harness.send("/mnth"), SendMessage)

    assert request.text == "Start with the amount, e.g. 25 coffee"
    assert fake.requests == []


async def test_correction_with_two_open_text_drafts_replaces_nothing(conn: Any) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", propose(entry()))),
        tool_reply(("tu_2", "propose_entries", propose(entry(amount="12")))),
        tool_reply(("tu_3", "propose_entries", propose(entry(amount="30"), replaces=True))),
    )
    harness = Harness(conn, fake)
    await draft_with(harness)
    await draft_with(harness, "кофе и вода 12")

    request = await draft_with(harness, "no, 30 instead")

    assert request.text == (
        "Draft:\n1. -30.00 EUR · Eating out · кофе с другом · 31.10.2026\n"
        "Another draft is still open above. Cancel the one you do not want."
    )
    assert DRAFT_OTHER_OPEN in request.text
    for draft_id in (1, 2):
        older = get_draft(conn, draft_id)
        assert older is not None
        assert older.status == "open"


async def test_correction_with_an_open_photo_draft_replaces_nothing(conn: Any) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", propose(entry()))),
        tool_reply(("tu_2", "propose_entries", propose(entry(amount="30"), replaces=True))),
    )
    harness = Harness(conn, fake)
    harness.bot.add_file("photo-1", JPEG)
    await harness.run(photo_update("photo-1"))

    request = await draft_with(harness, "no, 30 instead")

    assert request.text.endswith(DRAFT_OTHER_OPEN)
    photo = get_draft(conn, 1)
    assert photo is not None
    assert photo.status == "open"


async def test_correction_after_the_earlier_draft_was_saved_says_it_is_closed(conn: Any) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", propose(entry()))),
        tool_reply(("tu_2", "propose_entries", propose(entry(amount="30"), replaces=True))),
    )
    harness = Harness(conn, fake)
    first = await draft_with(harness)
    await harness.press(callback_data(first.reply_markup, "Save"))

    request = await draft_with(harness, "no, 30 instead")

    assert request.text.endswith(DRAFT_EARLIER_CLOSED)
    saved = get_draft(conn, 1)
    assert saved is not None
    assert saved.status == "saved"


async def test_correction_after_48_hours_does_not_count_the_old_draft(conn: Any) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", propose(entry()))),
        tool_reply(("tu_2", "propose_entries", propose(entry(amount="30"), replaces=True))),
    )
    harness = Harness(conn, fake)
    await draft_with(harness)
    age_draft(conn, 1, 49)

    request = await draft_with(harness, "no, 30 instead")

    assert request.text.endswith(DRAFT_EARLIER_CLOSED)
    old = get_draft(conn, 1)
    assert old is not None
    assert old.status == "open"


async def test_new_draft_without_a_correction_has_no_extra_line(conn: Any) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", propose(entry()))),
        tool_reply(("tu_2", "propose_entries", propose(entry(amount="12")))),
    )
    harness = Harness(conn, fake)
    await draft_with(harness)

    request = await draft_with(harness, "кофе и вода 12")

    assert request.text == "Draft:\n1. -12.00 EUR · Eating out · кофе с другом · 31.10.2026"


async def test_answer_failure_after_save_still_saves_replies_and_edits(
    conn: Any, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    fake = FakeAnthropic(
        tool_reply(
            (
                "tu_1",
                "propose_entries",
                propose(
                    entry(amount="25", note="coffee"), entry(amount="10", note="tea", category="")
                ),
            )
        )
    )
    harness = Harness(conn, fake)
    draft = await draft_with(harness, "coffee 25, tea 10 yesterday")
    script(harness, monkeypatch, AnswerCallbackQuery, ["too old"])
    caplog.set_level(logging.DEBUG)

    requests = await harness.press(callback_data(draft.reply_markup, "Save 2 entries"))

    assert len(all_records(conn)) == 2
    saved = of(requests, SendMessage)
    assert [r.text for r in saved][0] == "Saved 31.10: -25.00 EUR · coffee → Eating out"
    assert len(buttons(saved[1].reply_markup)) == 12
    assert [e.text for e in of(requests, EditMessageText)] == ["Saved 2 entries."]
    texts = [str(item["content"]) for item in harness.memory().history(datetime.now(UTC))]
    assert any("[draft saved]" in text for text in texts)
    messages = [r.getMessage() for r in caplog.records if r.name == "finbot.ai"]
    assert messages == ["callback answer failed: TelegramBadRequest"]


async def test_budget_read_failure_on_one_entry_still_sends_every_reply(
    conn: Any, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    fake = FakeAnthropic(
        tool_reply(
            (
                "tu_1",
                "propose_entries",
                propose(
                    entry(amount="25", note="coffee"),
                    entry(amount="10", note="tea"),
                    entry(amount="7", note="bun"),
                ),
            )
        )
    )
    harness = Harness(conn, fake)
    draft = await draft_with(harness, "coffee 25, tea 10, bun 7 yesterday")
    reads: list[int] = []

    def flaky_budget(db: sqlite3.Connection, record: Record) -> Any:
        reads.append(record.id)
        if len(reads) == 1:
            raise sqlite3.OperationalError("database is locked")
        return entry_budget(db, record)

    monkeypatch.setattr("finbot.bot.ai_handlers.entry_budget", flaky_budget)
    caplog.set_level(logging.DEBUG)

    requests = await harness.press(callback_data(draft.reply_markup, "Save 3 entries"))

    assert len(of(requests, SendMessage)) == 3
    assert [e.text for e in of(requests, EditMessageText)] == ["Saved 3 entries."]
    assert len(all_records(conn)) == 3
    messages = [r.getMessage() for r in caplog.records if r.name == "finbot.ai"]
    assert messages == ["budget read failed: OperationalError"]


async def test_category_list_failure_sends_the_reply_with_the_entry_keyboard(
    conn: Any, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", propose(entry(category="")))),
    )
    harness = Harness(conn, fake)
    draft = await draft_with(harness)

    def broken(*_args: Any, **_kwargs: Any) -> None:
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr("finbot.bot.ai_handlers.list_categories", broken)
    caplog.set_level(logging.DEBUG)

    [saved] = of(await harness.press(callback_data(draft.reply_markup, "Save")), SendMessage)

    assert saved.text == "Saved 31.10: -25.00 EUR · кофе с другом\nPick a category:"
    assert labels(saved.reply_markup) == [["Change category", "Undo"]]
    assert len(all_records(conn)) == 1
    messages = [r.getMessage() for r in caplog.records if r.name == "finbot.ai"]
    assert messages == ["category list failed: OperationalError"]


async def test_cancel_failure_is_answered_once_and_leaves_the_draft_open(
    conn: Any, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)

    def broken(*_args: Any, **_kwargs: Any) -> None:
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr("finbot.bot.ai_handlers.cancel_draft", broken)
    caplog.set_level(logging.DEBUG)

    requests = await harness.press(callback_data(draft.reply_markup, "Cancel"))

    [answer] = of(requests, AnswerCallbackQuery)
    assert answer.text == DRAFT_CANCEL_FAILED
    assert of(requests, EditMessageText) == []
    stored = get_draft(conn, 1)
    assert stored is not None
    assert stored.status == "open"
    messages = [r.getMessage() for r in caplog.records if r.name == "finbot.ai"]
    assert messages == ["cancel failed: OperationalError"]


async def test_unexpected_error_on_save_is_answered_and_logged_by_class_only(
    conn: Any, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", propose(entry()))))
    harness = Harness(conn, fake)
    draft = await draft_with(harness)

    def broken(*_args: Any, **_kwargs: Any) -> None:
        raise ValueError("secret words in the message")

    monkeypatch.setattr("finbot.bot.ai_handlers.save_draft", broken)
    caplog.set_level(logging.DEBUG)

    [answer] = of(
        await harness.press(callback_data(draft.reply_markup, "Save")), AnswerCallbackQuery
    )

    assert answer.text == DRAFT_SAVE_FAILED
    assert all_records(conn) == []
    records = [r for r in caplog.records if r.name == "finbot.ai"]
    assert [r.getMessage() for r in records] == ["draft save failed: ValueError"]
    assert records[0].levelno == logging.ERROR
