import sqlite3
import unicodedata
from dataclasses import dataclass

MAX_NAME_LENGTH = 30
MAX_PER_KIND = 30
_UNCATEGORIZED = "uncategorized"  # the month report's label for entries without a category


class CategoryError(ValueError):
    """The message is shown to the user as is."""


@dataclass(frozen=True)
class Category:
    id: int
    name: str
    kind: str


def list_categories(conn: sqlite3.Connection, kind: str) -> list[Category]:
    rows = conn.execute(
        "SELECT id, name, kind FROM categories WHERE kind = ? ORDER BY position", (kind,)
    ).fetchall()
    return [Category(id=row["id"], name=row["name"], kind=row["kind"]) for row in rows]


def get_category(conn: sqlite3.Connection, category_id: int) -> Category:
    row = conn.execute(
        "SELECT id, name, kind FROM categories WHERE id = ?", (category_id,)
    ).fetchone()
    if row is None:
        raise LookupError(f"no category with id {category_id}")
    return Category(id=row["id"], name=row["name"], kind=row["kind"])


def category_for_keyword(conn: sqlite3.Connection, word: str, kind: str) -> Category | None:
    row = conn.execute(
        "SELECT c.id, c.name, c.kind FROM keywords k JOIN categories c ON c.id = k.category_id "
        "WHERE k.word = ? AND c.kind = ?",
        (word, kind),
    ).fetchone()
    if row is None:
        return None
    return Category(id=row["id"], name=row["name"], kind=row["kind"])


def remember_keyword(conn: sqlite3.Connection, word: str, category_id: int) -> None:
    with conn:
        conn.execute(
            "INSERT INTO keywords (word, category_id) VALUES (?, ?) "
            "ON CONFLICT(word) DO UPDATE SET category_id = excluded.category_id",
            (word, category_id),
        )


def is_valid_name(name: str) -> bool:
    name = _clean_name(name)
    return (
        1 <= len(name) <= MAX_NAME_LENGTH
        and any(ch.isalpha() for ch in name)
        and not name.startswith("/")
        and name.casefold() != _UNCATEGORIZED
    )


def find_category(conn: sqlite3.Connection, name: str) -> Category | None:
    # Compared in Python: SQLite folds the case of ASCII letters only.
    wanted = _clean_name(name).casefold()
    for row in conn.execute("SELECT id, name, kind FROM categories ORDER BY id"):
        if row["name"].casefold() == wanted:
            return Category(id=row["id"], name=row["name"], kind=row["kind"])
    return None


def add_category(conn: sqlite3.Connection, name: str, kind: str) -> Category:
    name = _clean_name(name)
    with conn:
        _refuse_taken_name(conn, name, None)
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM categories WHERE kind = ?", (kind,)
        ).fetchone()
        if row["n"] >= MAX_PER_KIND:
            raise CategoryError(
                f"Up to {MAX_PER_KIND} {kind} categories. Rename one instead: "
                "/category rename Old New"
            )
        cursor = conn.execute(
            "INSERT INTO categories (name, kind, position) "
            "SELECT ?, ?, COALESCE(MAX(position), 0) + 1 FROM categories WHERE kind = ?",
            (name, kind, kind),
        )
    assert cursor.lastrowid is not None
    return Category(id=cursor.lastrowid, name=name, kind=kind)


def rename_category(conn: sqlite3.Connection, category_id: int, name: str) -> Category:
    name = _clean_name(name)
    with conn:
        _refuse_taken_name(conn, name, category_id)
        conn.execute("UPDATE categories SET name = ? WHERE id = ?", (name, category_id))
        return get_category(conn, category_id)


def _refuse_taken_name(conn: sqlite3.Connection, name: str, own_id: int | None) -> None:
    # A category may change only the case of its own name, so its own id does not count.
    taken = find_category(conn, name)
    if taken is not None and taken.id != own_id:
        raise CategoryError(f"There is already a category {taken.name}.")


def _clean_name(name: str) -> str:
    """Drop invisible format characters (zero-width, bidi marks), compose, trim, collapse spaces."""
    visible = "".join(ch for ch in name if unicodedata.category(ch) != "Cf")
    return " ".join(unicodedata.normalize("NFC", visible).split())
