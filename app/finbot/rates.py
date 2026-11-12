import re
import sqlite3
from datetime import date
from decimal import Decimal

from finbot.money import to_eur

_RATE_TEXT = re.compile(r"[0-9]+(?:[.,][0-9]{1,6})?")
RATE_RANGES = {"USD": (Decimal("0.5"), Decimal("2")), "UAH": (Decimal("0.005"), Decimal("0.1"))}
_RATE_EXAMPLES = {"USD": "0.92", "UAH": "0.022"}


class RateError(ValueError):
    """The message is shown to the user as is."""


def check_rate(currency: str, rate: Decimal) -> None:
    low, high = RATE_RANGES[currency]
    if not low <= rate <= high:
        raise RateError(
            f"That rate looks wrong: 1 {currency} should be between {low} and {high} EUR."
            f" Example: /rate {currency.lower()} {_RATE_EXAMPLES[currency]}"
        )


def parse_rate(text: str) -> Decimal:
    if not _RATE_TEXT.fullmatch(text):
        raise ValueError(f"invalid rate: {text!r}")
    rate = Decimal(text.replace(",", "."))
    if rate <= 0:
        raise ValueError(f"rate must be above zero: {text!r}")
    return rate


def rate_on(conn: sqlite3.Connection, currency: str, on: date) -> Decimal | None:
    row = conn.execute(
        "SELECT eur_per_unit FROM rates WHERE currency = ? AND set_on <= ?"
        " ORDER BY set_on DESC, id DESC LIMIT 1",
        (currency, on.isoformat()),
    ).fetchone()
    return None if row is None else Decimal(row["eur_per_unit"])


def set_rate(conn: sqlite3.Connection, currency: str, eur_per_unit: Decimal, on: date) -> list[int]:
    # The rate and the pending conversions commit together or not at all.
    with conn:
        conn.execute(
            "INSERT INTO rates (currency, eur_per_unit, set_on) VALUES (?, ?, ?)",
            (currency, str(eur_per_unit), on.isoformat()),
        )
        pending = conn.execute(
            "SELECT id, amount_cents FROM entries"
            " WHERE currency = ? AND eur_cents IS NULL AND deleted_at IS NULL ORDER BY id",
            (currency,),
        ).fetchall()
        for row in pending:
            conn.execute(
                "UPDATE entries SET rate = ?, eur_cents = ? WHERE id = ?",
                (str(eur_per_unit), to_eur(row["amount_cents"], eur_per_unit), row["id"]),
            )
    return [row["id"] for row in pending]
