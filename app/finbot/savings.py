import sqlite3
from dataclasses import dataclass, replace
from datetime import date

from finbot.money import format_cents
from finbot.parser import Entry


class SavingsError(ValueError):
    """The message is shown to the user as is."""


@dataclass(frozen=True)
class Pot:
    id: int
    name: str
    total_cents: int
    goal_cents: int | None
    goal_month: str | None = None  # YYYY-MM


@dataclass(frozen=True)
class PotMove:
    entry_id: int
    kind: str
    amount_cents: int
    on: date


# The LEFT JOIN condition keeps soft-deleted moves out of the total.
_POTS = (
    "SELECT p.id, p.name, p.goal_cents, p.goal_month, COALESCE(SUM(CASE e.kind"
    " WHEN 'save' THEN e.amount_cents WHEN 'take' THEN -e.amount_cents END), 0) AS total_cents"
    " FROM pots p LEFT JOIN entries e ON e.pot_id = p.id AND e.deleted_at IS NULL"
)


def apply_pot_entry(conn: sqlite3.Connection, entry: Entry) -> tuple[int, Pot]:
    # One transaction: a new pot and its first move commit together; a rejected take writes nothing.
    if entry.kind not in ("save", "take") or entry.pot is None:
        raise ValueError("apply_pot_entry needs a save or take entry that names a pot")
    name = entry.pot.lower()
    with conn:
        pot = get_pot(conn, name)
        if entry.kind == "take":
            if pot is None:
                raise _unknown_pot(name)
            if entry.amount_cents > pot.total_cents:
                raise SavingsError(
                    f"{name.capitalize()} has {format_cents(pot.total_cents)} EUR,"
                    f" cannot take {format_cents(entry.amount_cents)}"
                )
        pot_id = (
            pot.id
            if pot is not None
            else _insert(conn, "INSERT INTO pots (name) VALUES (?)", (name,))
        )
        entry_id = _insert(
            conn,
            "INSERT INTO entries (kind, amount_cents, currency, eur_cents, pot_id, occurred_on)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                entry.kind,
                entry.amount_cents,
                "EUR",
                entry.amount_cents,
                pot_id,
                entry.on.isoformat(),
            ),
        )
        return entry_id, _pot_by_id(conn, pot_id)


def set_goal(
    conn: sqlite3.Connection, name: str, goal_cents: int, goal_month: str | None = None
) -> Pot:
    name = name.lower()
    with conn:
        pot = get_pot(conn, name)
        if pot is None:
            raise _unknown_pot(name)
        conn.execute(
            "UPDATE pots SET goal_cents = ?, goal_month = ? WHERE id = ?",
            (goal_cents, goal_month, pot.id),
        )
    return replace(pot, goal_cents=goal_cents, goal_month=goal_month)


def months_left(goal_month: str, today: date) -> int:
    """Months from today's month to the goal month, both counted. 0 or less: it has passed."""
    year, month = _year_month(goal_month)
    return (year - today.year) * 12 + month - today.month + 1


def monthly_cents(remaining_cents: int, months: int) -> int:
    """Rounded UP to the cent, so the goal is not missed by rounding. This is the plan's
    exception to ROUND_HALF_UP. Needs months >= 1."""
    return -(-remaining_cents // months)


def month_label(goal_month: str) -> str:
    year, month = _year_month(goal_month)
    return f"{month:02d}.{year:04d}"


def get_pot(conn: sqlite3.Connection, name: str) -> Pot | None:
    row = conn.execute(_POTS + " WHERE p.name = ? GROUP BY p.id", (name.lower(),)).fetchone()
    return None if row is None else _pot(row)


def list_pots(conn: sqlite3.Connection) -> list[Pot]:
    # A pot whose moves were all deleted (e.g. a typo) is hidden; get_pot still finds it.
    return [
        _pot(row)
        for row in conn.execute(_POTS + " GROUP BY p.id HAVING COUNT(e.id) > 0 ORDER BY p.name")
    ]


def recent_moves(conn: sqlite3.Connection, pot_id: int, limit: int = 5) -> list[PotMove]:
    rows = conn.execute(
        "SELECT id, kind, amount_cents, occurred_on FROM entries"
        " WHERE pot_id = ? AND deleted_at IS NULL"
        " ORDER BY occurred_on DESC, id DESC LIMIT ?",
        (pot_id, limit),
    ).fetchall()
    return [
        PotMove(row["id"], row["kind"], row["amount_cents"], date.fromisoformat(row["occurred_on"]))
        for row in rows
    ]


def _year_month(goal_month: str) -> tuple[int, int]:
    year, month = goal_month.split("-")
    return int(year), int(month)


def _pot_by_id(conn: sqlite3.Connection, pot_id: int) -> Pot:
    return _pot(conn.execute(_POTS + " WHERE p.id = ? GROUP BY p.id", (pot_id,)).fetchone())


def _pot(row: sqlite3.Row) -> Pot:
    return Pot(row["id"], row["name"], row["total_cents"], row["goal_cents"], row["goal_month"])


def _unknown_pot(name: str) -> SavingsError:
    return SavingsError(f"No pot named {name} yet. Start it with: save 100 {name}")


def _insert(conn: sqlite3.Connection, sql: str, params: tuple) -> int:
    row_id = conn.execute(sql, params).lastrowid
    assert row_id is not None
    return row_id
