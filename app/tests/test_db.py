import sqlite3
import threading
import time
from contextlib import closing
from importlib.resources import files
from typing import Any

import pytest

from finbot.db import connect

EXPENSE = [
    "Groceries",
    "Eating out",
    "Transport",
    "Housing",
    "Utilities",
    "Health",
    "Shopping",
    "Entertainment",
    "Travel",
    "Subscriptions",
    "Gifts",
    "Other",
]
INCOME = ["Salary", "Freelance", "Other income"]


def test_fresh_database_is_at_version_4_with_expected_tables(conn):
    assert conn.execute("PRAGMA user_version").fetchone()[0] == 4
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    assert {row["name"] for row in rows} == {
        "categories",
        "keywords",
        "rates",
        "pots",
        "entries",
        "meta",
        "budgets",
        "drafts",
    }


@pytest.mark.parametrize(("kind", "names"), [("expense", EXPENSE), ("income", INCOME)])
def test_default_categories_are_in_spec_order(conn, kind, names):
    rows = conn.execute(
        "SELECT name, position FROM categories WHERE kind = ? ORDER BY position", (kind,)
    ).fetchall()
    assert [(row["name"], row["position"]) for row in rows] == [
        (name, position) for position, name in enumerate(names, start=1)
    ]


def test_second_connect_keeps_fifteen_categories(tmp_path):
    path = tmp_path / "t.db"
    connect(path).close()
    with closing(connect(path)) as conn:
        assert conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 15
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4


def test_connect_creates_parent_directory(tmp_path):
    path = tmp_path / "data" / "finbot.db"
    connect(path).close()
    assert path.is_file()


def test_foreign_keys_are_on(conn):
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_journal_mode_is_wal(conn):
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"


def test_rows_are_addressable_by_column_name(conn):
    assert conn.execute("SELECT 1 AS n").fetchone()["n"] == 1


def test_zero_amount_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        conn.execute(
            "INSERT INTO entries (kind, amount_cents, currency, category_id, occurred_on) "
            "VALUES ('expense', 0, 'EUR', 1, '2026-10-31')"
        )


def test_save_without_pot_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        conn.execute(
            "INSERT INTO entries (kind, amount_cents, currency, occurred_on) "
            "VALUES ('save', 500, 'EUR', '2026-10-31')"
        )


def test_failed_schema_leaves_nothing_behind(tmp_path):
    path = tmp_path / "t.db"
    # A conflicting table makes the schema script fail half-way, after several CREATEs.
    with closing(sqlite3.connect(path)) as raw:
        raw.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        raw.commit()
    with pytest.raises(sqlite3.OperationalError):
        connect(path)
    with closing(sqlite3.connect(path)) as raw:
        raw.execute("DROP TABLE meta")
        raw.commit()
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4
        assert conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 15


def _make_version_1_database(path):
    """The database as it is on the server: schema.sql applied, user_version 1, real rows."""
    schema = (files("finbot") / "schema.sql").read_text(encoding="utf-8")
    with closing(sqlite3.connect(path)) as raw:
        raw.execute("PRAGMA journal_mode = WAL")
        raw.executescript(schema)
        raw.execute("INSERT INTO pots (id, name, goal_cents) VALUES (1, 'emergency', 1000000)")
        raw.execute(
            "INSERT INTO entries (kind, amount_cents, currency, eur_cents, pot_id, occurred_on)"
            " VALUES ('save', 30000, 'EUR', 30000, 1, '2026-10-31')"
        )
        raw.execute(
            "INSERT INTO entries (kind, amount_cents, currency, eur_cents, category_id,"
            " keyword, note, occurred_on)"
            " VALUES ('expense', 2500, 'EUR', 2500, 2, 'coffee', 'coffee', '2026-10-31')"
        )
        raw.execute("PRAGMA user_version = 1")
        raw.commit()


def _pot_columns(conn) -> list[str]:
    return [row["name"] for row in conn.execute("PRAGMA table_info(pots)")]


