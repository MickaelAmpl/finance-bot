import asyncio
import logging
import re
import sqlite3
from datetime import date
from typing import Any

import httpx2
import pytest
from anthropic.types import UserMessageParam

from finbot import assistant
from finbot.assistant import (
    CREDITS_MSG,
    DAILY_CAP_MSG,
    KEY_MSG,
    SPEND_LIMIT_MSG,
    UNAVAILABLE_MSG,
    UNCLEAR_MSG,
    Answer,
    Failure,
    Proposal,
    TurnResult,
    run_turn,
)
from finbot.drafts import DraftEntry
from tests.fake_anthropic import FakeAnthropic, api_error, reply, text_reply, tool_reply

SYSTEM = "system prompt"
MESSAGE_DATE = date(2026, 11, 1)
USER: UserMessageParam = {"role": "user", "content": "кофе-секрет 25"}
PROPOSE = {
    "entries": [
        {
            "kind": "expense",
            "amount": "25",
            "currency": "EUR",
            "category": "",
            "note": "coffee",
            "date": "2026-11-01",
        }
    ],
    "replaces_open_draft": False,
}
LATE = {**PROPOSE, "entries": [{**PROPOSE["entries"][0], "date": "2026-11-02"}]}
LATE_REASON = "entry 1: 2026-11-02 is after the message date"
LIST_ENTRIES = {"start": "2026-11-01", "end": "2026-11-30"}


async def turn(
    fake: FakeAnthropic,
    conn: sqlite3.Connection,
    *,
    history: list[Any] | None = None,
    today: date = MESSAGE_DATE,
) -> TurnResult:
    return await run_turn(
        fake.client,
        conn,
        system=SYSTEM,
        history=history or [],
        user=USER,
        source="text",
        message_date=MESSAGE_DATE,
        today=today,
    )


def set_calls(conn: sqlite3.Connection, day: date, count: int) -> None:
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
            (f"ai_calls:{day.isoformat()}", str(count)),
        )


async def test_valid_draft_returns_proposal_with_one_request(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "propose_entries", PROPOSE), text="ignored"))
    result = await turn(fake, conn)
    assert result == Proposal(
        entries=(
            DraftEntry(
                kind="expense",
                amount_cents=2500,
                currency="EUR",
                category_id=None,
                category=None,
                note="coffee",
                on=date(2026, 11, 1),
            ),
        ),
        replaces_open_draft=False,
    )
    assert len(fake.requests) == 1


async def test_replaces_open_draft_flag_passes_through(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", {**PROPOSE, "replaces_open_draft": True}))
    )
    result = await turn(fake, conn)
    assert isinstance(result, Proposal)
    assert result.replaces_open_draft is True


async def test_request_contract_and_second_call_carries_results(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "list_entries", LIST_ENTRIES)),
        text_reply("done"),
    )
    assert await turn(fake, conn) == Answer(text="done")
    assert len(fake.requests) == 2
    first, second = fake.requests
    assert first["model"] == "claude-sonnet-5-5"
    assert first["max_tokens"] == 4096
    assert first["output_config"] == {"effort": "low"}
    for key in ("thinking", "tool_choice", "temperature", "top_p", "top_k"):
        assert key not in first
    assert [tool["name"] for tool in first["tools"]] == [
        "propose_entries",
        "month_summary",
        "list_entries",
        "savings",
    ]
    assert all(tool["strict"] is True for tool in first["tools"])
    assert first["system"] == SYSTEM
    assert second["system"] == first["system"]
    assert second["tools"] == first["tools"]
    assert first["messages"] == [USER]
    assert second["messages"][0] == USER
    assert second["messages"][1] == {
        "role": "assistant",
        "content": [
            {"type": "tool_use", "id": "tu_1", "name": "list_entries", "input": LIST_ENTRIES}
        ],
    }
    assert second["messages"][2]["role"] == "user"
    assert [block["type"] for block in second["messages"][2]["content"]] == ["tool_result"]
    assert second["messages"][2]["content"][0]["tool_use_id"] == "tu_1"
    assert second["messages"][2]["content"][0]["is_error"] is False


async def test_invalid_draft_is_sent_back_then_corrected_draft_wins(
    conn: sqlite3.Connection,
) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", LATE)),
        tool_reply(("tu_2", "propose_entries", PROPOSE)),
    )
    result = await turn(fake, conn)
    assert isinstance(result, Proposal)
    assert len(fake.requests) == 2
    assert fake.requests[1]["messages"][-1]["content"] == [
        {"type": "tool_result", "tool_use_id": "tu_1", "content": LATE_REASON, "is_error": True}
    ]


