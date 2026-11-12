from datetime import date
from decimal import Decimal

import pytest

from finbot.budgets import (
    Budget,
    BudgetError,
    entry_budget,
    list_budgets,
    remove_budget,
    set_budget,
)
from finbot.categories import add_category, find_category, rename_category
from finbot.ledger import Record, add_transaction, delete_entry, get_record, set_category
from finbot.parser import parse_entry
from finbot.rates import set_rate
from finbot.savings import apply_pot_entry

TODAY = date(2026, 12, 15)


def _category(conn, name):
    found = find_category(conn, name)
    assert found is not None
    return found


def _spend(conn, text: str, name: str = "Housing") -> Record:
    record = add_transaction(conn, parse_entry(text, TODAY))
    return set_category(conn, record.id, _category(conn, name).id)


def _budget(conn, name: str, cents: int, year: int = 2026, month: int = 12) -> Budget:
    return set_budget(conn, _category(conn, name), cents, year, month)


def test_set_budget_returns_the_budget_with_nothing_spent_yet(conn):
    assert _budget(conn, "Housing", 85000) == Budget("Housing", 85000, 0)


def test_set_budget_again_replaces_the_limit(conn):
    _budget(conn, "Housing", 85000)
    assert _budget(conn, "Housing", 90000) == Budget("Housing", 90000, 0)
    assert list_budgets(conn, 2026, 12) == [Budget("Housing", 90000, 0)]


def test_left_is_the_limit_minus_the_spent(conn):
    _spend(conn, "800 rent")
    budget = _budget(conn, "Housing", 85000)
    assert budget.spent_cents == 80000
    assert budget.left_cents == 5000


def test_spent_counts_the_month_of_the_entry_only(conn):
    _spend(conn, "100 rent 31.10")
    _spend(conn, "250 rent 01.11")
    _spend(conn, "30 rent 30.11")
    _spend(conn, "7 rent 01.12")
    _budget(conn, "Housing", 85000)
    assert list_budgets(conn, 2026, 10)[0].spent_cents == 10000
    assert list_budgets(conn, 2026, 11)[0].spent_cents == 28000
    assert list_budgets(conn, 2026, 12)[0].spent_cents == 700


def test_spent_in_a_month_without_entries_is_zero(conn):
    _spend(conn, "100 rent 31.10")
    _budget(conn, "Housing", 85000)
    assert list_budgets(conn, 2026, 9) == [Budget("Housing", 85000, 0)]


def test_a_usd_entry_is_counted_by_its_eur_amount(conn):
    set_rate(conn, "USD", Decimal("0.92"), TODAY)
    _spend(conn, "100 usd rent")
    assert _budget(conn, "Housing", 85000).spent_cents == 9200


def test_a_pending_entry_is_not_counted_until_it_has_a_rate(conn):
    _spend(conn, "100 usd rent")
    _spend(conn, "50 rent")
    assert _budget(conn, "Housing", 85000).spent_cents == 5000
    set_rate(conn, "USD", Decimal("0.92"), TODAY)
    assert list_budgets(conn, 2026, 12)[0].spent_cents == 14200


def test_a_deleted_entry_is_not_counted(conn):
    gone = _spend(conn, "100 rent")
    _spend(conn, "50 rent")
    delete_entry(conn, gone.id)
    assert _budget(conn, "Housing", 85000).spent_cents == 5000


def test_other_categories_are_not_counted(conn):
    _spend(conn, "100 rent")
    _spend(conn, "60 pizza", "Eating out")
    add_transaction(conn, parse_entry("45 mystery", TODAY))
    assert _budget(conn, "Housing", 85000).spent_cents == 10000
    assert _budget(conn, "Eating out", 30000).spent_cents == 6000


def test_an_income_entry_in_a_budgeted_category_is_not_counted(conn):
    housing = _category(conn, "Housing")
    _budget(conn, "Housing", 85000)
    with conn:
        cursor = conn.execute(
            "INSERT INTO entries (kind, amount_cents, currency, eur_cents, category_id,"
            " keyword, note, occurred_on) VALUES ('income', 50000, 'EUR', 50000, ?, 'x', 'x', ?)",
            (housing.id, TODAY.isoformat()),
        )
    stray = get_record(conn, cursor.lastrowid)
    assert stray is not None
    assert list_budgets(conn, 2026, 12) == [Budget("Housing", 85000, 0)]
    assert entry_budget(conn, stray) is None


