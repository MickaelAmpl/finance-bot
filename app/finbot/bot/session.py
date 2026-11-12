import logging
import re
import socket

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

_ANTHROPIC_KEY = re.compile(r"sk-ant-[A-Za-z0-9_-]+")


class _SecretFilter(logging.Filter):
    def __init__(self, secrets: list[str]) -> None:
        super().__init__()
        # Longest first, so a secret that contains a shorter one is masked whole.
        self._secrets = sorted(secrets, key=len, reverse=True)

    def _mask(self, text: str) -> str:
        for secret in self._secrets:
            text = text.replace(secret, "***")
        return _ANTHROPIC_KEY.sub("***", text)

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self._mask(record.getMessage())
        record.args = None
        if record.exc_info:
            traceback_text = logging.Formatter().formatException(record.exc_info)
            record.exc_text = self._mask(traceback_text)
        if record.stack_info:
            record.stack_info = self._mask(record.stack_info)
        return True


def build_bot(token: str) -> Bot:
    # IPv6 to api.telegram.org stalls on the VPS server (see _config/telegram-rules.md).
    session = AiohttpSession()
    session._connector_init["family"] = socket.AF_INET
    return Bot(token, session=session)


def redact_token_in_logs(*secrets: str | None) -> None:
    # Masks every secret passed in (bot token, Anthropic key, or both). Network errors
    # carry the request URL, and the URL carries the token. Empty or blank secrets are
    # skipped: "abc".replace("", "***") would garble the text.
    secret_filter = _SecretFilter([s for s in secrets if s and s.strip()])
    for handler in logging.getLogger().handlers:
        handler.addFilter(secret_filter)
