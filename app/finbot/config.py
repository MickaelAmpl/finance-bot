from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo

TZ: ZoneInfo = ZoneInfo("Europe/Vienna")


class ConfigError(Exception):
    """A required setting is missing or malformed."""


@dataclass(frozen=True)
class Settings:
    bot_token: str = field(repr=False)
    owner_id: int
    db_path: Path
    backup_dir: Path
    anthropic_api_key: str | None = field(default=None, repr=False)


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def _required(env: Mapping[str, str], key: str, example: str) -> str:
    value = env.get(key)
    if not value:
        raise ConfigError(f"{key} is missing. Add it to .env, e.g. {example}")
    return value


def load_settings(env: Mapping[str, str]) -> Settings:
    bot_token = _required(env, "BOT_TOKEN", "BOT_TOKEN=<token from @BotFather>")
    owner_raw = _required(env, "OWNER_ID", "OWNER_ID=123456789")
    try:
        owner_id = int(owner_raw)
    except ValueError:
        raise ConfigError("OWNER_ID must be a number, for example OWNER_ID=123456789") from None
    return Settings(
        bot_token=bot_token,
        owner_id=owner_id,
        db_path=Path(env.get("DB_PATH") or "data/finbot.db"),
        backup_dir=Path(env.get("BACKUP_DIR") or "data/backups"),
        anthropic_api_key=(env.get("ANTHROPIC_API_KEY") or "").strip() or None,
    )