def test_fresh_database_has_the_goal_month_column(conn):
    assert _pot_columns(conn) == ["id", "name", "goal_cents", "goal_month"]


def test_version_1_database_is_upgraded_with_data_intact(tmp_path):
    path = tmp_path / "t.db"
    _make_version_1_database(path)
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4
        assert _pot_columns(conn) == ["id", "name", "goal_cents", "goal_month"]
        pots = conn.execute("SELECT id, name, goal_cents, goal_month FROM pots").fetchall()
        assert [tuple(row) for row in pots] == [(1, "emergency", 1_000_000, None)]
        entries = conn.execute(
            "SELECT id, kind, amount_cents, pot_id, category_id, keyword FROM entries ORDER BY id"
        ).fetchall()
        assert [tuple(row) for row in entries] == [
            (1, "save", 30000, 1, None, ""),
            (2, "expense", 2500, None, 2, "coffee"),
        ]
        assert conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 15


def test_connecting_again_after_the_upgrade_changes_nothing(tmp_path):
    path = tmp_path / "t.db"
    _make_version_1_database(path)
    with closing(connect(path)) as conn, conn:
        conn.execute("UPDATE pots SET goal_month = '2027-12' WHERE id = 1")
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4
        assert _pot_columns(conn) == ["id", "name", "goal_cents", "goal_month"]
        assert conn.execute("SELECT goal_month FROM pots WHERE id = 1").fetchone()[0] == "2027-12"
        assert conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 2


def test_failed_upgrade_stays_at_version_1_with_data_intact(tmp_path):
    path = tmp_path / "t.db"
    _make_version_1_database(path)
    with closing(sqlite3.connect(path)) as raw:
        # The column is already there but the version says 1, so the ALTER must fail.
        raw.execute("ALTER TABLE pots ADD COLUMN goal_month TEXT")
        raw.commit()
    with pytest.raises(sqlite3.OperationalError, match="duplicate column name"):
        connect(path)
    with closing(sqlite3.connect(path)) as raw:
        assert raw.execute("PRAGMA user_version").fetchone()[0] == 1
        assert raw.execute("SELECT name, goal_cents FROM pots").fetchall() == [
            ("emergency", 1_000_000)
        ]
        assert raw.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 2


def test_connection_that_finds_version_2_inside_the_lock_does_nothing(tmp_path):
    path = tmp_path / "t.db"
    _make_version_1_database(path)
    holding_the_lock = threading.Event()

    def upgrade_in_another_process() -> None:
        with closing(sqlite3.connect(path, isolation_level=None)) as other:
            other.execute("BEGIN IMMEDIATE")
            holding_the_lock.set()
            time.sleep(0.3)
            other.execute("ALTER TABLE pots ADD COLUMN goal_month TEXT")
            other.execute("PRAGMA user_version = 2")
            other.execute("COMMIT")

    upgrader = threading.Thread(target=upgrade_in_another_process)
    upgrader.start()
    assert holding_the_lock.wait(timeout=5)
    # connect() reads version 1 here, then has to wait for the lock and find version 2 inside it.
    # It skips that step (no duplicate column) and goes on to the 2 -> 3 step.
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4
        assert _pot_columns(conn) == ["id", "name", "goal_cents", "goal_month"]
    upgrader.join()


def _make_version_2_database(path):
    """The live server database: version 1 plus the goal_month step, user_version 2, real rows."""
    _make_version_1_database(path)
    with closing(sqlite3.connect(path)) as raw:
        raw.execute("ALTER TABLE pots ADD COLUMN goal_month TEXT")
        raw.execute("UPDATE pots SET goal_month = '2027-12' WHERE id = 1")
        raw.execute("PRAGMA user_version = 2")
        raw.commit()


def _budget_columns(conn) -> list[tuple[str, str, int]]:
    return [
        (row["name"], row["type"], row["notnull"])
        for row in conn.execute("PRAGMA table_info(budgets)")
    ]


