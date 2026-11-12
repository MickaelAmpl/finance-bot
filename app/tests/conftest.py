import socket
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from finbot import db

_LOCAL_HOSTS = ("127.0.0.1", "::1", "localhost")
_ANTHROPIC_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_LOG",
    "ANTHROPIC_BASE_URL",
)
_real_connect = socket.socket.connect
_real_connect_ex = socket.socket.connect_ex
_real_getaddrinfo = socket.getaddrinfo


def _guard(sock: socket.socket, address: Any) -> None:
    # AF_UNIX is used by asyncio's event loop internals; only local TCP is allowed.
    if sock.family == socket.AF_UNIX:
        return
    host = address[0] if isinstance(address, tuple) else address
    if host not in _LOCAL_HOSTS:
        raise RuntimeError("network blocked in tests")


def _guarded_connect(self: socket.socket, address: Any) -> None:
    _guard(self, address)
    _real_connect(self, address)


def _guarded_connect_ex(self: socket.socket, address: Any) -> int:
    _guard(self, address)
    return _real_connect_ex(self, address)


def _guarded_getaddrinfo(host: Any, *args: Any, **kwargs: Any) -> Any:
    if host is not None and host not in _LOCAL_HOSTS:
        raise RuntimeError("network blocked in tests")
    return _real_getaddrinfo(host, *args, **kwargs)


@pytest.fixture(autouse=True)
def _isolated_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _ANTHROPIC_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(socket.socket, "connect", _guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", _guarded_connect_ex)
    monkeypatch.setattr(socket, "getaddrinfo", _guarded_getaddrinfo)


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    c = db.connect(tmp_path / "t.db")
    yield c
    c.close()
