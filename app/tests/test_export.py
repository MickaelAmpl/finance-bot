import sqlite3
from datetime import date

from finbot.categories import list_categories
from finbot.export import export_csv
from finbot.ledger import add_transaction, delete_entry, set_category
from finbot.parser import parse_entry
from finbot.rates import parse_rate, set_rate
from finbot.savings import apply_pot_entry

TODAY = date(2026, 11, 1)

EXPECTED = (
    b"date,type,amount,currency,rate,amount_eur,category,note,pot\n"
    b"2026-11-01,expense,25.00,EUR,,25.00,Eating out,coffee,\n"
    b"2026-11-01,expense,25.00,USD,,,,book,\n"
    b"2026-11-01,save,200.00,EUR,,200.00,,,emergency\n"
    b'2026-11-01,expense,12.00,EUR,,12.00,,"lunch, work",\n'
)


def test_export_same_day_rows_follow_id_and_skip_deleted(conn: sqlite3.Connection) -> None:
    eating_out = next(c for c in list_categories(conn, "expense") if c.name == "Eating out")
    coffee = add_transaction(conn, parse_entry("25 coffee", TODAY))
    set_category(conn, coffee.id, eating_out.id)
    add_transaction(conn, parse_entry("25 usd book", TODAY))
    apply_pot_entry(conn, parse_entry("save 200 emergency", TODAY))
    tea = add_transaction(conn, parse_entry("7 tea", TODAY))
    delete_entry(conn, tea.id)
    add_transaction(conn, parse_entry("12 lunch, work", TODAY))

    assert export_csv(conn) == EXPECTED


def test_export_shows_stored_rate_and_converted_pending_entry(conn: sqlite3.Connection) -> None:
    set_rate(conn, "UAH", parse_rate("0.0220"), TODAY)
    add_transaction(conn, parse_entry("100 uah book", TODAY))
    add_transaction(conn, parse_entry("25 usd lunch", TODAY))
    set_rate(conn, "USD", parse_rate("0.92"), TODAY)

    assert export_csv(conn) == (
        b"date,type,amount,currency,rate,amount_eur,category,note,pot\n"
        b"2026-11-01,expense,100.00,UAH,0.0220,2.20,,book,\n"
        b"2026-11-01,expense,25.00,USD,0.92,23.00,,lunch,\n"
    )
