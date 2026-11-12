import csv
import io
import sqlite3

from finbot import ledger

HEADER = ["date", "type", "amount", "currency", "rate", "amount_eur", "category", "note", "pot"]


def export_csv(conn: sqlite3.Connection) -> bytes:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(HEADER)
    for record in ledger.all_records(conn):
        writer.writerow(
            [
                record.on.isoformat(),
                record.kind,
                _amount(record.amount_cents),
                record.currency,
                "" if record.rate is None else str(record.rate),
                "" if record.eur_cents is None else _amount(record.eur_cents),
                record.category or "",
                record.note,
                record.pot or "",
            ]
        )
    return out.getvalue().encode("utf-8")


def _amount(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"
