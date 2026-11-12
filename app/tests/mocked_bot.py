import json
from collections import defaultdict, deque
from collections.abc import AsyncGenerator
from itertools import count
from typing import Any

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import GetFile, TelegramMethod
from aiogram.types import Message

TOKEN = "42:TEST"

Reply = tuple[bool, Any, int, str | None]


class MockedSession(BaseSession):
    def __init__(self) -> None:
        super().__init__()
        self.requests: list[TelegramMethod[Any]] = []
        self.queued: defaultdict[type[TelegramMethod[Any]], deque[Reply]] = defaultdict(deque)
        self.files: dict[str, bytes] = {}
        self._message_ids = count(100)

    async def close(self) -> None:
        return None

    async def make_request(
        self, bot: Bot, method: TelegramMethod[Any], timeout: int | None = None
    ) -> Any:
        self.requests.append(method)
        queue = self.queued[type(method)]
        ok, result, error_code, description = (
            queue.popleft() if queue else (True, self._default_result(method), 200, None)
        )
        content = json.dumps({"ok": ok, "result": result, "description": description})
        response = self.check_response(
            bot=bot, method=method, status_code=error_code, content=content
        )
        return response.result

    async def stream_content(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        timeout: int = 30,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes, None]:
        for file_path, data in self.files.items():
            if url.endswith(file_path):
                yield data
                return
        raise NotImplementedError("the mocked session has no such file")

    def _default_result(self, method: TelegramMethod[Any]) -> Any:
        if method.__returning__ is bool:
            return True
        if method.__returning__ is Message:
            return {
                "message_id": next(self._message_ids),
                "date": 0,
                "chat": {"id": 42, "type": "private"},
            }
        return None


class MockedBot(Bot):
    def __init__(self) -> None:
        self.mocked_session = MockedSession()
        super().__init__(TOKEN, session=self.mocked_session)

    @property
    def requests(self) -> list[TelegramMethod[Any]]:
        return self.mocked_session.requests

    def add_result_for(
        self,
        method_class: type[TelegramMethod[Any]],
        ok: bool,
        result: Any = None,
        error_code: int = 200,
        description: str | None = None,
    ) -> None:
        self.mocked_session.queued[method_class].append((ok, result, error_code, description))

    def add_file(self, file_id: str, data: bytes) -> None:
        file_path = f"files/{file_id}"
        self.mocked_session.files[file_path] = data
        self.add_result_for(
            GetFile,
            ok=True,
            result={"file_id": file_id, "file_unique_id": file_id, "file_path": file_path},
        )
