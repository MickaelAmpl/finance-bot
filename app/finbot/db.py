import sqlite3
from importlib.resources import files
from pathlib import Path


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    if conn.execute("PRAGMA user_version").fetchone()[0] == 0:
        _apply_schema(conn)
    if conn.execute("PRAGMA user_version").fetchone()[0] == 1:
        _add_goal_month(conn)
    if conn.execute("PRAGMA user_version").fetchone()[0] == 2:
        _add_budgets(conn)
    if conn.execute("PRAGMA user_version").fetchone()[0] == 3:
        _add_drafts(conn)
    return conn


def _apply_schema(conn: sqlite3.Connection) -> None:
    # executescript() runs its script outside any transaction, so BEGIN/COMMIT go here.
    # `with conn` rolls the whole schema back if a statement fails half-way.
    schema = (files("finbot") / "schema.sql").read_text(encoding="utf-8")
    with conn:
        conn.executescript(f"BEGIN;\n{schema}\nPRAGMA user_version = 1;\nCOMMIT;")


def _add_goal_month(conn: sqlite3.Connection) -> None:
    # Version 1 -> 2. The bot and the daily job both call connect(): BEGIN IMMEDIATE takes the
    # write lock first, then the version is read again, so the loser of a race finds 2 and skips.
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute("PRAGMA user_version").fetchone()[0] == 1:
            conn.execute("ALTER TABLE pots ADD COLUMN goal_month TEXT")
            conn.execute("PRAGMA user_version = 2")


def _add_budgets(conn: sqlite3.Connection) -> None:
    # Version 2 -> 3, locked and re-checked like the step above.
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute("PRAGMA user_version").fetchone()[0] == 2:
            conn.execute(
                "CREATE TABLE budgets (category_id INTEGER PRIMARY KEY REFERENCES categories(id),"
                " amount_cents INTEGER NOT NULL CHECK (amount_cents > 0))"
            )
            conn.execute("PRAGMA user_version = 3")


def _add_drafts(conn: sqlite3.Connection) -> None:
    # Version 3 -> 4, locked and re-checked like the steps above.
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute("PRAGMA user_version").fetchone()[0] == 3:
            conn.execute(
                "CREATE TABLE drafts (id INTEGER PRIMARY KEY,"
                " source TEXT NOT NULL CHECK (source IN ('text','photo')),"
                " entries TEXT NOT NULL,"
                " status TEXT NOT NULL DEFAULT 'open'"
                " CHECK (status IN ('open','saved','cancelled','replaced','expired')),"
                " created_at TEXT NOT NULL, message_id INTEGER)"
            )
            conn.execute("PRAGMA user_version = 4")
