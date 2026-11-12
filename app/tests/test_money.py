from decimal import Decimal

import pytest

from finbot.money import format_cents, parse_amount, signed, to_eur


@pytest.mark.parametrize(
    "text,cents",
    [("25", 2500), ("12,50", 1250), ("12.5", 1250), ("0.01", 1), ("10000000", 1_000_000_000)],
)
def test_parse_amount(text, cents):
    assert parse_amount(text) == cents


@pytest.mark.parametrize(
    "text",
    ["", "0", "-5", "1.234", "1,2,3", "10000000.01", "abc", "1e3", "1 200"],
)
def test_parse_amount_rejects(text):
    with pytest.raises(ValueError):
        parse_amount(text)


def test_format():
    assert (format_cents(120000), format_cents(-2500), format_cents(5)) == (
        "1,200.00",
        "-25.00",
        "0.05",
    )


def test_signed():
    assert (signed(2500, False), signed(300000, True)) == ("-25.00", "+3,000.00")


def test_to_eur():
    assert (
        to_eur(120000, Decimal("0.0220")),
        to_eur(2500, Decimal("0.92")),
        to_eur(1, Decimal("0.5")),
    ) == (2640, 2300, 1)
