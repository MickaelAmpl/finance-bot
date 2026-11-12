from collections.abc import Iterator, Mapping
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from finbot.ai_tools import SCHEMA_KEYWORDS, TOOLS, run_read_tool
from finbot.categories import find_category, remember_keyword
from finbot.ledger import add_transaction, delete_entry
from finbot.parser import parse_entry
from finbot.rates import set_rate
from finbot.reports import build_month_report, render_month
from finbot.savings import apply_pot_entry, list_pots, recent_moves
from finbot.texts import savings_text

TODAY = date(2026, 11, 12)


def _add(conn, text: str) -> None:
    add_transaction(conn, parse_entry(text, TODAY))


def _schemas(
    schema: Mapping[str, Any], path: str = "input"
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    yield path, schema
    for name, sub in schema.get("properties", {}).items():
        yield from _schemas(sub, f"{path}.{name}")
    if "items" in schema:
        yield from _schemas(schema["items"], f"{path}[]")


def test_tools_are_the_four_planned_tools_in_order():
    assert [tool["name"] for tool in TOOLS] == [
        "propose_entries",
        "month_summary",
        "list_entries",
        "savings",
    ]


def test_tool_descriptions_match_the_plan():
    descriptions = {tool["name"]: tool.get("description") for tool in TOOLS}
    assert descriptions == {
        "propose_entries": "Draft 1 to 10 ledger entries for the user to confirm. Nothing is saved "
        "until the user presses Save. Use it only for expenses or income the user states or shows "
        "on a receipt.",
        "month_summary": "The same report as /month for one calendar month: totals, categories, "
        "budgets, top expenses, savings pots.",
        "list_entries": "Expenses and incomes between two dates inclusive. "
        "The first line holds the totals over all matching entries; "
        "then up to 100 entries, newest first.",
        "savings": "The same text as /savings: pots, totals, goals, recent moves.",
    }


def test_every_tool_is_strict():
    assert all(tool.get("strict") is True for tool in TOOLS)


def test_schemas_use_only_known_keywords():
    for tool in TOOLS:
        for path, schema in _schemas(tool["input_schema"]):
            unknown = set(schema) - SCHEMA_KEYWORDS
            assert not unknown, f"{tool['name']} {path} has {unknown}"


def test_min_items_is_zero_or_one_and_objects_forbid_extra_keys():
    for tool in TOOLS:
        for path, schema in _schemas(tool["input_schema"]):
            if "minItems" in schema:
                assert schema["minItems"] in (0, 1), f"{tool['name']} {path}"
            if "properties" in schema:
                assert schema.get("additionalProperties") is False, f"{tool['name']} {path}"


def test_only_list_entries_filters_are_optional():
    optional = {
        (tool["name"], path, key)
        for tool in TOOLS
        for path, schema in _schemas(tool["input_schema"])
        for key in set(schema.get("properties", {})) - set(schema.get("required", []))
    }
    assert optional == {("list_entries", "input", "category"), ("list_entries", "input", "text")}


def test_month_summary_equals_the_month_report(conn):
    _add(conn, "1000 rent 05.10")
    _add(conn, "+3000 salary 01.10")
    text, is_error = run_read_tool(conn, "month_summary", {"month": "2026-10"}, TODAY)
    assert is_error is False
    assert text == render_month(build_month_report(conn, 2026, 10))


def test_month_summary_rejects_bad_months(conn):
    for month in ("2026-13", "2026-00", "10-2026", "2026-1", "0000-10"):
        assert run_read_tool(conn, "month_summary", {"month": month}, TODAY) == (
            "month must be YYYY-MM",
            True,
        )


def test_list_entries_totals_and_caps_lines_at_100(conn):
    for amount in range(1, 106):
        _add(conn, f"{amount} snack 02.11")
    lines = run_read_tool(
        conn, "list_entries", {"start": "2026-11-01", "end": "2026-11-30"}, TODAY
    )[0].splitlines()
    assert lines[0] == "Spent 5,565.00 EUR, income 0.00 EUR, 105 entries"
    assert lines[1] == "02.11.2026 expense 105.00 EUR · no category · snack"
    assert lines[-1] == "first 100 of 105"
    assert len(lines) == 102


def test_list_entries_lists_pending_without_counting_them(conn):
    set_rate(conn, "USD", Decimal("0.9"), date(2026, 11, 5))
    _add(conn, "12.40 USD taxi 03.11")
    _add(conn, "300 uah dinner 03.11")
    _add(conn, "+100 usd gift 04.11")
    _add(conn, "20 coffee 04.11")
    _add(conn, "10 usd tea 06.11")
    _add(conn, "+500 salary 06.11")
    text, is_error = run_read_tool(
        conn, "list_entries", {"start": "2026-11-01", "end": "2026-11-30"}, TODAY
    )
    assert is_error is False
    assert text == "\n".join(
        [
            "Spent 29.00 EUR, income 500.00 EUR, 6 entries; 3 without a rate, not counted: "
            "-12.40 USD, -300.00 UAH, +100.00 USD",
            "06.11.2026 income 500.00 EUR · no category · salary",
            "06.11.2026 expense 10.00 USD (9.00 EUR) · no category · tea",
            "04.11.2026 expense 20.00 EUR · no category · coffee",
            "04.11.2026 income 100.00 USD (no rate) · no category · gift",
            "03.11.2026 expense 300.00 UAH (no rate) · no category · dinner",
            "03.11.2026 expense 12.40 USD (no rate) · no category · taxi",
        ]
    )


def test_list_entries_skips_pot_moves_and_deleted_entries(conn):
    apply_pot_entry(conn, parse_entry("save 100 emergency 05.11", TODAY))
    _add(conn, "7 coffee 05.11")
    delete_entry(conn, 2)
    text, _ = run_read_tool(
        conn, "list_entries", {"start": "2026-11-05", "end": "2026-11-05"}, TODAY
    )
    assert text == "Spent 0.00 EUR, income 0.00 EUR, 0 entries"


def test_list_entries_category_filter_ignores_case(conn):
    groceries = find_category(conn, "Groceries")
    assert groceries is not None
    remember_keyword(conn, "billa", groceries.id)
    _add(conn, "10 billa 05.11")
    _add(conn, "5 tea 05.11")
    text, _ = run_read_tool(
        conn,
        "list_entries",
        {"start": "2026-11-05", "end": "2026-11-05", "category": "GROCERIES"},
        TODAY,
    )
    assert text.splitlines()[0] == "Spent 10.00 EUR, income 0.00 EUR, 1 entries"
    assert "Groceries · billa" in text
    assert "tea" not in text


def test_list_entries_text_filter_ignores_case(conn):
    _add(conn, "120 кофе с другом 05.11")
    _add(conn, "5 tea 05.11")
    text, _ = run_read_tool(
        conn, "list_entries", {"start": "2026-11-05", "end": "2026-11-05", "text": "КОФЕ"}, TODAY
    )
    assert text.splitlines() == [
        "Spent 120.00 EUR, income 0.00 EUR, 1 entries",
        "05.11.2026 expense 120.00 EUR · no category · кофе с другом",
    ]


def test_list_entries_dates_are_inclusive(conn):
    _add(conn, "1 a 01.11")
    _add(conn, "2 b 05.11")
    _add(conn, "3 c 06.11")
    text, _ = run_read_tool(
        conn, "list_entries", {"start": "2026-11-01", "end": "2026-11-05"}, TODAY
    )
    assert text.splitlines()[0] == "Spent 3.00 EUR, income 0.00 EUR, 2 entries"


def test_list_entries_errors(conn):
    cases = [
        ({"start": "05.11.2026", "end": "2026-11-05"}, "dates must be YYYY-MM-DD"),
        ({"start": "2026-11-05", "end": "2026-11-01"}, "end is before start"),
        (
            {"start": "2026-11-01", "end": "2026-11-05", "category": "Nope"},
            "unknown category Nope",
        ),
    ]
    for args, message in cases:
        assert run_read_tool(conn, "list_entries", args, TODAY) == (message, True)


def test_savings_equals_the_savings_text(conn):
    apply_pot_entry(conn, parse_entry("save 100 emergency 05.11", TODAY))
    pots = list_pots(conn)
    expected = savings_text(pots, {p.id: recent_moves(conn, p.id) for p in pots}, TODAY)
    assert run_read_tool(conn, "savings", {}, TODAY) == (expected, False)


def test_unknown_tool_is_an_error(conn):
    assert run_read_tool(conn, "nope", {}, TODAY) == ("unknown tool nope", True)


@pytest.mark.parametrize("args", [{}, {"month": None}, {"month": 202610}])
def test_month_summary_missing_or_non_string_month_is_an_error(conn, args):
    assert run_read_tool(conn, "month_summary", args, TODAY) == ("month must be YYYY-MM", True)


@pytest.mark.parametrize(
    "args",
    [
        {"end": "2026-11-05"},
        {"start": None, "end": "2026-11-05"},
        {"start": 20261101, "end": "2026-11-05"},
        {"start": "2026-11-01"},
        {"start": "2026-11-01", "end": None},
    ],
)
def test_list_entries_missing_or_non_string_dates_are_errors(conn, args):
    assert run_read_tool(conn, "list_entries", args, TODAY) == ("dates must be YYYY-MM-DD", True)


def test_blank_or_null_category_and_text_count_as_absent(conn):
    _add(conn, "10 coffee 05.11")
    _add(conn, "5 tea 05.11")
    extras = [
        {"category": ""},
        {"category": None},
        {"category": "   "},
        {"text": None},
        {"text": "  "},
        {"category": None, "text": ""},
    ]
    for extra in extras:
        args = {"start": "2026-11-05", "end": "2026-11-05", **extra}
        text, is_error = run_read_tool(conn, "list_entries", args, TODAY)
        assert is_error is False
        assert text.splitlines()[0] == "Spent 15.00 EUR, income 0.00 EUR, 2 entries"


def test_category_name_is_stripped(conn):
    transport = find_category(conn, "Transport")
    assert transport is not None
    remember_keyword(conn, "ticket", transport.id)
    _add(conn, "15 ticket 05.11")
    _add(conn, "5 tea 05.11")
    text, _ = run_read_tool(
        conn,
        "list_entries",
        {"start": "2026-11-05", "end": "2026-11-05", "category": "  transport  "},
        TODAY,
    )
    assert text.splitlines()[0] == "Spent 15.00 EUR, income 0.00 EUR, 1 entries"


def test_income_under_a_category_filter_is_counted_as_income(conn):
    salary = find_category(conn, "Salary")
    assert salary is not None
    remember_keyword(conn, "salary", salary.id)
    _add(conn, "+500 salary 05.11")
    _add(conn, "10 tea 05.11")
    text, _ = run_read_tool(
        conn,
        "list_entries",
        {"start": "2026-11-05", "end": "2026-11-05", "category": "Salary"},
        TODAY,
    )
    assert text.splitlines() == [
        "Spent 0.00 EUR, income 500.00 EUR, 1 entries",
        "05.11.2026 income 500.00 EUR · Salary · salary",
    ]


def test_usd_with_rate_under_a_category_filter_shows_eur_and_counts(conn):
    set_rate(conn, "USD", Decimal("0.9"), date(2026, 11, 1))
    transport = find_category(conn, "Transport")
    assert transport is not None
    remember_keyword(conn, "ticket", transport.id)
    _add(conn, "10 usd ticket 05.11")
    _add(conn, "5 tea 05.11")
    text, _ = run_read_tool(
        conn,
        "list_entries",
        {"start": "2026-11-05", "end": "2026-11-05", "category": "Transport"},
        TODAY,
    )
    assert text.splitlines() == [
        "Spent 9.00 EUR, income 0.00 EUR, 1 entries",
        "05.11.2026 expense 10.00 USD (9.00 EUR) · Transport · ticket",
    ]