async def test_four_invalid_drafts_fail_with_the_last_reason(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(*[tool_reply((f"tu_{n}", "propose_entries", LATE)) for n in range(4)])
    assert await turn(fake, conn) == Failure(
        f"I could not draft that: {LATE_REASON}. Nothing saved. Write it as 25 coffee."
    )
    assert len(fake.requests) == 4


async def test_four_read_tool_calls_end_unclear(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(*[tool_reply((f"tu_{n}", "savings", {})) for n in range(4)])
    assert await turn(fake, conn) == Failure(UNCLEAR_MSG)
    assert len(fake.requests) == 4


async def test_read_tool_then_text_is_an_answer_cut_to_limit(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "list_entries", LIST_ENTRIES)), text_reply("a" * 5000))
    assert await turn(fake, conn) == Answer(text="a" * assistant.ANSWER_MAX)


async def test_empty_text_is_unclear(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(text_reply("   "))
    assert await turn(fake, conn) == Failure(UNCLEAR_MSG)


@pytest.mark.parametrize("stop_reason", ["max_tokens", "refusal"])
async def test_other_stop_reasons_are_unclear(conn: sqlite3.Connection, stop_reason: str) -> None:
    fake = FakeAnthropic(reply([{"type": "text", "text": "half"}], stop_reason))
    assert await turn(fake, conn) == Failure(UNCLEAR_MSG)
    assert len(fake.requests) == 1


async def test_two_tool_uses_are_answered_in_one_user_message(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "month_summary", {"month": "2026-11"}), ("tu_2", "savings", {})),
        text_reply("ok"),
    )
    assert await turn(fake, conn) == Answer(text="ok")
    results = fake.requests[1]["messages"][-1]["content"]
    assert [block["tool_use_id"] for block in results] == ["tu_1", "tu_2"]


async def test_second_propose_in_one_reply_is_refused(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", LATE), ("tu_2", "propose_entries", PROPOSE)),
        tool_reply(("tu_3", "propose_entries", PROPOSE)),
    )
    assert isinstance(await turn(fake, conn), Proposal)
    assert fake.requests[1]["messages"][-1]["content"] == [
        {"type": "tool_result", "tool_use_id": "tu_1", "content": LATE_REASON, "is_error": True},
        {
            "type": "tool_result",
            "tool_use_id": "tu_2",
            "content": "only one propose_entries per reply",
            "is_error": True,
        },
    ]


async def test_history_is_not_written_back(conn: sqlite3.Connection) -> None:
    history: list[Any] = [
        {"role": "user", "content": "earlier"},
        {"role": "assistant", "content": "reply"},
    ]
    before = list(history)
    fake = FakeAnthropic(text_reply("fine"))
    await turn(fake, conn, history=history)
    assert history == before
    assert fake.requests[0]["messages"] == [*before, USER]


SECRET_WORDS = " кофе-секрет sk-ant-test-0000"


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (
            api_error(
                400, "Your credit balance is too low to access the Anthropic API." + SECRET_WORDS
            ),
            CREDITS_MSG,
        ),
        (api_error(402, "payment required" + SECRET_WORDS, "billing_error"), CREDITS_MSG),
        (
            api_error(
                400,
                "You have reached your specified API usage limits. You will regain access "
                "on 2026-12-01 at 00:00 UTC." + SECRET_WORDS,
            ),
            SPEND_LIMIT_MSG,
        ),
        (api_error(401, "invalid x-api-key" + SECRET_WORDS, "authentication_error"), KEY_MSG),
        (api_error(403, "forbidden" + SECRET_WORDS, "permission_error"), KEY_MSG),
        (api_error(429, "slow down" + SECRET_WORDS, "rate_limit_error"), UNAVAILABLE_MSG),
        (api_error(500, "boom" + SECRET_WORDS, "api_error"), UNAVAILABLE_MSG),
        (api_error(529, "overloaded" + SECRET_WORDS, "overloaded_error"), UNAVAILABLE_MSG),
        (httpx2.ConnectError("refused" + SECRET_WORDS), UNAVAILABLE_MSG),
    ],
)
async def test_api_errors_map_to_fixed_failures_and_log_no_content(
    conn: sqlite3.Connection,
    caplog: pytest.LogCaptureFixture,
    error: Any,
    expected: str,
) -> None:
    caplog.set_level(logging.INFO, logger="finbot.ai")
    fake = FakeAnthropic(error)
    assert await turn(fake, conn) == Failure(expected)
    assert len(fake.requests) == 1
    assert "ai call failed: " in caplog.text
    assert "кофе-секрет" not in caplog.text
    assert "sk-ant-test-0000" not in caplog.text


