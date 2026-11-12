from datetime import date
from decimal import Decimal

import pytest

from finbot.categories import Category, category_for_keyword, remember_keyword
from finbot.ledger import (
    add_transaction,
    all_records,
    clear_month,
    clearable_summary,
    delete_entry,
    get_record,
    last_records,
    records_between,
    set_category,
    undo_last,
)
from finbot.parser import parse_entry
from finbot.rates import set_rate
from finbot.savings import SavingsError, apply_pot_entry, get_pot

TODAY = date(2026, 11, 1)
LATER = date(2026, 12, 15)
BELOW_ZERO = "Emergency would go below zero. Delete the later take first."


def category_id(conn, name):
    return conn.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()["id"]


def add_pot_move(conn, kind, cents, pot, on):
    with conn:
        conn.execute("INSERT OR IGNORE INTO pots (name) VALUES (?)", (pot,))
        conn.execute(
            "INSERT INTO entries (kind, amount_cents, currency, pot_id, occurred_on)"
            " VALUES (?, ?, 'EUR', (SELECT id FROM pots WHERE name = ?), ?)",
            (kind, cents, pot, on.isoformat()),
        )


def test_eur_expense_without_keyword_is_saved_in_full(conn):
    record = add_transaction(conn, parse_entry("25 coffee", TODAY))
    assert record.kind == "expense"
    assert record.category is None
    assert record.eur_cents == 2500
    assert record.rate is None
    assert record.on == TODAY
    assert record.pending is False


def test_remembered_keyword_sets_the_category(conn):
    remember_keyword(conn, "coffee", category_id(conn, "Eating out"))
    record = add_transaction(conn, parse_entry("25 coffee", TODAY))
    assert record.category == "Eating out"


def test_income_uses_the_remembered_income_category(conn):
    remember_keyword(conn, "salary", category_id(conn, "Salary"))
    record = add_transaction(conn, parse_entry("+3000 salary", TODAY))
    assert record.kind == "income"
    assert record.category == "Salary"
    assert record.eur_cents == 300000


def test_foreign_entry_is_converted_with_the_rate_on_its_date(conn):
    set_rate(conn, "UAH", Decimal("0.022"), TODAY)
    record = add_transaction(conn, parse_entry("1200 uah taxi", TODAY))
    assert record.currency == "UAH"
    assert record.rate == Decimal("0.022")
    assert record.eur_cents == 2640
    assert record.pending is False


def test_foreign_entry_without_a_rate_is_pending(conn):
    record = add_transaction(conn, parse_entry("25 usd book", TODAY))
    assert record.pending is True
    assert record.rate is None
    assert record.eur_cents is None


def test_entry_dated_back_uses_the_rate_in_force_on_its_date(conn):
    set_rate(conn, "USD", Decimal("0.90"), date(2026, 10, 1))
    set_rate(conn, "USD", Decimal("0.95"), date(2026, 10, 20))
    early = add_transaction(conn, parse_entry("25 usd book 05.10", TODAY))
    late = add_transaction(conn, parse_entry("25 usd book 25.10", TODAY))
    assert (early.rate, early.eur_cents) == (Decimal("0.90"), 2250)
    assert (late.rate, late.eur_cents) == (Decimal("0.95"), 2375)


def test_add_transaction_rejects_pot_moves(conn):
    with pytest.raises(ValueError):
        add_transaction(conn, parse_entry("save 200 emergency", TODAY))


def test_set_category_updates_entry_and_remembers_keyword(conn):
    groceries = category_id(conn, "Groceries")
    record = add_transaction(conn, parse_entry("25 coffee", TODAY))
    updated = set_category(conn, record.id, groceries)
    assert updated.category == "Groceries"
    assert get_record(conn, record.id) == updated
    assert category_for_keyword(conn, "coffee", "expense") == Category(
        id=groceries, name="Groceries", kind="expense"
    )


