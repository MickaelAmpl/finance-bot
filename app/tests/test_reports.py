from datetime import date

import pytest

from finbot.budgets import set_budget
from finbot.categories import find_category, list_categories, remember_keyword
from finbot.ledger import add_transaction
from finbot.parser import parse_entry
from finbot.reports import build_month_report, parse_month_arg, render_month
from finbot.savings import apply_pot_entry, set_goal

TODAY = date(2026, 10, 31)
NOV_1 = date(2026, 11, 1)
KEYWORDS = {
    "rent": "Housing",
    "billa": "Groceries",
    "dinner": "Eating out",
    "ticket": "Transport",
    "salary": "Salary",
}
GOLDEN = """October 2026

Income 3,000.00 EUR
Spent  1,850.00 EUR  ▲ 6% vs Sep
Saved    400.00 EUR
Net      750.00 EUR

Housing     930.00  ████████████  50%
Groceries   420.00  █████         23%
Eating out  310.00  ████          17%
Transport   190.00  ██            10%

Top expenses
01.10  930.00  rent
03.10  420.00  billa
10.10  310.00  dinner
15.10  190.00  ticket

Savings
Emergency  1,400.00 / 10,000.00 (14%)"""


def _add(conn, text: str) -> None:
    add_transaction(conn, parse_entry(text, TODAY))


def _remember_keywords(conn) -> None:
    found = list_categories(conn, "expense") + list_categories(conn, "income")
    ids = {category.name: category.id for category in found}
    for keyword, name in KEYWORDS.items():
        remember_keyword(conn, keyword, ids[name])


def _golden_month(conn) -> None:
    _remember_keywords(conn)
    _add(conn, "1745 rent 15.09")
    _add(conn, "+3000 salary 01.10")
    _add(conn, "930 rent 01.10")
    _add(conn, "420 billa 03.10")
    _add(conn, "310 dinner 10.10")
    _add(conn, "190 ticket 15.10")
    apply_pot_entry(conn, parse_entry("save 1000 emergency 15.09", TODAY))
    apply_pot_entry(conn, parse_entry("save 400 emergency 05.10", TODAY))
    set_goal(conn, "emergency", 1_000_000)


def _line(text: str, start: str) -> str:
    return next(line for line in text.splitlines() if line.startswith(start))


@pytest.mark.parametrize("arg", [None, ""])
def test_parse_month_arg_without_value_is_the_current_month(arg):
    assert parse_month_arg(arg, NOV_1) == (2026, 11)


def test_parse_month_arg_month_number_is_this_year_or_last_year_when_future():
    assert parse_month_arg("10", NOV_1) == (2026, 10)
    assert parse_month_arg("12", NOV_1) == (2025, 12)


def test_parse_month_arg_accepts_year_and_month():
    assert parse_month_arg("2026-09", NOV_1) == (2026, 9)


@pytest.mark.parametrize("arg", ["13", "0", "2026-13", "October", "10.2026"])
def test_parse_month_arg_rejects_anything_else(arg):
    with pytest.raises(ValueError):
        parse_month_arg(arg, NOV_1)


def test_golden_october_report(conn):
    _golden_month(conn)
    assert render_month(build_month_report(conn, 2026, 10)) == GOLDEN


def test_pending_usd_expense_is_left_out_and_counted_in_a_note(conn):
    _golden_month(conn)
    _add(conn, "25 usd book")
    assert render_month(build_month_report(conn, 2026, 10)) == (
        GOLDEN + "\n\nNot counted: 1 pending (no rate). Use /rate to convert."
    )


def test_month_without_entries_says_no_entries(conn):
    assert render_month(build_month_report(conn, 2026, 10)) == "October 2026\n\nNo entries."


def test_spending_below_previous_month_shows_down_arrow(conn):
    _add(conn, "1000 rent 15.09")
    _add(conn, "500 rent 03.10")
    assert "▼ 50% vs Sep" in render_month(build_month_report(conn, 2026, 10))


def test_equal_spending_shows_up_arrow_with_zero_percent(conn):
    _add(conn, "500 rent 15.09")
    _add(conn, "500 rent 03.10")
    assert "▲ 0% vs Sep" in render_month(build_month_report(conn, 2026, 10))


def test_no_change_marker_without_previous_month_spending(conn):
    _add(conn, "500 rent 03.10")
    text = render_month(build_month_report(conn, 2026, 10))
    assert "▲" not in text and "▼" not in text


def test_saved_is_save_minus_take(conn):
    apply_pot_entry(conn, parse_entry("save 400 emergency 05.10", TODAY))
    apply_pot_entry(conn, parse_entry("take 100 emergency 06.10", TODAY))
    report = build_month_report(conn, 2026, 10)
    assert (report.saved_cents, report.net_cents) == (30000, -30000)


def test_income_only_month_has_only_header_and_totals(conn):
    _add(conn, "+1000 salary 01.10")
    assert len(render_month(build_month_report(conn, 2026, 10)).split("\n\n")) == 2


def test_top_expenses_are_the_five_largest_then_by_date(conn):
    _add(conn, "600 food 02.10")
    _add(conn, "500 food 03.10")
    _add(conn, "400 food 04.10")
    _add(conn, "300 food 05.10")
    _add(conn, "200 food 06.10")
    _add(conn, "200 food 01.10")
    _add(conn, "100 food 07.10")
    top = build_month_report(conn, 2026, 10).top
    assert [(r.on.day, r.eur_cents) for r in top] == [
        (2, 60000),
        (3, 50000),
        (4, 40000),
        (5, 30000),
        (1, 20000),
    ]


