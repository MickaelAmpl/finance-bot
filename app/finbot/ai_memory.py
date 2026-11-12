from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from anthropic.types import AssistantMessageParam, MessageParam, UserMessageParam

MEMORY_SIZE = 10
MEMORY_TTL = timedelta(hours=2)


@dataclass
class _Item:
    role: Literal["user", "assistant"]
    text: str
    draft_id: int | None = None


class Memory:
    """The last messages of this process only; nothing is written to disk."""

    def __init__(self) -> None:
        self._items: deque[_Item] = deque(maxlen=MEMORY_SIZE)
        self._last: datetime | None = None

    def history(self, now: datetime) -> list[MessageParam]:
        self._expire(now)
        history: list[MessageParam] = []
        for item in self._items:
            if item.role == "user":
                history.append(UserMessageParam(role="user", content=item.text))
            else:
                history.append(AssistantMessageParam(role="assistant", content=item.text))
        return history

    def add(
        self, user_text: str, reply_text: str, now: datetime, draft_id: int | None = None
    ) -> None:
        self._expire(now)
        self._items.append(_Item("user", user_text))
        self._items.append(_Item("assistant", reply_text, draft_id))
        self._last = now

    def mark_draft(self, draft_id: int, mark: str) -> None:
        for item in self._items:
            if item.draft_id == draft_id:
                item.text += "\n" + mark

    def _expire(self, now: datetime) -> None:
        if self._last is not None and now - self._last > MEMORY_TTL:
            self._items.clear()
