import asyncio
import logging
import sqlite3
import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any, cast

import anthropic
from anthropic import AsyncAnthropic
from anthropic.types import (
    MessageParam,
    TextBlock,
    ToolResultBlockParam,
    ToolUseBlock,
    UserMessageParam,
)

from finbot.ai_tools import TOOLS, run_read_tool
from finbot.drafts import DraftEntry, DraftError, check_draft

MODEL = "claude-sonnet-5-5"
MAX_CALLS = 4
DAILY_CAP = 100
TURN_SECONDS = 90.0
ANSWER_MAX = 4000
CREDITS_MSG = "AI credits are used up or expired. Nothing saved. Write it as 25 coffee."
SPEND_LIMIT_MSG = "AI spend limit for this month is reached. Nothing saved. Write it as 25 coffee."
KEY_MSG = "The AI key is not accepted. Nothing saved. Write it as 25 coffee."
UNAVAILABLE_MSG = "AI is not available right now. Nothing saved. Write it as 25 coffee."
UNCLEAR_MSG = "I could not make sense of that. Write it as 25 coffee, or ask again."
DRAFT_FAILED = "I could not draft that: {reason}. Nothing saved. Write it as 25 coffee."
DAILY_CAP_MSG = (
    f"AI daily limit reached ({DAILY_CAP} requests). Write it as 25 coffee. It resets at midnight."
)
_ONE_PROPOSAL = "only one propose_entries per reply"
_log = logging.getLogger("finbot.ai")


@dataclass(frozen=True)
class Proposal:
    entries: tuple[DraftEntry, ...]
    replaces_open_draft: bool


@dataclass(frozen=True)
class Answer:
    text: str


@dataclass(frozen=True)
class Failure:
    reply: str


TurnResult = Proposal | Answer | Failure


@dataclass(frozen=True)
class _ToolRound:
    reason: str | None
    results: list[ToolResultBlockParam]


async def run_turn(
    client: AsyncAnthropic,
    conn: sqlite3.Connection,
    *,
    system: str,
    history: list[MessageParam],
    user: UserMessageParam,
    source: str,
    message_date: date,
    today: date,
) -> TurnResult:
    messages: list[MessageParam] = [*history, user]
    try:
        async with asyncio.timeout(TURN_SECONDS):
            return await _loop(client, conn, system, messages, source, message_date, today)
    except TimeoutError:
        _log.error("ai turn deadline")
        return Failure(UNAVAILABLE_MSG)
    except anthropic.APIError as error:
        return _api_failure(error)


async def _loop(
    client: AsyncAnthropic,
    conn: sqlite3.Connection,
    system: str,
    messages: list[MessageParam],
    source: str,
    message_date: date,
    today: date,
) -> TurnResult:
    reason: str | None = None
    for number in range(1, MAX_CALLS + 1):
        if not _take_call(conn, today):
            return Failure(DAILY_CAP_MSG)
        started = time.perf_counter()
        response = await client.messages.create(
            model=MODEL,
            max_tokens=4096,
            output_config={"effort": "low"},
            system=system,
            tools=TOOLS,
            messages=messages,
        )
        _log.info(
            "ai call %d/%d model=%s input=%d output=%d stop=%s request=%s %.1fs",
            number,
            MAX_CALLS,
            MODEL,
            response.usage.input_tokens,
            response.usage.output_tokens,
            response.stop_reason,
            getattr(response, "_request_id", None) or "-",
            time.perf_counter() - started,
        )
        if response.stop_reason == "tool_use":
            if not any(isinstance(block, ToolUseBlock) for block in response.content):
                return Failure(UNCLEAR_MSG)
            outcome = _tool_round(conn, response.content, source, message_date, today)
            if isinstance(outcome, Proposal):
                return outcome
            reason = outcome.reason
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": outcome.results})
            continue
        if response.stop_reason == "end_turn":
            text = "".join(
                block.text for block in response.content if isinstance(block, TextBlock)
            ).strip()
            return Answer(text[:ANSWER_MAX]) if text else Failure(UNCLEAR_MSG)
        return Failure(UNCLEAR_MSG)
    if reason is not None:
        return Failure(DRAFT_FAILED.format(reason=reason))
    return Failure(UNCLEAR_MSG)


def _tool_round(
    conn: sqlite3.Connection,
    content: Sequence[object],
    source: str,
    message_date: date,
    today: date,
) -> Proposal | _ToolRound:
    results: list[ToolResultBlockParam] = []
    reason: str | None = None
    proposed = False
    for block in content:
        if not isinstance(block, ToolUseBlock):
            continue
        raw = cast(dict[str, Any], block.input)
        if block.name == "propose_entries":
            if proposed:
                results.append(_result(block.id, _ONE_PROPOSAL, error=True))
                continue
            proposed = True
            try:
                entries = check_draft(conn, raw, source, message_date)
            except DraftError as error:
                reason = str(error)
                results.append(_result(block.id, reason, error=True))
                continue
            return Proposal(entries, bool(raw.get("replaces_open_draft")))
        text, failed = run_read_tool(conn, block.name, raw, today)
        results.append(_result(block.id, text, error=failed))
    return _ToolRound(reason, results)


def _result(tool_use_id: str, text: str, *, error: bool) -> ToolResultBlockParam:
    return {"type": "tool_result", "tool_use_id": tool_use_id, "content": text, "is_error": error}


def _take_call(conn: sqlite3.Connection, today: date) -> bool:
    key = f"ai_calls:{today.isoformat()}"
    # BEGIN IMMEDIATE takes the write lock before the read, so two turns cannot both pass the cap.
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        count = int(row["value"]) if row is not None else 0
        if count >= DAILY_CAP:
            return False
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (key, str(count + 1))
        )
    return True


def _api_failure(error: anthropic.APIError) -> Failure:
    status = error.status_code if isinstance(error, anthropic.APIStatusError) else None
    request_id = getattr(error, "request_id", None)
    _log.error(
        "ai call failed: %s status=%s request=%s",
        type(error).__name__,
        status or "-",
        request_id or "-",
    )
    if isinstance(error, anthropic.APIStatusError):
        # Credits and the spend limit come back as HTTP 400 too; only the body tells them apart.
        kind, message = _error_body(error.body)
        if status in (400, 402) and (
            kind == "billing_error" or "credit balance" in message.lower()
        ):
            return Failure(CREDITS_MSG)
        if status == 400 and message.startswith("You have reached your specified"):
            return Failure(SPEND_LIMIT_MSG)
    if isinstance(error, anthropic.AuthenticationError | anthropic.PermissionDeniedError):
        return Failure(KEY_MSG)
    return Failure(UNAVAILABLE_MSG)


def _error_body(body: object) -> tuple[str, str]:
    inner = body.get("error") if isinstance(body, dict) else None
    if not isinstance(inner, dict):
        return "", ""
    return str(inner.get("type", "")), str(inner.get("message", ""))