def test_percentages_round_half_up(conn):
    _remember_keywords(conn)
    _add(conn, "700 rent 01.10")
    _add(conn, "100 billa 02.10")
    text = render_month(build_month_report(conn, 2026, 10))
    assert _line(text, "Groceries").endswith("  13%")
    assert _line(text, "Housing").endswith("  88%")


def test_expense_without_category_is_grouped_as_uncategorized(conn):
    _add(conn, "500 coffee 02.10")
    assert build_month_report(conn, 2026, 10).by_category == [("Uncategorized", 50000)]


def test_pot_without_goal_shows_total_only(conn):
    apply_pot_entry(conn, parse_entry("save 200 travel 05.10", TODAY))
    assert render_month(build_month_report(conn, 2026, 10)).endswith("Savings\nTravel  200.00")


def test_month_with_only_a_save_and_take_renders_totals(conn):
    apply_pot_entry(conn, parse_entry("save 100 emergency 05.10", TODAY))
    apply_pot_entry(conn, parse_entry("take 100 emergency 06.10", TODAY))
    assert render_month(build_month_report(conn, 2026, 10)) == (
        "October 2026\n\n"
        "Income 0.00 EUR\n"
        "Spent  0.00 EUR\n"
        "Saved  0.00 EUR\n"
        "Net    0.00 EUR\n\n"
        "Savings\n"
        "Emergency  0.00"
    )


def test_pending_only_month_renders_zero_totals_and_the_note(conn):
    _add(conn, "25 usd book")
    assert render_month(build_month_report(conn, 2026, 10)) == (
        "October 2026\n\n"
        "Income 0.00 EUR\n"
        "Spent  0.00 EUR\n"
        "Saved  0.00 EUR\n"
        "Net    0.00 EUR\n\n"
        "Not counted: 1 pending (no rate). Use /rate to convert."
    )


def test_empty_month_says_no_entries_even_when_pots_exist(conn):
    apply_pot_entry(conn, parse_entry("save 200 emergency 15.09", TODAY))
    assert render_month(build_month_report(conn, 2026, 10)) == "October 2026\n\nNo entries."


def test_january_compares_with_december_of_the_previous_year(conn):
    _add(conn, "300 rent 15.12.2025")
    _add(conn, "400 rent 03.01")
    assert "▲ 33% vs Dec" in render_month(build_month_report(conn, 2026, 1))


def test_category_bar_is_at_least_one_block(conn):
    _remember_keywords(conn)
    _add(conn, "100 rent 01.10")
    _add(conn, "1 billa 02.10")
    text = render_month(build_month_report(conn, 2026, 10))
    assert _line(text, "Groceries") == "Groceries    1.00  █" + " " * 13 + "1%"


def _set_budget(conn, name: str, cents: int) -> None:
    category = find_category(conn, name)
    assert category is not None
    set_budget(conn, category, cents, 2026, 10)


def test_month_report_lists_budgets_after_the_categories_in_position_order(conn):
    _golden_month(conn)
    _set_budget(conn, "Housing", 85000)
    _set_budget(conn, "Groceries", 50000)
    _set_budget(conn, "Eating out", 31000)
    assert render_month(build_month_report(conn, 2026, 10)) == GOLDEN.replace(
        "\n\nTop expenses",
        "\n\nBudgets\n"
        "Groceries: 420.00 of 500.00 · 80.00 left\n"
        "Eating out: 310.00 of 310.00 · 0.00 left\n"
        "Housing: 930.00 of 850.00 · over by 80.00\n\nTop expenses",
    )


def test_month_report_budgets_are_for_the_month_of_the_report(conn):
    _golden_month(conn)
    add_transaction(conn, parse_entry("100 rent 05.11", date(2026, 11, 20)))
    _set_budget(conn, "Housing", 85000)
    october = render_month(build_month_report(conn, 2026, 10))
    november = render_month(build_month_report(conn, 2026, 11))
    assert "Housing: 930.00 of 850.00 · over by 80.00" in october
    assert "Budgets\nHousing: 100.00 of 850.00 · 750.00 left" in november


def test_month_report_without_budgets_has_no_budgets_block(conn):
    _golden_month(conn)
    assert "Budgets" not in render_month(build_month_report(conn, 2026, 10))


def test_month_report_budgets_show_when_the_month_has_no_expenses(conn):
    _add(conn, "+1000 salary 01.10")
    _set_budget(conn, "Housing", 85000)
    assert render_month(build_month_report(conn, 2026, 10)).endswith(
        "\n\nBudgets\nHousing: 0.00 of 850.00 · 850.00 left"
    )


def test_month_without_entries_has_no_budgets_block_even_with_budgets(conn):
    _set_budget(conn, "Housing", 85000)
    assert render_month(build_month_report(conn, 2026, 10)) == "October 2026\n\nNo entries."


def test_month_report_budgets_come_before_savings_and_the_pending_note(conn):
    _golden_month(conn)
    _add(conn, "25 usd book")
    _set_budget(conn, "Housing", 85000)
    text = render_month(build_month_report(conn, 2026, 10))
    assert text.index("Budgets") < text.index("Top expenses") < text.index("Savings")
    assert text.endswith("Not counted: 1 pending (no rate). Use /rate to convert.")
