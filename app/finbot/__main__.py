import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import anthropic
from anthropic import AsyncAnthropic

from finbot.bot.ai_handlers import AiState
from finbot.bot.app import build_dispatcher
from finbot.bot.session import build_bot, redact_token_in_logs
from finbot.config import TZ, Settings, load_settings, read_env_file
from finbot.db import connect

ENV_FILE = Path(".env")
SDK_LOGGERS = ("anthropic", "httpx2", "httpcore2")


def quiet_sdk_loggers() -> None:
    # ANTHROPIC_LOG=debug would otherwise print request bodies, including the user's text.
    for name in SDK_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)


def build_ai(settings: Settings) -> AiState | None:
    if not settings.anthropic_api_key:
        return None
    client = AsyncAnthropic(
        api_key=settings.anthropic_api_key,
        base_url="https://api.anthropic.com",
        timeout=anthropic.Timeout(45.0, connect=5.0),
        max_retries=2,
    )
    return AiState(client=client)


def main() -> None:
    logging.basicConfig(level=logging.INFO, force=True)
    settings = load_settings(
        {**read_env_file(ENV_FILE), **os.environ} if ENV_FILE.exists() else dict(os.environ)
    )
    redact_token_in_logs(settings.bot_token, settings.anthropic_api_key)
    quiet_sdk_loggers()
    ai = build_ai(settings)
    logging.info("AI input: %s", "on" if ai else "off")
    conn = connect(settings.db_path)
    bot = build_bot(settings.bot_token)
    dp = build_dispatcher(conn, settings.owner_id, lambda: datetime.now(TZ).date(), ai)
    if ai is not None:
        dp.shutdown.register(ai.client.close)
    try:
        asyncio.run(dp.start_polling(bot))
    except Exception:
        logging.exception("bot stopped")
        sys.exit(1)


if __name__ == "__main__":
    main()
