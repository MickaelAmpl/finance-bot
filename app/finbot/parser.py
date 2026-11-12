import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from finbot.money import CURRENCIES, SYMBOLS, parse_amount

Kind = Literal["expense", "income", "save", "take"]
UNSUPPORTED = ("GBP", "CHF", "PLN", "CZK", "HUF", "TRY", "JPY")

START_MSG = "Start with the amount, e.g. 25 coffee"
NOTE_MSG = "Add a word after the amount, e.g. 25 coffee"
AMOUNT_MSG = "Amount must be like 25 or 12,50"
SPLIT_MSG = "Write 1200 without spaces, e.g. 1200 taxi"
DATE_MSG = "Use a date like 28.10 or 28.10.2026"
POT_MSG = "Use: save 200 emergency"
POT_EUR_MSG = "Pots are in EUR for now"
POT_LONG_MSG = "Pot name up to 30 letters, e.g. save 200 emergency"
NOTE_LONG_MSG = "Keep the note under 100 characters, e.g. 25 coffee"
FUTURE_DATE_MSG = "That date is in the future. Use a date like 28.10 or 28.10.2026"
CURRENCY_MSG = "Put the currency right after the amount, e.g. 1200 uah taxi"
MAX_ENTRIES = 10
TOO_MANY_MSG = (
    f"Up to {MAX_ENTRIES} entries in one message. Nothing saved: send them in two messages."
)
QUOTED_PART_MAX = 40
DATE_RE = re.compile(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?")
SPLIT_RE = re.compile(r"\d+(?:[.,]\d+)?")
# A comma starts a new entry only when an amount follows: a pot move always has one.
_AMOUNT_START = rf"[{re.escape(''.join(SYMBOLS))}]?\d"
ENTRY_START_RE = re.compile(
    rf", +(?=\+?{_AMOUNT_START}|(?:save|take) +{_AMOUNT_START})", re.IGNORECASE
)


@dataclass(frozen=True)
class Entry:
    kind: Kind
    amount_cents: int
    currency: str
    note: str
    keyword: str
    pot: str | None
    on: date


class ParseError(ValueError):
    """The message is shown to the user as is."""


def parse_entry(text: str, today: date) -> Entry:
    tokens = text.split()
    if not tokens:
        raise ParseError(START_MSG)
    if tokens[0].lower() in ("save", "take"):
        return _parse_pot(tokens, today)
    return _parse_expense(tokens, today)


def parse_entries(text: str, today: date) -> list[Entry]:
    parts = _split_parts(text)
    if len(parts) <= 1:
        return [parse_entry(text, today)]
    if len(parts) > MAX_ENTRIES:
        raise ParseError(TOO_MANY_MSG)
    entries: list[Entry] = []
    for number, part in enumerate(parts, start=1):
        try:
            entries.append(parse_entry(part, today))
        except ParseError as error:
            shown = part if len(part) <= QUOTED_PART_MAX else part[: QUOTED_PART_MAX - 1] + "…"
            raise ParseError(f'Nothing saved. Entry {number} "{shown}": {error}') from None
    return entries


def _split_parts(text: str) -> list[str]:
    pieces = (piece for line in text.splitlines() for piece in ENTRY_START_RE.split(line))
    parts = (piece.strip().removesuffix(",").strip() for piece in pieces)
    return [part for part in parts if part]


def _parse_expense(tokens: list[str], today: date) -> Entry:
    first = tokens[0]
    income = first.startswith("+")
    attached, body = _split_symbol(first[1:] if income else first)
    # No digit at all means a word came first, so the start message is the accurate one.
    if not any(ch.isdigit() for ch in body):
        raise ParseError(START_MSG)
    cents = _cents(body, AMOUNT_MSG)

    rest = tokens[1:]
    code = _currency_code(rest[0]) if rest else None
    if code in UNSUPPORTED:
        raise ParseError(f"{code} is not supported. Use EUR, USD or UAH")
    currency = attached or "EUR"
    if code is not None and attached in (None, code):
        currency = code
        rest = rest[1:]
    if not rest:
        raise ParseError(NOTE_MSG)

    # Runs before the split-number check so that a mistyped date reports the date error.
    rest, on = _take_date(rest, today)
    _, number = _split_symbol(rest[0])
    if SPLIT_RE.fullmatch(number):
        raise ParseError(SPLIT_MSG)
    # A currency typed after the note would otherwise be saved as EUR silently.
    if _currency_code(rest[-1]) is not None:
        raise ParseError(CURRENCY_MSG)
    note = " ".join(rest)
    if len(note) > 100:
        raise ParseError(NOTE_LONG_MSG)
    kind: Kind = "income" if income else "expense"
    return Entry(kind, cents, currency, note, rest[0].lower(), None, on)


def _parse_pot(tokens: list[str], today: date) -> Entry:
    kind: Kind = "save" if tokens[0].lower() == "save" else "take"
    rest = tokens[1:]
    if not rest:
        raise ParseError(POT_MSG)
    attached, body = _split_symbol(rest[0])
    cents = _cents(body, POT_MSG)
    rest = rest[1:]
    code = _currency_code(rest[0]) if rest else None
    if attached not in (None, "EUR") or code not in (None, "EUR"):
        raise ParseError(POT_EUR_MSG)
    if code == "EUR":
        rest = rest[1:]
    rest, on = _take_date(rest, today)
    if len(rest) != 1 or not any(ch.isalpha() for ch in rest[0]):
        raise ParseError(POT_MSG)
    if len(rest[0]) > 30:
        raise ParseError(POT_LONG_MSG)
    return Entry(kind, cents, "EUR", "", "", rest[0].lower(), on)


def _split_symbol(token: str) -> tuple[str | None, str]:
    if token[:1] in SYMBOLS:
        return SYMBOLS[token[:1]], token[1:]
    if token[-1:] in SYMBOLS:
        return SYMBOLS[token[-1:]], token[:-1]
    return None, token


def _currency_code(token: str) -> str | None:
    if token in SYMBOLS:
        return SYMBOLS[token]
    code = token.upper()
    return code if code in CURRENCIES or code in UNSUPPORTED else None


def _cents(text: str, message: str) -> int:
    try:
        return parse_amount(text)
    except ValueError:
        raise ParseError(message) from None


def _take_date(words: list[str], today: date) -> tuple[list[str], date]:
    # A valid date is taken only when a word remains before it: "25 yesterday" keeps its note.
    found = _date_word(words[-1], today) if words else None
    if found is not None and len(words) >= 2:
        return words[:-1], found
    return words, today


def _date_word(word: str, today: date) -> date | None:
    if word.lower() == "yesterday":
        return today - timedelta(days=1)
    match = DATE_RE.fullmatch(word)
    if match is None:
        return None
    day, month, year = match.groups()
    if len(day) != 2 or len(month) != 2 or (year is not None and len(year) != 4):
        raise ParseError(DATE_MSG)
    dd, mm = int(day), int(month)
    if year is None:
        return _latest_past_day(dd, mm, today)
    # Outside the try: ParseError is a ValueError and must not be turned into DATE_MSG.
    try:
        on = date(int(year), mm, dd)
    except ValueError:
        raise ParseError(DATE_MSG) from None
    if on > today:
        raise ParseError(FUTURE_DATE_MSG)
    return on


def _latest_past_day(day: int, month: int, today: date) -> date:
    # Feb 29 exists only in leap years, so look back up to 4 years for one that does.
    for year in range(today.year, today.year - 5, -1):
        try:
            on = date(year, month, day)
        except ValueError:
            continue
        if on <= today:
            return on
    raise ParseError(DATE_MSG)