def test_version_2_database_gets_the_budgets_table_with_data_intact(tmp_path):
    path = tmp_path / "t.db"
    _make_version_2_database(path)
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4
        assert _budget_columns(conn) == [
            ("category_id", "INTEGER", 0),
            ("amount_cents", "INTEGER", 1),
        ]
        assert conn.execute("SELECT COUNT(*) FROM budgets").fetchone()[0] == 0
        pots = conn.execute("SELECT id, name, goal_cents, goal_month FROM pots").fetchall()
        assert [tuple(row) for row in pots] == [(1, "emergency", 1_000_000, "2027-12")]
        entries = conn.execute("SELECT id, kind, amount_cents FROM entries ORDER BY id").fetchall()
        assert [tuple(row) for row in entries] == [(1, "save", 30000), (2, "expense", 2500)]
        assert conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 15


def test_connecting_again_after_the_budgets_upgrade_changes_nothing(tmp_path):
    path = tmp_path / "t.db"
    _make_version_2_database(path)
    with closing(connect(path)) as conn, conn:
        conn.execute("INSERT INTO budgets (category_id, amount_cents) VALUES (4, 85000)")
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4
        rows = conn.execute("SELECT category_id, amount_cents FROM budgets").fetchall()
        assert [tuple(row) for row in rows] == [(4, 85000)]


def test_failed_budgets_upgrade_stays_at_version_2_with_data_intact(tmp_path):
    path = tmp_path / "t.db"
    _make_version_2_database(path)
    with closing(sqlite3.connect(path)) as raw:
        # The table is already there but the version says 2, so the CREATE must fail.
        raw.execute("CREATE TABLE budgets (category_id INTEGER)")
        raw.commit()
    with pytest.raises(sqlite3.OperationalError, match="already exists"):
        connect(path)
    with closing(sqlite3.connect(path)) as raw:
        assert raw.execute("PRAGMA user_version").fetchone()[0] == 2
        assert raw.execute("SELECT name, goal_month FROM pots").fetchall() == [
            ("emergency", "2027-12")
        ]
        assert raw.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 2


class _FailsSettingVersion3(sqlite3.Connection):
    """Lets the 2 -> 3 step run its CREATE TABLE, then fails on the version bump."""

    def execute(self, sql: str, /, *args: Any) -> sqlite3.Cursor:
        if sql == "PRAGMA user_version = 3":
            raise sqlite3.OperationalError("disk I/O error")
        return super().execute(sql, *args)


def test_budgets_upgrade_that_fails_after_creating_the_table_leaves_nothing_behind(
    tmp_path, monkeypatch
):
    path = tmp_path / "t.db"
    _make_version_2_database(path)
    real_connect = sqlite3.connect
    with monkeypatch.context() as patched:
        patched.setattr(
            sqlite3, "connect", lambda p: real_connect(p, factory=_FailsSettingVersion3)
        )
        with pytest.raises(sqlite3.OperationalError, match="disk I/O error"):
            connect(path)
    with closing(sqlite3.connect(path)) as raw:
        assert raw.execute("PRAGMA user_version").fetchone()[0] == 2
        tables = raw.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        assert "budgets" not in {row[0] for row in tables}
        assert raw.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 2
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4


def test_connection_that_finds_version_3_inside_the_lock_does_nothing(tmp_path):
    path = tmp_path / "t.db"
    _make_version_2_database(path)
    holding_the_lock = threading.Event()

    def upgrade_in_another_process() -> None:
        with closing(sqlite3.connect(path, isolation_level=None)) as other:
            other.execute("BEGIN IMMEDIATE")
            holding_the_lock.set()
            time.sleep(0.3)
            other.execute(
                "CREATE TABLE budgets (category_id INTEGER PRIMARY KEY REFERENCES categories(id),"
                " amount_cents INTEGER NOT NULL CHECK (amount_cents > 0))"
            )
            other.execute("PRAGMA user_version = 3")
            other.execute("COMMIT")

    upgrader = threading.Thread(target=upgrade_in_another_process)
    upgrader.start()
    assert holding_the_lock.wait(timeout=5)
    # connect() reads version 2 here, then has to wait for the lock and find version 3 inside it.
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4
        assert _budget_columns(conn) == [
            ("category_id", "INTEGER", 0),
            ("amount_cents", "INTEGER", 1),
        ]
    upgrader.join()