def test_over_the_limit_has_a_negative_left(conn):
    _spend(conn, "320 pizza", "Eating out")
    budget = _budget(conn, "Eating out", 30000)
    assert budget.left_cents == -2000


def test_exactly_at_the_limit_has_nothing_left(conn):
    _spend(conn, "300 pizza", "Eating out")
    assert _budget(conn, "Eating out", 30000).left_cents == 0


def test_list_budgets_follows_the_category_position_order(conn):
    _budget(conn, "Housing", 85000)
    _budget(conn, "Eating out", 30000)
    add_category(conn, "Rent", "expense")
    _budget(conn, "Rent", 50000)
    assert [b.category for b in list_budgets(conn, 2026, 12)] == ["Eating out", "Housing", "Rent"]


def test_list_budgets_is_empty_without_budgets(conn):
    assert list_budgets(conn, 2026, 12) == []


def test_set_budget_refuses_an_income_category(conn):
    with pytest.raises(BudgetError) as error:
        _budget(conn, "Salary", 100000)
    assert str(error.value) == "Budgets are for expense categories."
    assert list_budgets(conn, 2026, 12) == []


def test_remove_budget_deletes_it(conn):
    _budget(conn, "Housing", 85000)
    _budget(conn, "Eating out", 30000)
    remove_budget(conn, _category(conn, "Housing"))
    assert [b.category for b in list_budgets(conn, 2026, 12)] == ["Eating out"]


def test_remove_budget_without_a_budget_says_so(conn):
    with pytest.raises(BudgetError) as error:
        remove_budget(conn, _category(conn, "Housing"))
    assert str(error.value) == "Housing has no budget."


def test_remove_budget_refuses_an_income_category(conn):
    with pytest.raises(BudgetError) as error:
        remove_budget(conn, _category(conn, "Salary"))
    assert str(error.value) == "Budgets are for expense categories."


def test_a_renamed_category_keeps_its_budget_under_the_new_name(conn):
    _spend(conn, "100 rent")
    _budget(conn, "Housing", 85000)
    rename_category(conn, _category(conn, "Housing").id, "Rent")
    assert list_budgets(conn, 2026, 12) == [Budget("Rent", 85000, 10000)]


def test_entry_budget_is_the_budget_of_the_entry_own_month(conn):
    _budget(conn, "Housing", 85000)
    october = _spend(conn, "100 rent 31.10")
    november = _spend(conn, "250 rent 01.11")
    assert entry_budget(conn, october) == Budget("Housing", 85000, 10000)
    assert entry_budget(conn, november) == Budget("Housing", 85000, 25000)


def test_entry_budget_counts_the_entry_itself(conn):
    _budget(conn, "Housing", 85000)
    assert entry_budget(conn, _spend(conn, "800 rent")) == Budget("Housing", 85000, 80000)


def test_entry_budget_is_none_for_a_category_without_a_budget(conn):
    assert entry_budget(conn, _spend(conn, "800 rent")) is None


def test_entry_budget_is_none_for_a_pending_entry(conn):
    _budget(conn, "Housing", 85000)
    assert entry_budget(conn, _spend(conn, "800 usd rent")) is None


def test_entry_budget_is_none_for_an_entry_without_a_category(conn):
    _budget(conn, "Housing", 85000)
    assert entry_budget(conn, add_transaction(conn, parse_entry("45 mystery", TODAY))) is None


def test_entry_budget_is_none_for_income(conn):
    _budget(conn, "Housing", 85000)
    income = add_transaction(conn, parse_entry("+3000 salary", TODAY))
    assert entry_budget(conn, set_category(conn, income.id, _category(conn, "Salary").id)) is None


def test_entry_budget_is_none_for_a_pot_move(conn):
    _budget(conn, "Housing", 85000)
    entry_id, _ = apply_pot_entry(conn, parse_entry("save 200 emergency", TODAY))
    move = get_record(conn, entry_id)
    assert move is not None
    assert entry_budget(conn, move) is None
