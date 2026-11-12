import re
from decimal import ROUND_HALF_UP, Decimal

CURRENCIES = ("EUR", "USD", "UAH")
SYMBOLS = {"€": "EUR", "$": "USD", "₴": "UAH"}
MAX_CENTS = 1_000_000_000


def parse_amount(text: str) -> int:
    if not re.fullmatch(r"\d+([.,]\d{1,2})?", text):
        raise ValueError(f"not an amount: {text!r}")
    cents = int(Decimal(text.replace(",", ".")) * 100)
    if not 0 < cents <= MAX_CENTS:
        raise ValueError(f"amount out of range: {text!r}")
    return cents


def format_cents(cents: int) -> str:
    whole, frac = divmod(abs(cents), 100)
    sign = "-" if cents < 0 else ""
    return f"{sign}{whole:,}.{frac:02d}"


def signed(cents: int, positive: bool) -> str:
    return ("+" if positive else "-") + format_cents(abs(cents))


def to_eur(cents: int, rate: Decimal) -> int:
    return int((cents * rate).quantize(Decimal(1), rounding=ROUND_HALF_UP))
