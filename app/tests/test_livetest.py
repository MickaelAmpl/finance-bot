import logging
import sys
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from finbot import livetest
from finbot.assistant import UNAVAILABLE_MSG
from finbot.db import connect
from finbot.ledger import records_between
from finbot.livetest import QUESTIONS, TEXTS, build_synthetic_db, main, run
from finbot.money import format_cents
from finbot.reports import build_month_report
from finbot.savings import get_pot
from tests.fake_anthropic import FakeAnthropic, api_error, text_reply, tool_reply

TODAY = date(2026, 11, 12)
KEY = "sk-ant-test-0000"
PROPOSE = {
    "entries": [
        {
            "kind": "expense",
            "amount": "25",
            "currency": "EUR",
            "category": "",
            "note": "coffee",
            "date": "2026-11-12",
        }
    ],
    "replaces_open_draft": False,
}
_LOGGERS = ("anthropic", "httpx2", "httpcore2", "finbot.ai")


@pytest.fixture(autouse=True)
def restore_logging() -> Iterator[None]:
    # main() installs a key filter on the root handlers and sets logger levels; undo both.
    root = logging.getLogger()
    handlers = list(root.handlers)
    filters = {handler: list(handler.filters) for handler in handlers}
    root_level = root.level
    levels = {name: logging.getLogger(name).level for name in _LOGGERS}
    yield
    root.handlers[:] = handlers
    for handler, saved in filters.items():
        handler.filters[:] = saved
    root.setLevel(root_level)
    for name, level in levels.items():
        logging.getLogger(name).setLevel(level)


def count(conn_path: Path, table: str) -> int:
    conn = connect(conn_path)
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        conn.close()


def _env(tmp_path: Path, text: str) -> Path:
    # The .env sits in its own folder so that --db in tmp_path is outside it.
    env = tmp_path / "app" / ".env"
    env.parent.mkdir(exist_ok=True)
    env.write_text(text, encoding="utf-8")
    return env


def _argv(monkeypatch: pytest.MonkeyPatch, env: Path, db: Path) -> None:
    monkeypatch.setattr(sys, "argv", ["livetest", "--env", str(env), "--db", str(db)])


def test_expected_answers_match_the_reports(tmp_path: Path) -> None:
    path = tmp_path / "live.db"
    expected = build_synthetic_db(path, TODAY)
    conn = connect(path)
    october = build_month_report(conn, 2026, 10)
    november = build_month_report(conn, 2026, 11)
    eating = next(b for b in november.budgets if b.category == "Eating out")
    pot = get_pot(conn, "emergency")
    assert pot is not None
    assert format_cents(october.spent_cents) in expected[QUESTIONS[0]]
    assert format_cents(eating.spent_cents) in expected[QUESTIONS[1]]
    assert format_cents(eating.left_cents) in expected[QUESTIONS[1]]
    assert november.pending == 2
    assert format_cents(pot.total_cents) in expected[QUESTIONS[3]]
    assert pot.total_cents == 50000
    conn.close()


def test_groceries_window_differs_from_all_of_october(tmp_path: Path) -> None:
    path = tmp_path / "live.db"
    expected = build_synthetic_db(path, TODAY)
    conn = connect(path)
    window = sum(
        r.eur_cents or 0
        for r in records_between(conn, date(2026, 10, 1), date(2026, 10, 15))
        if r.category == "Groceries" and r.kind == "expense" and not r.pending
    )
    month = sum(
        r.eur_cents or 0
        for r in records_between(conn, date(2026, 10, 1), date(2026, 10, 31))
        if r.category == "Groceries" and r.kind == "expense" and not r.pending
    )
    conn.close()
    assert window != month
    assert expected[QUESTIONS[2]] == f"Groceries 01.10-15.10: {format_cents(window)} EUR"


def test_existing_database_path_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "live.db"
    path.write_text("taken")
    with pytest.raises(FileExistsError):
        build_synthetic_db(path, TODAY)