def test_budget_amount_must_be_positive(conn):
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        conn.execute("INSERT INTO budgets (category_id, amount_cents) VALUES (1, 0)")


def test_a_category_has_one_budget(conn):
    conn.execute("INSERT INTO budgets (category_id, amount_cents) VALUES (1, 100)")
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed"):
        conn.execute("INSERT INTO budgets (category_id, amount_cents) VALUES (1, 200)")


def test_a_budget_needs_an_existing_category(conn):
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        conn.execute("INSERT INTO budgets (category_id, amount_cents) VALUES (999, 100)")


def _make_version_3_database(path):
    """The database after the budgets step: version 3, with real rows in every table."""
    _make_version_2_database(path)
    with closing(sqlite3.connect(path)) as raw:
        raw.execute(
            "CREATE TABLE budgets (category_id INTEGER PRIMARY KEY REFERENCES categories(id),"
            " amount_cents INTEGER NOT NULL CHECK (amount_cents > 0))"
        )
        raw.execute("INSERT INTO budgets (category_id, amount_cents) VALUES (4, 85000)")
        raw.execute("PRAGMA user_version = 3")
        raw.commit()


def _drafts_columns(conn) -> list[tuple[str, str, int]]:
    return [
        (row["name"], row["type"], row["notnull"])
        for row in conn.execute("PRAGMA table_info(drafts)")
    ]


def test_version_3_database_gets_the_drafts_table_with_data_intact(tmp_path):
    path = tmp_path / "t.db"
    _make_version_3_database(path)
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4
        assert _drafts_columns(conn) == [
            ("id", "INTEGER", 0),
            ("source", "TEXT", 1),
            ("entries", "TEXT", 1),
            ("status", "TEXT", 1),
            ("created_at", "TEXT", 1),
            ("message_id", "INTEGER", 0),
        ]
        assert conn.execute("SELECT COUNT(*) FROM drafts").fetchone()[0] == 0
        rows = conn.execute("SELECT category_id, amount_cents FROM budgets").fetchall()
        assert [tuple(row) for row in rows] == [(4, 85000)]
        pots = conn.execute("SELECT id, name, goal_cents, goal_month FROM pots").fetchall()
        assert [tuple(row) for row in pots] == [(1, "emergency", 1_000_000, "2027-12")]
        entries = conn.execute("SELECT id, kind, amount_cents FROM entries ORDER BY id").fetchall()
        assert [tuple(row) for row in entries] == [(1, "save", 30000), (2, "expense", 2500)]


def test_connection_that_finds_version_4_inside_the_lock_does_nothing(tmp_path):
    path = tmp_path / "t.db"
    _make_version_3_database(path)
    holding_the_lock = threading.Event()

    def upgrade_in_another_process() -> None:
        with closing(sqlite3.connect(path, isolation_level=None)) as other:
            other.execute("BEGIN IMMEDIATE")
            holding_the_lock.set()
            time.sleep(0.3)
            other.execute(
                "CREATE TABLE drafts (id INTEGER PRIMARY KEY,"
                " source TEXT NOT NULL CHECK (source IN ('text','photo')),"
                " entries TEXT NOT NULL,"
                " status TEXT NOT NULL DEFAULT 'open'"
                " CHECK (status IN ('open','saved','cancelled','replaced','expired')),"
                " created_at TEXT NOT NULL, message_id INTEGER)"
            )
            other.execute("PRAGMA user_version = 4")
            other.execute("COMMIT")

    upgrader = threading.Thread(target=upgrade_in_another_process)
    upgrader.start()
    assert holding_the_lock.wait(timeout=5)
    # connect() reads version 3 here, then has to wait for the lock and find version 4 inside it.
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 4
        assert _drafts_columns(conn)[0] == ("id", "INTEGER", 0)
    upgrader.join()
