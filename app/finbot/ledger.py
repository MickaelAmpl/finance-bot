import sqlite3
from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from finbot.categories import category_for_keyword, remember_keyword
from finbot.money import to_eur
from finbot.parser import Entry
from finbot.rates import rate_on
from finbot.savings import SavingsError, get_pot

_SELECT = (
    "SELECT e.id, e.kind, e.amount_cents, e.currency, e.rate, e.eur_cents, e.keyword, e.note,"
    " e.occurred_on, c.name AS category, p.name AS pot"
    " FROM entries e"
    " LEFT JOIN categories c ON c.id = e.category_id"
    " LEFT JOIN pots p ON p.id = e.pot_id"
)
# Pot moves (save, take) are not part of a month's expenses and incomes.
_CLEARABLE = "deleted_at IS NULL AND kind IN ('expense', 'income') AND occurred_on BETWEEN ? AND ?"


@dataclass(frozen=True)
class Record:
    id: int
    kind: str
    amount_cents: int
    currency: str
    rate: Decimal | None
    eur_cents: int | None
    category: str | None
    pot: str | None
    keyword: str
    note: str
    on: date

    @property
    def pending(self) -> bool:
        return self.eur_cents is None


def add_transaction(conn: sqlite3.Connection, entry: Entry) -> Record:
    if entry.kind not in ("expense", "income"):
        raise ValueError("add_transaction takes expense or income entries")
    category = category_for_keyword(conn, entry.keyword, entry.kind)
    with conn:
        entry_id = insert_transaction(conn, entry, None if category is None else category.id)
    return _record(conn.execute(_SELECT + " WHERE e.id = ?", (entry_id,)).fetchone())


def insert_transaction(conn: sqlite3.Connection, entry: Entry, category_id: int | None) -> int:
    """Insert one entry with its rate and EUR amount. The caller owns the transaction."""
    rate: str | None = None
    eur_cents: int | None = None
    if entry.currency == "EUR":
        eur_cents = entry.amount_cents
    else:
        found = rate_on(conn, entry.currency, entry.on)
        if found is not None:
            rate = str(found)
            eur_cents = to_eur(entry.amount_cents, found)
    cur = conn.execute(
        "INSERT INTO entries (kind, amount_cents, currency, rate, eur_cents, category_id,"
        " keyword, note, occurred_on) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            entry.kind,
            entry.amount_cents,
            entry.currency,
            rate,
            eur_cents,
            category_id,
            entry.keyword,
            entry.note,
            entry.on.isoformat(),
        ),
    )
    assert cur.lastrowid is not None
    return cur.lastrowid


def get_record(conn: sqlite3.Connection, entry_id: int) -> Record | None:
    row = conn.execute(_SELECT + " WHERE e.id = ? AND e.deleted_at IS NULL", (entry_id,)).fetchone()
    return None if row is None else _record(row)


def set_category(conn: sqlite3.Connection, entry_id: int, category_id: int) -> Record:
    entry = get_record(conn, entry_id)
    if entry is None:
        raise LookupError(f"no entry with id {entry_id}")
    with conn:
        conn.execute("UPDATE entries SET category_id = ? WHERE id = ?", (category_id, entry_id))
    if entry.keyword:
        remember_keyword(conn, entry.keyword, category_id)
    return _record(conn.execute(_SELECT + " WHERE e.id = ?", (entry_id,)).fetchone())


def delete_entry(conn: sqlite3.Connection, entry_id: int) -> Record | None:
    # The pot check and the delete share one transaction, so a refused delete writes nothing.
    with conn:
        entry = get_record(conn, entry_id)
        if entry is None:
            return None
        if entry.kind == "save" and entry.pot is not None:
            pot = get_pot(conn, entry.pot)
            if pot is not None and pot.total_cents - entry.amount_cents < 0:
                raise SavingsError(
                    f"{entry.pot.capitalize()} would go below zero. Delete the later take first."
                )
        conn.execute(
            "UPDATE entries SET deleted_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') WHERE id = ?",
            (entry_id,),
        )
    return entry


def clearable_summary(conn: sqlite3.Connection, year: int, month: int) -> tuple[int, int]:
    """How many expenses and incomes the month has, and the highest id among them (0 if none)."""
    row = conn.execute(
        "SELECT COUNT(*), COALESCE(MAX(id), 0) FROM entries WHERE " + _CLEARABLE,
        _month_bounds(year, month),
    ).fetchone()
    return row[0], row[1]


def clear_month(
    conn: sqlite3.Connection, year: int, month: int, count: int, last_id: int
) -> int | None:
    """Soft-delete the expenses and incomes that were shown: `count` of them, the newest `last_id`.

    Returns how many were deleted, or None (nothing written) when the month no longer has
    exactly that set. Ids only grow, so any add, or an undo followed by a new entry, changes it.
    """
    with conn:
        # The write lock first, so the recount and the delete cannot be split by another writer.
        conn.execute("BEGIN IMMEDIATE")
        if clearable_summary(conn, year, month) != (count, last_id):
            return None
        cursor = conn.execute(
            "UPDATE entries SET deleted_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') WHERE "
            + _CLEARABLE
            + " AND id <= ?",
            (*_month_bounds(year, month), last_id),
        )
    return cursor.rowcount


def undo_last(conn: sqlite3.Connection) -> Record | None:
    row = conn.execute(
        "SELECT id FROM entries WHERE deleted_at IS NULL ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return None if row is None else delete_entry(conn, row["id"])


def last_records(conn: sqlite3.Connection, limit: int = 10) -> list[Record]:
    rows = conn.execute(
        _SELECT + " WHERE e.deleted_at IS NULL ORDER BY e.id DESC LIMIT ?", (limit,)
    ).fetchall()
    return [_record(row) for row in rows]


def records_between(conn: sqlite3.Connection, start: date, end: date) -> list[Record]:
    rows = conn.execute(
        _SELECT + " WHERE e.deleted_at IS NULL AND e.occurred_on BETWEEN ? AND ?"
        " ORDER BY e.occurred_on, e.id",
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    return [_record(row) for row in rows]


def all_records(conn: sqlite3.Connection) -> list[Record]:
    rows = conn.execute(
        _SELECT + " WHERE e.deleted_at IS NULL ORDER BY e.occurred_on, e.id"
    ).fetchall()
    return [_record(row) for row in rows]


def _month_bounds(year: int, month: int) -> tuple[str, str]:
    first = date(year, month, 1)
    last = date(year, month, monthrange(year, month)[1])
    return first.isoformat(), last.isoformat()


def _record(row: sqlite3.Row) -> Record:
    return Record(
        id=row["id"],
        kind=row["kind"],
        amount_cents=row["amount_cents"],
        currency=row["currency"],
        rate=None if row["rate"] is None else Decimal(row["rate"]),
        eur_cents=row["eur_cents"],
        category=row["category"],
        pot=row["pot"],
        keyword=row["keyword"],
        note=row["note"],
        on=date.fromisoformat(row["occurred_on"]),
    )