async def test_run_prints_each_message_and_saves_nothing(tmp_path: Path) -> None:
    path = tmp_path / "live.db"
    expected = build_synthetic_db(path, TODAY)
    script = [tool_reply(("tu_1", "propose_entries", PROPOSE)) for _ in TEXTS]
    script += [text_reply(f"answer {n}") for n, _ in enumerate(QUESTIONS, start=1)]
    fake = FakeAnthropic(*script)
    entries_before = count(path, "entries")
    conn = connect(path)
    lines: list[str] = []
    await run(fake.client, conn, TODAY, lines.append)
    conn.close()

    assert sum(line.startswith("> ") for line in lines) == 15
    assert any(line.startswith("Draft:") for line in lines)
    assert sum(line.startswith("expected: ") for line in lines) == 5
    for question in QUESTIONS:
        assert f"expected: {expected[question]}" in lines
    assert count(path, "entries") == entries_before
    assert count(path, "drafts") == 0


async def test_failure_is_printed_and_kept_out_of_memory(tmp_path: Path) -> None:
    path = tmp_path / "live.db"
    build_synthetic_db(path, TODAY)
    script: list[Any] = [api_error(500, "boom", "api_error")]
    script.append(tool_reply(("tu_1", "propose_entries", PROPOSE)))
    script += [text_reply("answer") for _ in range(len(TEXTS) + len(QUESTIONS) - 2)]
    fake = FakeAnthropic(*script)
    conn = connect(path)
    lines: list[str] = []
    failed = await run(fake.client, conn, TODAY, lines.append)
    conn.close()

    assert failed == 1
    assert UNAVAILABLE_MSG in lines
    # Message 2 starts with empty memory: the failed message 1 was not kept.
    assert fake.requests[1]["messages"] == [{"role": "user", "content": TEXTS[1]}]
    # Message 3 sees the draft reply of message 2, not the failure.
    history = fake.requests[2]["messages"]
    assert history[0] == {"role": "user", "content": TEXTS[1]}
    assert history[1]["role"] == "assistant"
    assert history[1]["content"].startswith("Draft:")
    assert history[2] == {"role": "user", "content": TEXTS[2]}


async def test_lines_are_emitted_as_each_turn_produces_them(tmp_path: Path) -> None:
    path = tmp_path / "live.db"
    build_synthetic_db(path, TODAY)
    fake = FakeAnthropic(*[text_reply("answer") for _ in range(len(TEXTS) + len(QUESTIONS))])
    seen: list[tuple[str, int]] = []
    conn = connect(path)
    await run(fake.client, conn, TODAY, lambda line: seen.append((line, len(fake.requests))))
    conn.close()

    # Each message line is printed before its own request: the second one sees one request made.
    starts = [requests for line, requests in seen if line.startswith("> ")]
    assert starts[:2] == [0, 1]
    assert [line for line, _ in seen[:2]] == [f"> {TEXTS[0]}", "answer"]


def _main_with_fake_ai(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, script: list[Any]) -> None:
    env = _env(tmp_path, f"ANTHROPIC_API_KEY={KEY}\n")
    fake = FakeAnthropic(*script)
    real_build = livetest.build_synthetic_db
    monkeypatch.setattr(livetest, "build_synthetic_db", lambda path, today: real_build(path, TODAY))
    monkeypatch.setattr(livetest, "AsyncAnthropic", lambda **_: fake.client)
    _argv(monkeypatch, env, tmp_path / "live.db")


def test_main_exits_1_when_every_turn_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    script: list[Any] = [
        api_error(401, "invalid x-api-key", "authentication_error")
        for _ in range(len(TEXTS) + len(QUESTIONS))
    ]
    _main_with_fake_ai(tmp_path, monkeypatch, script)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    assert capsys.readouterr().out.splitlines()[-1] == "failed turns: 15 of 15"