def test_recategorising_replaces_the_remembered_keyword(conn):
    eating_out = category_id(conn, "Eating out")
    groceries = category_id(conn, "Groceries")
    record = add_transaction(conn, parse_entry("25 coffee", TODAY))
    set_category(conn, record.id, eating_out)
    set_category(conn, record.id, groceries)
    assert category_for_keyword(conn, "coffee", "expense") == Category(
        id=groceries, name="Groceries", kind="expense"
    )


def test_set_category_on_missing_or_deleted_entry_raises(conn):
    groceries = category_id(conn, "Groceries")
    record = add_transaction(conn, parse_entry("25 coffee", TODAY))
    delete_entry(conn, record.id)
    with pytest.raises(LookupError):
        set_category(conn, record.id, groceries)
    with pytest.raises(LookupError):
        set_category(conn, 999, groceries)


def test_delete_entry_returns_the_record_once(conn):
    record = add_transaction(conn, parse_entry("25 coffee", TODAY))
    assert delete_entry(conn, record.id) == record
    assert delete_entry(conn, record.id) is None
    assert delete_entry(conn, 999) is None
    assert get_record(conn, record.id) is None


def test_undo_last_removes_the_newest_entry_each_time(conn):
    first = add_transaction(conn, parse_entry("25 coffee", TODAY))
    second = add_transaction(conn, parse_entry("12 bus", TODAY))
    assert undo_last(conn) == second
    assert undo_last(conn) == first
    assert undo_last(conn) is None


def test_undo_last_removes_a_pot_move(conn):
    add_pot_move(conn, "save", 20000, "emergency", TODAY)
    record = undo_last(conn)
    assert record is not None
    assert record.kind == "save"
    assert record.pot == "emergency"
    assert all_records(conn) == []


def pot_move(conn, text):
    entry_id, _ = apply_pot_entry(conn, parse_entry(text, TODAY))
    return entry_id


def pot_total(conn, name):
    pot = get_pot(conn, name)
    assert pot is not None
    return pot.total_cents


def test_deleting_a_save_that_takes_already_used_is_refused_and_changes_nothing(conn):
    save_id = pot_move(conn, "save 100 emergency")
    pot_move(conn, "take 80 emergency")

    with pytest.raises(SavingsError, match=BELOW_ZERO):
        delete_entry(conn, save_id)

    assert get_record(conn, save_id) is not None
    assert pot_total(conn, "emergency") == 2000


def test_deleting_a_save_that_leaves_exactly_zero_is_allowed(conn):
    first_id = pot_move(conn, "save 100 emergency")
    pot_move(conn, "take 80 emergency")
    pot_move(conn, "save 80 emergency")

    record = delete_entry(conn, first_id)

    assert record is not None
    assert record.id == first_id
    assert pot_total(conn, "emergency") == 0


def test_deleting_a_take_is_allowed(conn):
    pot_move(conn, "save 100 emergency")
    take_id = pot_move(conn, "take 80 emergency")

    assert delete_entry(conn, take_id) is not None

    assert pot_total(conn, "emergency") == 10000


def test_a_save_is_checked_against_its_own_pot_only(conn):
    holiday_id = pot_move(conn, "save 100 holiday")
    pot_move(conn, "save 100 emergency")
    pot_move(conn, "take 80 emergency")

    assert delete_entry(conn, holiday_id) is not None

    assert pot_total(conn, "emergency") == 2000


def test_undo_last_refuses_a_save_that_would_leave_the_pot_below_zero(conn):
    # A pot that is already below zero, as the old delete rule could leave it.
    old_save_id = pot_move(conn, "save 100 emergency")
    pot_move(conn, "take 80 emergency")
    with conn:
        conn.execute("UPDATE entries SET deleted_at = 'x' WHERE id = ?", (old_save_id,))
    newest_id = pot_move(conn, "save 10 emergency")

    with pytest.raises(SavingsError, match=BELOW_ZERO):
        undo_last(conn)

    assert get_record(conn, newest_id) is not None


