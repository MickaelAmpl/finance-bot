import logging
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import anthropic
import pytest

from finbot.__main__ import build_ai, quiet_sdk_loggers
from finbot.bot.ai_handlers import AiState
from finbot.config import Settings

APP_DIR = Path(__file__).resolve().parent.parent
KEY = "sk-ant-test-0000"
SECRET_WORDS = "кофе-секрет"
SDK_LOGGERS = ("anthropic", "httpx2", "httpcore2")


def settings(key: str | None) -> Settings:
    return Settings(
        bot_token="1:x",
        owner_id=1,
        db_path=Path("data/finbot.db"),
        backup_dir=Path("data/backups"),
        anthropic_api_key=key,
    )


@pytest.fixture
def restore_sdk_levels() -> Iterator[None]:
    saved = {name: logging.getLogger(name).level for name in SDK_LOGGERS}
    yield
    for name, level in saved.items():
        logging.getLogger(name).setLevel(level)


def test_build_ai_without_key_returns_none() -> None:
    assert build_ai(settings(None)) is None


def test_build_ai_with_key_builds_client_with_fixed_settings() -> None:
    ai = build_ai(settings(KEY))
    assert isinstance(ai, AiState)
    client = ai.client
    assert client.api_key == KEY
    assert str(client.base_url).rstrip("/") == "https://api.anthropic.com"
    assert client.timeout == anthropic.Timeout(45.0, connect=5.0)
    assert client.max_retries == 2


def test_quiet_sdk_loggers_overrides_debug(restore_sdk_levels: None) -> None:
    for name in SDK_LOGGERS:
        logging.getLogger(name).setLevel(logging.DEBUG)
    quiet_sdk_loggers()
    for name in SDK_LOGGERS:
        assert logging.getLogger(name).level == logging.WARNING, name


def test_debug_sdk_logging_leaks_no_message_text_or_key() -> None:
    code = (
        "import logging\n"
        "logging.basicConfig(level=logging.INFO)\n"
        "from finbot.__main__ import quiet_sdk_loggers\n"
        "quiet_sdk_loggers()\n"
        "from tests.fake_anthropic import FakeAnthropic, text_reply\n"
        "fake = FakeAnthropic(text_reply('ok'))\n"
        "fake.client.messages.create(\n"
        "    model='claude-sonnet-5-5', max_tokens=16,\n"
        "    messages=[{'role': 'user', 'content': 'кофе-секрет'}],\n"
        ")\n"
        "print('done')\n"
    )
    dropped = ("BOT_TOKEN", "OWNER_ID")
    env = {
        k: v for k, v in os.environ.items() if k not in dropped and not k.startswith("ANTHROPIC_")
    }
    env.update(
        PYTHONPATH=str(APP_DIR),
        ANTHROPIC_LOG="debug",
        ANTHROPIC_API_KEY=KEY,
        PYTHONIOENCODING="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=APP_DIR,
        env=env,
        capture_output=True,
        timeout=60,
    )
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == 0, stderr
    assert stdout.strip() == "done"
    for leaked in (SECRET_WORDS, KEY):
        assert leaked not in stdout
        assert leaked not in stderr


def test_info_logging_survives_an_earlier_basicconfig(tmp_path: Path) -> None:
    # Stands in for the SDK configuring logging at import; main() must still log at INFO.
    code = (
        "import asyncio, logging\n"
        "logging.basicConfig(level=logging.WARNING)\n"
        "asyncio.run = lambda coroutine: coroutine.close()\n"
        "from finbot.__main__ import main\n"
        "main()\n"
    )
    env = {k: v for k, v in os.environ.items() if not k.startswith("ANTHROPIC_")}
    env.update(PYTHONPATH=str(APP_DIR), BOT_TOKEN="1:x", OWNER_ID="1", PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        timeout=60,
    )
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == 0, stderr
    assert "AI input: off" in stderr
