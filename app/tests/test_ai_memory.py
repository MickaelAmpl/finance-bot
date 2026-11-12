from datetime import UTC, datetime, timedelta

from anthropic.types import AssistantMessageParam, UserMessageParam

from finbot.ai_memory import Memory

T0 = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)


def _exchange(memory: Memory, n: int, now: datetime, draft_id: int | None = None) -> None:
    memory.add(f"u{n}", f"a{n}", now, draft_id)


def test_keeps_last_ten_items_starting_with_user():
    memory = Memory()
    for n in range(6):
        _exchange(memory, n, T0)
    history = memory.history(T0)
    assert len(history) == 10
    assert history[0] == UserMessageParam(role="user", content="u1")
    assert history[1] == AssistantMessageParam(role="assistant", content="a1")
    assert history[-1] == AssistantMessageParam(role="assistant", content="a5")


def test_history_returns_copies():
    memory = Memory()
    _exchange(memory, 0, T0)
    first = memory.history(T0)
    first[0]["content"] = "changed"
    first.append(UserMessageParam(role="user", content="extra"))
    assert memory.history(T0) == [
        UserMessageParam(role="user", content="u0"),
        AssistantMessageParam(role="assistant", content="a0"),
    ]


def test_history_empties_after_two_hours_and_keeps_within_them():
    memory = Memory()
    _exchange(memory, 0, T0)
    assert len(memory.history(T0 + timedelta(hours=1, minutes=59))) == 2
    assert memory.history(T0 + timedelta(hours=2, seconds=1)) == []


def test_mark_draft_appends_to_the_right_assistant_item():
    memory = Memory()
    _exchange(memory, 0, T0)
    _exchange(memory, 1, T0, draft_id=7)
    memory.mark_draft(7, "[draft saved]")
    history = memory.history(T0)
    assert history[1] == AssistantMessageParam(role="assistant", content="a0")
    assert history[3] == AssistantMessageParam(role="assistant", content="a1\n[draft saved]")


def test_mark_draft_for_a_draft_no_longer_kept_does_nothing():
    memory = Memory()
    _exchange(memory, 0, T0, draft_id=7)
    for n in range(1, 6):
        _exchange(memory, n, T0)
    memory.mark_draft(7, "[draft saved]")
    assert all("[draft saved]" not in str(item["content"]) for item in memory.history(T0))


def test_add_after_ttl_starts_a_fresh_history():
    memory = Memory()
    _exchange(memory, 0, T0)
    memory.add("new", "reply", T0 + timedelta(hours=3))
    assert memory.history(T0 + timedelta(hours=3)) == [
        UserMessageParam(role="user", content="new"),
        AssistantMessageParam(role="assistant", content="reply"),
    ]
