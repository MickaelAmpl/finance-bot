import sqlite3
from calendar import monthrange
from dataclasses import dataclass
from datetime import date

from finbot.categories import Category
from finbot.ledger import Record


class BudgetError(ValueError):
    """The message is shown to the user as is."""


@dataclass(frozen=True)
class Budget:
    category: str
    limit_cents: int
    spent_cents: int

    @property
    def left_cents(self) -> int:
        return self.limit_cents - self.spent_cents


def set_budget(
    conn: sqlite3.Connection, category: Category, amount_cents: int, year: int, month: int
) -> Budget:
    _require_expense(category)
    with conn:
        conn.execute(
            "INSERT INTO budgets (category_id, amount_cents) VALUES (?, ?) "
            "ON CONFLICT(category_id) DO UPDATE SET amount_cents = excluded.amount_cents",
            (category.id, amount_cents),
        )
    return Budget(category.name, amount_cents, _spent(conn, category.id, year, month))


def remove_budget(conn: sqlite3.Connection, category: Category) -> None:
    _require_expense(category)
    with conn:
        cursor = conn.execute("DELETE FROM budgets WHERE category_id = ?", (category.id,))
    if cursor.rowcount == 0:
        raise BudgetError(f"{category.name} has no budget.")


def list_budgets(conn: sqlite3.Connection, year: int, month: int) -> list[Budget]:
    rows = conn.execute(
        "SELECT c.id, c.name, b.amount_cents FROM budgets b "
        "JOIN categories c ON c.id = b.category_id ORDER BY c.position"
    ).fetchall()
    return [
        Budget(row["name"], row["amount_cents"], _spent(conn, row["id"], year, month))
        for row in rows
    ]


def entry_budget(conn: sqlite3.Connection, record: Record) -> Budget | None:
    """Where an expense stands against its category's budget, in the month of the expense itself.

    A pending expense is not in the sums yet, so it gets no budget.
    """
    if record.kind != "expense" or record.pending or record.category is None:
        return None
    row = conn.execute(
        "SELECT c.id, b.amount_cents FROM budgets b "
        "JOIN categories c ON c.id = b.category_id WHERE c.name = ?",
        (record.category,),
    ).fetchone()
    if row is None:
        return None
    spent = _spent(conn, row["id"], record.on.year, record.on.month)
    return Budget(record.category, row["amount_cents"], spent)


def _require_expense(category: Category) -> None:
    if category.kind != "expense":
        raise BudgetError("Budgets are for expense categories.")


def _spent(conn: sqlite3.Connection, category_id: int, year: int, month: int) -> int:
    # SUM skips pending entries: their eur_cents is NULL.
    first = date(year, month, 1)
    last = date(year, month, monthrange(year, month)[1])
    row = conn.execute(
        "SELECT COALESCE(SUM(eur_cents), 0) AS cents FROM entries "
        "WHERE category_id = ? AND kind = 'expense' AND deleted_at IS NULL "
        "AND occurred_on BETWEEN ? AND ?",
        (category_id, first.isoformat(), last.isoformat()),
    ).fetchone()
    return row["cents"]
