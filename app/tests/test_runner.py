import asyncio
import io
import logging
import os
import socket
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from aiogram.client.session.aiohttp import AiohttpSession

from finbot.bot.session import build_bot, redact_token_in_logs

APP_DIR = Path(__file__).resolve().parent.parent
TOKEN = "123456:SECRET"


def run_python(cwd: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    dropped = (
        "BOT_TOKEN",
        "OWNER_ID",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_LOG",
        "ANTHROPIC_BASE_URL",
    )
    env = {k: v for k, v in os.environ.items() if k not in dropped}
    env["PYTHONPATH"] = str(APP_DIR)
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        timeout=60,
    )


@pytest.fixture
def log_output() -> Iterator[io.StringIO]:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    root = logging.getLogger()
    # Tests add secret filters to pytest's shared handlers too; restore them afterwards.
    saved = [(h, list(h.filters)) for h in root.handlers]
    root.addHandler(handler)
    redact_token_in_logs(TOKEN)
    yield stream
    root.removeHandler(handler)
    for existing, filters in saved:
        existing.filters[:] = filters


def test_bot_session_connects_over_ipv4_only() -> None:
    session = build_bot("1:x").session
    assert isinstance(session, AiohttpSession)
    assert session._connector_init["family"] == socket.AF_INET


def test_token_is_masked_in_log_messages(log_output: io.StringIO) -> None:
    logging.getLogger("finbot.test").error(
        "request failed: https://api.telegram.org/bot123456:SECRET/getUpdates"
    )
    output = log_output.getvalue()
    assert "***" in output
    assert "123456:SECRET" not in output


def test_token_is_masked_in_tracebacks(log_output: io.StringIO) -> None:
    try:
        raise RuntimeError("failed: https://api.telegram.org/bot123456:SECRET/sendDocument")
    except RuntimeError:
        logging.getLogger("finbot.test").exception("daily job failed")
    output = log_output.getvalue()
    assert "RuntimeError" in output
    assert "***" in output
    assert "123456:SECRET" not in output


def test_api_key_is_masked_in_chained_tracebacks(log_output: io.StringIO) -> None:
    redact_token_in_logs(TOKEN, "sk-ant-api03-REALKEY")
    try:
        try:
            raise ValueError("bad key sk-ant-api03-REALKEY")
        except ValueError as first:
            raise RuntimeError("request failed for 123456:SECRET") from first
    except RuntimeError:
        logging.getLogger("finbot.test").exception("model call failed")
    output = log_output.getvalue()
    assert "ValueError" in output and "RuntimeError" in output
    assert "sk-ant-api03-REALKEY" not in output
    assert "123456:SECRET" not in output


def test_empty_or_missing_secrets_leave_plain_text_unchanged(log_output: io.StringIO) -> None:
    redact_token_in_logs(TOKEN, None)
    redact_token_in_logs(TOKEN, "")
    logging.getLogger("finbot.test").error("abc")
    assert log_output.getvalue() == "abc\n"


def test_unconfigured_anthropic_style_key_is_masked(log_output: io.StringIO) -> None:
    redact_token_in_logs(TOKEN, None)
    logging.getLogger("finbot.test").error("key sk-ant-other-123 rejected")
    assert log_output.getvalue() == "key *** rejected\n"


def test_child_process_does_not_inherit_anthropic_variables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in (
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_LOG",
        "ANTHROPIC_BASE_URL",
    ):
        monkeypatch.setenv(name, "x")
    result = run_python(
        tmp_path, "-c", "import os; print(any(k.startswith('ANTHROPIC_') for k in os.environ))"
    )
    assert result.stdout.strip() == b"False"


def test_network_is_blocked_for_external_addresses() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        with pytest.raises(RuntimeError, match="network blocked in tests"):
            sock.connect(("93.184.216.34", 443))
    finally:
        sock.close()


def test_jobs_without_a_command_exits_with_usage_error(tmp_path: Path) -> None:
    assert run_python(tmp_path, "-m", "finbot.jobs").returncode == 2


def test_jobs_with_an_unknown_command_exits_with_usage_error(tmp_path: Path) -> None:
    assert run_python(tmp_path, "-m", "finbot.jobs", "weekly").returncode == 2


def test_entry_modules_import_without_running_anything(tmp_path: Path) -> None:
    assert run_python(tmp_path, "-c", "import finbot.__main__, finbot.jobs").returncode == 0


def test_longer_secret_is_masked_before_a_shorter_one_inside_it(log_output: io.StringIO) -> None:
    redact_token_in_logs("abc", "abcdef-SECRET")
    logging.getLogger("finbot.test").error("text abcdef-SECRET")
    assert log_output.getvalue() == "text ***\n"


def test_whitespace_only_secret_is_skipped(log_output: io.StringIO) -> None:
    redact_token_in_logs("  ", None)
    logging.getLogger("finbot.test").error("a  b")
    assert log_output.getvalue() == "a  b\n"


def test_key_in_format_arguments_is_masked(log_output: io.StringIO) -> None:
    redact_token_in_logs(TOKEN, "sk-ant-api03-REALKEY")
    logging.getLogger("finbot.test").error("x %s", "sk-ant-api03-REALKEY")
    assert log_output.getvalue() == "x ***\n"


def test_key_in_stack_info_is_masked(log_output: io.StringIO) -> None:
    redact_token_in_logs(TOKEN, "sk-ant-api03-REALKEY")
    logger = logging.getLogger("finbot.test")
    record = logger.makeRecord(
        logger.name,
        logging.ERROR,
        __file__,
        1,
        "boom",
        (),
        None,
        sinfo="Stack: sk-ant-api03-REALKEY",
    )
    logger.handle(record)
    output = log_output.getvalue()
    assert "Stack: ***" in output
    assert "sk-ant-api03-REALKEY" not in output


def test_loopback_connect_is_allowed() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(server.getsockname())
    finally:
        client.close()
        server.close()


def test_connect_ex_is_blocked_for_external_addresses() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        with pytest.raises(RuntimeError, match="network blocked in tests"):
            sock.connect_ex(("93.184.216.34", 443))
    finally:
        sock.close()


async def test_asyncio_connection_to_external_host_is_blocked() -> None:
    with pytest.raises(RuntimeError, match="network blocked in tests"):
        await asyncio.open_connection("93.184.216.34", 443)


def test_dns_lookup_of_external_host_is_blocked() -> None:
    with pytest.raises(RuntimeError, match="network blocked in tests"):
        socket.getaddrinfo("example.com", 443)