async def test_bad_request_log_line_has_class_status_and_request_id(
    conn: sqlite3.Connection, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO, logger="finbot.ai")
    fake = FakeAnthropic(api_error(400, "Your credit balance is too low"))
    await turn(fake, conn)
    assert "ai call failed: BadRequestError status=400 request=req_1" in caplog.text


async def test_connection_error_log_line_has_no_status(
    conn: sqlite3.Connection, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO, logger="finbot.ai")
    fake = FakeAnthropic(httpx2.ConnectError("refused"))
    await turn(fake, conn)
    assert "ai call failed: APIConnectionError status=- request=-\n" in caplog.text


async def test_deadline_gives_unavailable(
    conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO, logger="finbot.ai")
    fake = FakeAnthropic()

    async def slow(**kwargs: object) -> None:
        await asyncio.sleep(1)

    monkeypatch.setattr(fake.client.messages, "create", slow)
    monkeypatch.setattr(assistant, "TURN_SECONDS", 0.05)
    assert await turn(fake, conn) == Failure(UNAVAILABLE_MSG)
    assert "ai turn deadline" in caplog.text
    assert "кофе-секрет" not in caplog.text


async def test_usage_line_is_logged(
    conn: sqlite3.Connection, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO, logger="finbot.ai")
    fake = FakeAnthropic(text_reply("hi"))
    await turn(fake, conn)
    assert re.search(
        r"ai call 1/4 model=claude-sonnet-5-5 input=100 output=20 stop=end_turn "
        r"request=req_1 [0-9]+\.[0-9]s",
        caplog.text,
    )


async def test_daily_cap_allows_the_hundredth_call_then_refuses(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(text_reply("last one"))
    set_calls(conn, MESSAGE_DATE, 99)
    assert await turn(fake, conn) == Answer(text="last one")
    assert await turn(fake, conn) == Failure(DAILY_CAP_MSG)
    assert len(fake.requests) == 1


async def test_daily_cap_counts_today_not_message_date(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(text_reply("fine"))
    set_calls(conn, MESSAGE_DATE, 100)
    assert await turn(fake, conn, today=date(2026, 11, 2)) == Answer(text="fine")
    assert len(fake.requests) == 1


async def test_daily_cap_refuses_without_a_request_on_the_same_day(
    conn: sqlite3.Connection,
) -> None:
    fake = FakeAnthropic()
    set_calls(conn, date(2026, 11, 2), 100)
    assert await turn(fake, conn, today=date(2026, 11, 2)) == Failure(DAILY_CAP_MSG)
    assert fake.requests == []


def count_for(conn: sqlite3.Connection, day: date) -> str | None:
    row = conn.execute(
        "SELECT value FROM meta WHERE key = ?", (f"ai_calls:{day.isoformat()}",)
    ).fetchone()
    return None if row is None else row["value"]


async def test_text_next_to_valid_draft_is_ignored(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "propose_entries", PROPOSE), text="Saved it for you, sure?")
    )
    result = await turn(fake, conn)
    assert isinstance(result, Proposal)
    assert len(fake.requests) == 1


async def test_text_block_before_read_tool_is_replayed_unchanged(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(
        tool_reply(("tu_1", "list_entries", LIST_ENTRIES), text="let me check"),
        text_reply("done"),
    )
    assert await turn(fake, conn) == Answer(text="done")
    assert fake.requests[1]["messages"][1] == {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "let me check"},
            {"type": "tool_use", "id": "tu_1", "name": "list_entries", "input": LIST_ENTRIES},
        ],
    }


async def test_tool_use_without_tool_block_is_unclear_at_once(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(reply([{"type": "text", "text": "hm"}], "tool_use"))
    assert await turn(fake, conn) == Failure(UNCLEAR_MSG)
    assert len(fake.requests) == 1


async def test_cap_hit_mid_loop_stops_before_the_second_call(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "savings", {})), text_reply("never"))
    set_calls(conn, MESSAGE_DATE, 99)
    assert await turn(fake, conn) == Failure(DAILY_CAP_MSG)
    assert len(fake.requests) == 1


async def test_failed_call_still_counts_toward_the_cap(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(api_error(500, "boom", "api_error"))
    assert await turn(fake, conn) == Failure(UNAVAILABLE_MSG)
    assert count_for(conn, MESSAGE_DATE) == "1"


async def test_new_day_counts_on_its_own_key(conn: sqlite3.Connection) -> None:
    fake = FakeAnthropic(text_reply("fine"))
    set_calls(conn, MESSAGE_DATE, 5)
    assert await turn(fake, conn, today=date(2026, 11, 2)) == Answer(text="fine")
    assert count_for(conn, date(2026, 11, 2)) == "1"
    assert count_for(conn, MESSAGE_DATE) == "5"