def test_last_records_returns_ten_newest_first(conn):
    for euros in range(1, 13):
        add_transaction(conn, parse_entry(f"{euros} coffee", TODAY))
    assert [r.amount_cents for r in last_records(conn)] == [
        1200,
        1100,
        1000,
        900,
        800,
        700,
        600,
        500,
        400,
        300,
    ]


def test_last_records_skips_a_deleted_entry(conn):
    kept = add_transaction(conn, parse_entry("25 coffee", TODAY))
    deleted = add_transaction(conn, parse_entry("12 bus", TODAY))
    delete_entry(conn, deleted.id)
    assert [r.id for r in last_records(conn)] == [kept.id]


def test_history_is_ordered_by_date_then_id(conn):
    later = add_transaction(conn, parse_entry("1 coffee", date(2026, 11, 20)))
    earlier = add_transaction(conn, parse_entry("2 coffee", date(2026, 11, 5)))
    same_day = add_transaction(conn, parse_entry("3 coffee", date(2026, 11, 5)))
    expected = [earlier.id, same_day.id, later.id]
    assert [r.id for r in all_records(conn)] == expected
    november = records_between(conn, date(2026, 11, 1), date(2026, 11, 30))
    assert [r.id for r in november] == expected


def test_records_between_is_inclusive_and_skips_deleted_and_out_of_range(conn):
    add_transaction(conn, parse_entry("9 coffee", date(2026, 10, 31)))
    add_transaction(conn, parse_entry("10 coffee", date(2026, 11, 1)))
    deleted = add_transaction(conn, parse_entry("30 coffee", date(2026, 11, 15)))
    delete_entry(conn, deleted.id)
    add_pot_move(conn, "save", 20000, "emergency", date(2026, 11, 30))
    add_transaction(conn, parse_entry("50 coffee", date(2026, 12, 1)))

    records = records_between(conn, date(2026, 11, 1), date(2026, 11, 30))

    assert [r.amount_cents for r in records] == [1000, 20000]
    assert records[1].kind == "save"
    assert records[1].pot == "emergency"


def deleted_at(conn, entry_id):
    return conn.execute("SELECT deleted_at FROM entries WHERE id = ?", (entry_id,)).fetchone()[
        "deleted_at"
    ]


def test_clearable_summary_counts_expenses_and_incomes_of_the_month_by_entry_date(conn):
    add_transaction(conn, parse_entry("9 coffee 31.10", LATER))
    add_transaction(conn, parse_entry("10 coffee 01.11", LATER))
    add_transaction(conn, parse_entry("+3000 salary 15.11", LATER))
    add_transaction(conn, parse_entry("12 bus 30.11", LATER))
    add_transaction(conn, parse_entry("5 coffee 01.12", LATER))
    assert clearable_summary(conn, 2026, 11) == (3, 4)
    assert clearable_summary(conn, 2026, 10) == (1, 1)
    assert clearable_summary(conn, 2026, 12) == (1, 5)
    assert clearable_summary(conn, 2027, 1) == (0, 0)


def test_clearable_summary_skips_pot_moves_and_deleted_entries(conn):
    add_transaction(conn, parse_entry("10 coffee", TODAY))
    gone = add_transaction(conn, parse_entry("20 coffee", TODAY))
    delete_entry(conn, gone.id)
    add_pot_move(conn, "save", 20000, "emergency", TODAY)
    add_pot_move(conn, "take", 5000, "emergency", TODAY)
    assert clearable_summary(conn, 2026, 11) == (1, 1)


def test_clear_month_soft_deletes_the_months_expenses_and_incomes_and_keeps_their_ids(conn):
    expense = add_transaction(conn, parse_entry("10 coffee", TODAY))
    income = add_transaction(conn, parse_entry("+3000 salary", TODAY))
    october = add_transaction(conn, parse_entry("9 coffee 31.10", TODAY))
    december = add_transaction(conn, parse_entry("8 coffee", date(2026, 12, 1)))

    assert clear_month(conn, 2026, 11, 2, income.id) == 2

    assert deleted_at(conn, expense.id) is not None
    assert deleted_at(conn, income.id) is not None
    assert deleted_at(conn, october.id) is None
    assert deleted_at(conn, december.id) is None
    assert get_record(conn, expense.id) is None
    assert clearable_summary(conn, 2026, 11) == (0, 0)


