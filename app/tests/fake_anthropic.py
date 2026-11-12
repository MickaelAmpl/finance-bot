import json
from dataclasses import dataclass
from typing import Any

import anthropic
import httpx2

MODEL = "claude-sonnet-5-5"
_USAGE = {"input_tokens": 100, "output_tokens": 20}


@dataclass(frozen=True)
class ApiError:
    status: int
    message: str
    type_: str


def api_error(status: int, message: str, type_: str = "invalid_request_error") -> ApiError:
    return ApiError(status=status, message=message, type_=type_)


def reply(content: list[dict[str, Any]], stop_reason: str) -> dict[str, Any]:
    return {
        "id": "msg_1",
        "type": "message",
        "role": "assistant",
        "model": MODEL,
        "content": content,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": dict(_USAGE),
    }


def text_reply(text: str) -> dict[str, Any]:
    return reply([{"type": "text", "text": text}], "end_turn")


def tool_reply(*uses: tuple[str, str, dict[str, Any]], text: str = "") -> dict[str, Any]:
    content: list[dict[str, Any]] = [{"type": "text", "text": text}] if text else []
    content += [
        {"type": "tool_use", "id": use_id, "name": name, "input": tool_input}
        for use_id, name, tool_input in uses
    ]
    return reply(content, "tool_use")


class FakeAnthropic:
    def __init__(self, *script: dict[str, Any] | ApiError | Exception) -> None:
        self._script = list(script)
        self._calls = 0
        self.requests: list[dict[str, Any]] = []
        transport = httpx2.MockTransport(self._handle)
        self.client = anthropic.AsyncAnthropic(
            api_key="sk-ant-test-0000",
            http_client=httpx2.AsyncClient(transport=transport),
            max_retries=0,
        )

    def _handle(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(json.loads(request.content))
        if not self._script:
            raise AssertionError("no scripted reply")
        self._calls += 1
        item = self._script.pop(0)
        headers = {"request-id": f"req_{self._calls}"}
        if isinstance(item, Exception):
            raise item
        if isinstance(item, ApiError):
            body = {"type": "error", "error": {"type": item.type_, "message": item.message}}
            return httpx2.Response(item.status, json=body, headers=headers)
        return httpx2.Response(200, json=item, headers=headers)
