from datetime import date
from decimal import Decimal

import pytest

from finbot.rates import RateError, check_rate, parse_rate, rate_on, set_rate


def _entry(
    conn, currency, amount_cents, *, kind="expense", eur_cents=None, rate=None, deleted_at=None
):
    with conn:
        cur = conn.execute(
            "INSERT INTO entries (kind, amount_cents, currency, eur_cents, rate, occurred_on,"
            " deleted_at) VALUES (?, ?, ?, ?, ?, '2026-10-20', ?)",
            (kind, amount_cents, currency, eur_cents, rate, deleted_at),
        )
    return cur.lastrowid


def _row(conn, entry_id):
    return conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()


@pytest.mark.parametrize(
    "text,rate",
    [("0.92", Decimal("0.92")), ("0,022", Decimal("0.022")), ("0.123456", Decimal("0.123456"))],
)
def test_parse_rate(text, rate):
    assert parse_rate(text) == rate


@pytest.mark.parametrize(
    "text", ["0", "0.000", "-1", "abc", "0.1234567", "", "1.", ".5", "+1", "1e3", "1 200"]
)
def test_parse_rate_rejects(text):
    with pytest.raises(ValueError):
        parse_rate(text)


@pytest.mark.parametrize(
    ("currency", "rate"),
    [
        ("USD", Decimal("0.5")),
        ("USD", Decimal("2")),
        ("UAH", Decimal("0.005")),
        ("UAH", Decimal("0.1")),
    ],
)
def test_check_rate_accepts_the_range_limits(currency, rate):
    check_rate(currency, rate)


@pytest.mark.parametrize(
    ("currency", "rate", "message"),
    [
        (
            "USD",
            Decimal("0.4"),
            "That rate looks wrong: 1 USD should be between 0.5 and 2 EUR. Example: /rate usd 0.92",
        ),
        (
            "USD",
            Decimal("2.01"),
            "That rate looks wrong: 1 USD should be between 0.5 and 2 EUR. Example: /rate usd 0.92",
        ),
        (
            "UAH",
            Decimal("0.000001"),
            "That rate looks wrong: 1 UAH should be between 0.005 and 0.1 EUR."
            " Example: /rate uah 0.022",
        ),
        (
            "UAH",
            Decimal("0.2"),
            "That rate looks wrong: 1 UAH should be between 0.005 and 0.1 EUR."
            " Example: /rate uah 0.022",
        ),
    ],
)
def test_check_rate_rejects_values_outside_the_range_with_an_example(currency, rate, message):
    with pytest.raises(RateError) as error:
        check_rate(currency, rate)

    assert str(error.value) == message


def test_rate_is_none_before_any_rate(conn):
    assert rate_on(conn, "USD", date(2026, 11, 5)) is None


def test_rate_applies_from_its_date_and_only_to_its_currency(conn):
    set_rate(conn, "USD", Decimal("0.92"), date(2026, 11, 1))
    assert rate_on(conn, "USD", date(2026, 11, 5)) == Decimal("0.92")
    assert rate_on(conn, "USD", date(2026, 10, 31)) is None
    assert rate_on(conn, "UAH", date(2026, 11, 5)) is None


def test_latest_rate_on_or_before_the_date_wins(conn):
    set_rate(conn, "USD", Decimal("0.92"), date(2026, 11, 1))
    set_rate(conn, "USD", Decimal("0.93"), date(2026, 11, 3))
    assert rate_on(conn, "USD", date(2026, 11, 2)) == Decimal("0.92")
    assert rate_on(conn, "USD", date(2026, 11, 4)) == Decimal("0.93")


def test_same_day_rates_use_the_later_one(conn):
    set_rate(conn, "USD", Decimal("0.92"), date(2026, 11, 1))
    set_rate(conn, "USD", Decimal("0.93"), date(2026, 11, 1))
    assert rate_on(conn, "USD", date(2026, 11, 1)) == Decimal("0.93")


def test_set_rate_stores_the_rate_as_typed(conn):
    set_rate(conn, "USD", parse_rate("0.0220"), date(2026, 11, 1))
    assert conn.execute("SELECT eur_per_unit FROM rates").fetchone()[0] == "0.0220"


def test_set_rate_converts_pending_entries_of_that_currency_whatever_their_date(conn):
    pending = _entry(conn, "USD", 2500)
    uah = _entry(conn, "UAH", 2500)
    deleted = _entry(conn, "USD", 4000, deleted_at="2026-10-25T00:00:00Z")

    assert set_rate(conn, "USD", Decimal("0.92"), date(2026, 11, 1)) == [pending]

    assert (_row(conn, pending)["eur_cents"], _row(conn, pending)["rate"]) == (2300, "0.92")
    assert (_row(conn, uah)["eur_cents"], _row(conn, uah)["rate"]) == (None, None)
    assert (_row(conn, deleted)["eur_cents"], _row(conn, deleted)["rate"]) == (None, None)


def test_set_rate_converts_pending_income_too(conn):
    income = _entry(conn, "USD", 2500, kind="income")

    assert set_rate(conn, "USD", Decimal("0.92"), date(2026, 11, 1)) == [income]

    assert (_row(conn, income)["eur_cents"], _row(conn, income)["rate"]) == (2300, "0.92")


def test_set_rate_leaves_already_converted_entries_alone(conn):
    entry = _entry(conn, "USD", 1000, eur_cents=400, rate="0.40")

    assert set_rate(conn, "USD", Decimal("0.92"), date(2026, 11, 1)) == []

    assert (_row(conn, entry)["eur_cents"], _row(conn, entry)["rate"]) == (400, "0.40")


def test_set_rate_returns_the_converted_ids_in_id_order(conn):
    first = _entry(conn, "USD", 2500)
    second = _entry(conn, "USD", 1000)

    assert set_rate(conn, "USD", Decimal("0.92"), date(2026, 11, 1)) == [first, second]


def test_set_rate_is_all_or_nothing(conn, monkeypatch):
    first = _entry(conn, "USD", 2500)
    second = _entry(conn, "USD", 1000)
    calls = []

    def fail_on_second(cents, rate):
        calls.append(cents)
        if len(calls) == 2:
            raise RuntimeError("boom")
        return 1

    monkeypatch.setattr("finbot.rates.to_eur", fail_on_second)

    with pytest.raises(RuntimeError):
        set_rate(conn, "USD", Decimal("0.92"), date(2026, 11, 1))

    assert rate_on(conn, "USD", date(2026, 11, 2)) is None
    assert (_row(conn, first)["eur_cents"], _row(conn, second)["eur_cents"]) == (None, None)