def test_clear_month_leaves_pot_moves_and_pot_totals_alone(conn):
    entry = add_transaction(conn, parse_entry("10 coffee", TODAY))
    add_pot_move(conn, "save", 20000, "emergency", TODAY)
    add_pot_move(conn, "take", 5000, "emergency", TODAY)

    clear_month(conn, 2026, 11, 1, entry.id)

    assert pot_total(conn, "emergency") == 15000
    assert [r.kind for r in all_records(conn)] == ["save", "take"]


def test_clear_month_keeps_the_time_an_entry_was_deleted_earlier(conn):
    earlier = add_transaction(conn, parse_entry("20 coffee", TODAY))
    with conn:
        conn.execute(
            "UPDATE entries SET deleted_at = '2026-10-01T08:00:00.000Z' WHERE id = ?",
            (earlier.id,),
        )
    current = add_transaction(conn, parse_entry("10 coffee", TODAY))

    assert clear_month(conn, 2026, 11, 1, current.id) == 1

    assert deleted_at(conn, earlier.id) == "2026-10-01T08:00:00.000Z"


def test_clear_month_deletes_nothing_when_the_count_changed(conn):
    first = add_transaction(conn, parse_entry("10 coffee", TODAY))
    second = add_transaction(conn, parse_entry("20 coffee", TODAY))
    assert clear_month(conn, 2026, 11, 1, second.id) is None
    assert clear_month(conn, 2026, 11, 3, second.id) is None
    assert get_record(conn, first.id) is not None
    assert clearable_summary(conn, 2026, 11) == (2, second.id)


def test_clear_month_deletes_nothing_when_the_count_is_the_same_but_the_entries_are_new(conn):
    add_transaction(conn, parse_entry("10 coffee", TODAY))
    shown = add_transaction(conn, parse_entry("20 coffee", TODAY))
    undone = undo_last(conn)
    assert undone is not None
    replacement = add_transaction(conn, parse_entry("30 coffee", TODAY))
    assert clearable_summary(conn, 2026, 11) == (2, replacement.id)

    assert clear_month(conn, 2026, 11, 2, shown.id) is None

    assert get_record(conn, replacement.id) is not None


def test_clear_month_a_second_time_finds_nothing_and_changes_nothing(conn):
    entry = add_transaction(conn, parse_entry("10 coffee", TODAY))
    assert clear_month(conn, 2026, 11, 1, entry.id) == 1
    stamp = deleted_at(conn, entry.id)
    assert clear_month(conn, 2026, 11, 1, entry.id) is None
    assert deleted_at(conn, entry.id) == stamp


def test_clear_month_takes_the_write_lock_before_it_counts_and_commits_once(conn):
    entry = add_transaction(conn, parse_entry("10 coffee", TODAY))
    statements = []
    conn.set_trace_callback(statements.append)

    clear_month(conn, 2026, 11, 1, entry.id)

    conn.set_trace_callback(None)
    assert statements[0] == "BEGIN IMMEDIATE"
    assert statements[1].startswith("SELECT COUNT(*)")
    assert statements[2].startswith("UPDATE entries SET deleted_at")
    assert statements[3:] == ["COMMIT"]


def test_clear_month_rejects_a_month_that_is_not_a_date_and_writes_nothing(conn):
    entry = add_transaction(conn, parse_entry("10 coffee", TODAY))
    for year, month in [(2026, 13), (2026, 0), (0, 11), (10000, 11)]:
        with pytest.raises(ValueError):
            clear_month(conn, year, month, 1, entry.id)
    assert get_record(conn, entry.id) is not None
    assert conn.in_transaction is False
