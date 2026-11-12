import re
import sqlite3
from collections import defaultdict
from collections.abc import Mapping
from datetime import date
from typing import Any

from anthropic.types import ToolParam

from finbot.categories import find_category
from finbot.ledger import Record, records_between
from finbot.money import format_cents, signed
from finbot.reports import build_month_report, render_month
from finbot.savings import list_pots, recent_moves
from finbot.texts import savings_text

SCHEMA_KEYWORDS = {
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "enum",
    "description",
    "format",
    "pattern",
    "minItems",
}
MAX_LISTED = 100
_MONTH = re.compile(r"([0-9]{4})-([0-9]{2})")
_DAY = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_PENDING_ORDER = (
    ("expense", "USD"),
    ("expense", "UAH"),
    ("income", "USD"),
    ("income", "UAH"),
)

_ENTRY = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": ["expense", "income"]},
        "amount": {
            "type": "string",
            "pattern": r"^[0-9]+(\.[0-9]{1,2})?$",
            "description": "Positive amount, dot as decimal separator, no currency, "
            "no thousands separator, e.g. 12.50",
        },
        "currency": {"type": "string", "enum": ["EUR", "USD", "UAH"]},
        "category": {
            "type": "string",
            "description": "Exact category name for this kind from the system prompt, "
            "or an empty string",
        },
        "note": {
            "type": "string",
            "description": "The words that describe it, in the user's language, "
            "under 100 characters",
        },
        "date": {"type": "string", "format": "date"},
    },
    "required": ["kind", "amount", "currency", "category", "note", "date"],
    "additionalProperties": False,
}

TOOLS: list[ToolParam] = [
    {
        "name": "propose_entries",
        "description": "Draft 1 to 10 ledger entries for the user to confirm. Nothing is saved "
        "until the user presses Save. Use it only for expenses or income the user states or shows "
        "on a receipt.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "entries": {"type": "array", "minItems": 1, "items": _ENTRY},
                "replaces_open_draft": {
                    "type": "boolean",
                    "description": "true only when this corrects the draft that is still open",
                },
            },
            "required": ["entries", "replaces_open_draft"],
            "additionalProperties": False,
        },
    },
    {
        "name": "month_summary",
        "description": "The same report as /month for one calendar month: totals, categories, "
        "budgets, top expenses, savings pots.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"month": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}$"}},
            "required": ["month"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_entries",
        "description": "Expenses and incomes between two dates inclusive. The first line holds the "
        "totals over all matching entries; then up to 100 entries, newest first.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "start": {"type": "string", "format": "date"},
                "end": {"type": "string", "format": "date"},
                "category": {"type": "string", "description": "Only this category"},
                "text": {
                    "type": "string",
                    "description": "Only entries whose note contains this text",
                },
            },
            "required": ["start", "end"],
            "additionalProperties": False,
        },
    },
    {
        "name": "savings",
        "description": "The same text as /savings: pots, totals, goals, recent moves.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
]


def run_read_tool(
    conn: sqlite3.Connection, name: str, args: Mapping[str, Any], today: date
) -> tuple[str, bool]:
    if name == "month_summary":
        return _month_summary(conn, args.get("month"))
    if name == "list_entries":
        return _list_entries(conn, args)
    if name == "savings":
        pots = list_pots(conn)
        moves = {pot.id: recent_moves(conn, pot.id) for pot in pots}
        return savings_text(pots, moves, today), False
    return f"unknown tool {name}", True


def _month_summary(conn: sqlite3.Connection, month: object) -> tuple[str, bool]:
    match = _MONTH.fullmatch(month) if isinstance(month, str) else None
    if match is None:
        return "month must be YYYY-MM", True
    year, number = int(match[1]), int(match[2])
    if year < 1 or not 1 <= number <= 12:
        return "month must be YYYY-MM", True
    return render_month(build_month_report(conn, year, number)), False


def _list_entries(conn: sqlite3.Connection, args: Mapping[str, Any]) -> tuple[str, bool]:
    start, end = _parse_day(args.get("start")), _parse_day(args.get("end"))
    if start is None or end is None:
        return "dates must be YYYY-MM-DD", True
    if end < start:
        return "end is before start", True
    category = _text_arg(args, "category")
    found = None
    if category:
        found = find_category(conn, category)
        if found is None:
            return f"unknown category {category}", True
    wanted = _text_arg(args, "text").casefold()
    matching = [
        r
        for r in records_between(conn, start, end)
        if r.kind in ("expense", "income")
        and (found is None or r.category == found.name)
        and wanted in r.note.casefold()
    ]
    ordered = sorted(matching, key=lambda r: (r.on, r.id), reverse=True)
    lines = [_totals(matching)]
    lines.extend(_entry_line(r) for r in ordered[:MAX_LISTED])
    if len(ordered) > MAX_LISTED:
        lines.append(f"first {MAX_LISTED} of {len(ordered)}")
    return "\n".join(lines), False


def _text_arg(args: Mapping[str, Any], key: str) -> str:
    value = args.get(key)
    return value.strip() if isinstance(value, str) else ""


def _parse_day(value: object) -> date | None:
    if not isinstance(value, str) or not _DAY.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _totals(matching: list[Record]) -> str:
    spent = _eur_total(matching, "expense")
    income = _eur_total(matching, "income")
    head = (
        f"Spent {format_cents(spent)} EUR, income {format_cents(income)} EUR, "
        f"{len(matching)} entries"
    )
    pending = [r for r in matching if r.pending]
    if pending:
        head += f"; {len(pending)} without a rate, not counted: {_pending_sums(pending)}"
    return head


def _eur_total(matching: list[Record], kind: str) -> int:
    return sum(r.eur_cents for r in matching if r.kind == kind and r.eur_cents is not None)


def _pending_sums(pending: list[Record]) -> str:
    sums: defaultdict[tuple[str, str], int] = defaultdict(int)
    for r in pending:
        sums[(r.kind, r.currency)] += r.amount_cents
    return ", ".join(
        f"{signed(sums[key], key[0] == 'income')} {key[1]}" for key in _PENDING_ORDER if key in sums
    )


def _entry_line(r: Record) -> str:
    line = f"{r.on:%d.%m.%Y} {r.kind} {format_cents(r.amount_cents)} {r.currency}"
    if r.currency != "EUR":
        if r.eur_cents is None:
            line += " (no rate)"
        else:
            line += f" ({format_cents(r.eur_cents)} EUR)"
    return line + f" · {r.category or 'no category'} · {r.note}"