def test_main_exits_0_when_every_turn_succeeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    script: list[Any] = [tool_reply(("tu_1", "propose_entries", PROPOSE)) for _ in TEXTS]
    script += [text_reply("answer") for _ in QUESTIONS]
    _main_with_fake_ai(tmp_path, monkeypatch, script)
    main()
    assert capsys.readouterr().out.splitlines()[-1] == "failed turns: 0 of 15"


def test_main_without_key_exits_2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    env = _env(tmp_path, "BOT_TOKEN=123:abc\nOWNER_ID=1\n")
    _argv(monkeypatch, env, tmp_path / "x.db")
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert "No ANTHROPIC_API_KEY in that file." in capsys.readouterr().err


def test_main_refuses_existing_db(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    env = _env(tmp_path, f"ANTHROPIC_API_KEY={KEY}\n")
    db = tmp_path / "x.db"
    db.write_text("taken")
    _argv(monkeypatch, env, db)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert "already exists" in capsys.readouterr().err


def test_main_refuses_existing_wal_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    env = _env(tmp_path, f"ANTHROPIC_API_KEY={KEY}\n")
    db = tmp_path / "x.db"
    Path(f"{db}-wal").write_text("left over")
    _argv(monkeypatch, env, db)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert "-wal" in capsys.readouterr().err
    assert not db.exists()


def test_main_refuses_db_in_env_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    env = _env(tmp_path, f"ANTHROPIC_API_KEY={KEY}\n")
    db = env.parent / "data" / "live.db"
    _argv(monkeypatch, env, db)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert "folder of the .env" in capsys.readouterr().err
    assert not db.exists()


def test_main_turns_too_early_date_into_exit_2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    env = _env(tmp_path, f"ANTHROPIC_API_KEY={KEY}\n")
    _argv(monkeypatch, env, tmp_path / "x.db")

    def too_early(path: Path, today: date) -> dict[str, str]:
        raise ValueError("The synthetic data runs to 10.11.2026; run this on or after that day.")

    monkeypatch.setattr(livetest, "build_synthetic_db", too_early)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    assert "runs to 10.11.2026" in capsys.readouterr().err


def test_main_output_never_contains_the_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    env = _env(tmp_path, f"ANTHROPIC_API_KEY={KEY}\n")
    monkeypatch.setattr(livetest, "build_synthetic_db", lambda path, today: {})

    async def leaking_run(client: object, conn: object, today: date, emit: Any) -> int:
        # A log line that carries the key goes through the real filter on the stdout handler.
        logging.getLogger("finbot.ai").info("ai call with key %s", KEY)
        emit("> hello")
        emit("answer")
        return 0

    monkeypatch.setattr(livetest, "run", leaking_run)
    _argv(monkeypatch, env, tmp_path / "live.db")
    main()
    out = capsys.readouterr()
    assert "ai call with key ***" in out.out
    assert out.out.splitlines()[-3:] == ["> hello", "answer", "failed turns: 0 of 15"]
    assert KEY not in out.out + out.err


def test_client_is_built_with_the_planned_settings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env = _env(tmp_path, f"ANTHROPIC_API_KEY={KEY}\n")
    captured: dict[str, Any] = {}

    class RecordingClient:
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)

    async def quiet_run(client: object, conn: object, today: date, emit: Any) -> int:
        return 0

    monkeypatch.setattr(livetest, "AsyncAnthropic", RecordingClient)
    monkeypatch.setattr(livetest, "build_synthetic_db", lambda path, today: {})
    monkeypatch.setattr(livetest, "run", quiet_run)
    _argv(monkeypatch, env, tmp_path / "live.db")
    main()
    assert captured["api_key"] == KEY
    assert captured["base_url"] == "https://api.anthropic.com"
    assert captured["timeout"].read == 45.0
    assert captured["timeout"].connect == 5.0
    assert captured["max_retries"] == 2
