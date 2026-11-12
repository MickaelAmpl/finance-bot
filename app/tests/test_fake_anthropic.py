import anthropic
import httpx2
import pytest

from tests.fake_anthropic import FakeAnthropic, api_error, text_reply, tool_reply

CALL = {
    "model": "claude-sonnet-5-5",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "hi"}],
}


async def test_scripted_text_reply_is_returned_and_request_recorded() -> None:
    fake = FakeAnthropic(text_reply("hello"))
    message = await fake.client.messages.create(**CALL)
    assert message.content[0].text == "hello"
    assert message.stop_reason == "end_turn"
    assert fake.requests[0]["model"] == "claude-sonnet-5-5"


async def test_tool_reply_carries_tool_use_blocks() -> None:
    fake = FakeAnthropic(tool_reply(("tu_1", "lookup", {"q": "food"}), text="checking"))
    message = await fake.client.messages.create(**CALL)
    assert message.stop_reason == "tool_use"
    assert [block.type for block in message.content] == ["text", "tool_use"]
    assert message.content[1].name == "lookup"


async def test_api_error_raises_the_sdk_error_with_request_id() -> None:
    fake = FakeAnthropic(api_error(400, "bad input"))
    with pytest.raises(anthropic.BadRequestError) as info:
        await fake.client.messages.create(**CALL)
    assert info.value.request_id == "req_1"


async def test_empty_script_fails_the_test() -> None:
    fake = FakeAnthropic()
    with pytest.raises(anthropic.APIConnectionError) as info:
        await fake.client.messages.create(**CALL)
    assert isinstance(info.value.__cause__, AssertionError)
    assert "no scripted reply" in str(info.value.__cause__)


async def test_connect_error_surfaces_as_api_connection_error() -> None:
    fake = FakeAnthropic(httpx2.ConnectError("refused"))
    with pytest.raises(anthropic.APIConnectionError):
        await fake.client.messages.create(**CALL)


def test_tool_reply_without_text_has_no_text_block() -> None:
    message = tool_reply(("tu_1", "lookup", {}))
    assert [block["type"] for block in message["content"]] == ["tool_use"]
