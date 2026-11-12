from pathlib import Path

import pytest

from finbot.config import ConfigError, load_settings, read_env_file


def test_load_settings_reads_keys_and_defaults():
    s = load_settings({"BOT_TOKEN": "123:abc", "OWNER_ID": "42"})
    assert (s.bot_token, s.owner_id) == ("123:abc", 42)
    assert s.db_path == Path("data/finbot.db") and s.backup_dir == Path("data/backups")


def test_missing_token_raises():
    with pytest.raises(ConfigError, match="BOT_TOKEN"):
        load_settings({"OWNER_ID": "42"})


def test_missing_keys_show_an_example():
    with pytest.raises(ConfigError, match="BOT_TOKEN is missing.*e.g. BOT_TOKEN="):
        load_settings({"OWNER_ID": "42"})
    with pytest.raises(ConfigError, match="OWNER_ID is missing.*e.g. OWNER_ID=123456789"):
        load_settings({"BOT_TOKEN": "x"})


def test_owner_id_must_be_integer():
    with pytest.raises(ConfigError, match="OWNER_ID"):
        load_settings({"BOT_TOKEN": "x", "OWNER_ID": "abc"})


@pytest.mark.parametrize("key", ["BOT_TOKEN", "OWNER_ID"])
def test_empty_required_value_counts_as_missing(key):
    env = {"BOT_TOKEN": "123:abc", "OWNER_ID": "42", key: ""}
    with pytest.raises(ConfigError, match=key):
        load_settings(env)


def test_optional_paths_can_be_overridden():
    s = load_settings(
        {"BOT_TOKEN": "x", "OWNER_ID": "42", "DB_PATH": "custom/f.db", "BACKUP_DIR": "custom/b"}
    )
    assert (s.db_path, s.backup_dir) == (Path("custom/f.db"), Path("custom/b"))


def test_empty_optional_path_uses_default():
    s = load_settings({"BOT_TOKEN": "x", "OWNER_ID": "42", "DB_PATH": "", "BACKUP_DIR": ""})
    assert (s.db_path, s.backup_dir) == (Path("data/finbot.db"), Path("data/backups"))


def test_read_env_file_skips_comments_and_blanks(tmp_path):
    p = tmp_path / ".env"
    p.write_text("A=1\n# note\n\nB = two \n")
    assert read_env_file(p) == {"A": "1", "B": "two"}


def test_anthropic_key_is_read_when_set():
    s = load_settings({"BOT_TOKEN": "x", "OWNER_ID": "42", "ANTHROPIC_API_KEY": "sk-ant-x"})
    assert s.anthropic_api_key == "sk-ant-x"


@pytest.mark.parametrize("value", [None, "", "   "])
def test_missing_or_blank_anthropic_key_is_none(value):
    env = {"BOT_TOKEN": "x", "OWNER_ID": "42"}
    if value is not None:
        env["ANTHROPIC_API_KEY"] = value
    assert load_settings(env).anthropic_api_key is None


def test_secrets_are_hidden_in_repr():
    s = load_settings({"BOT_TOKEN": "123:abc", "OWNER_ID": "42", "ANTHROPIC_API_KEY": "sk-ant-x"})
    text = repr(s)
    assert "123:abc" not in text
    assert "sk-ant-x" not in text
