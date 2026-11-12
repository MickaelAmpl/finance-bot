import re
import sqlite3
from calendar import monthrange
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from finbot.budgets import Budget, list_budgets
from finbot.ledger import Record, records_between
from finbot.money import format_cents
from finbot.savings import Pot, list_pots
from finbot.texts import MONTHS, budget_line

MONTH_ARG_MSG = "Use a month like /month 10 or /month 2026-10"
BAR_WIDTH = 12
LABEL_WIDTH = 6
TOP_COUNT = 5
_YEAR_MONTH = re.compile(r"([1-9][0-9]{3})-(0?[1-9]|1[0-2])")
_MONTH = re.compile(r"(?:0?[1-9]|1[0-2])")


@dataclass(frozen=True)
class MonthReport:
    year: int
    month: int
    income_cents: int
    spent_cents: int
    saved_cents: int
    net_cents: int
    prev_spent_cents: int
    by_category: list[tuple[str, int]]
    top: list[Record]
    pots: list[Pot]
    budgets: list[Budget]
    pending: int
    entries: int


def parse_month_arg(arg: str | None, today: date) -> tuple[int, int]:
    text = (arg or "").strip()
    if not text:
        return today.year, today.month
    match = _YEAR_MONTH.fullmatch(text)
    if match is not None:
        return int(match[1]), int(match[2])
    if _MONTH.fullmatch(text):
        month = int(text)
        return (today.year - 1 if month > today.month else today.year), month
    raise ValueError(MONTH_ARG_MSG)


def build_month_report(conn: sqlite3.Connection, year: int, month: int) -> MonthReport:
    first = date(year, month, 1)
    last = date(year, month, monthrange(year, month)[1])
    prev_last = first - timedelta(days=1)
    prev_first = prev_last.replace(day=1)
    records = records_between(conn, first, last)
    expenses = [r for r in records if r.kind == "expense" and not r.pending]
    income = _total(records, "income")
    spent = _total(records, "expense")
    saved = _total(records, "save") - _total(records, "take")
    return MonthReport(
        year=year,
        month=month,
        income_cents=income,
        spent_cents=spent,
        saved_cents=saved,
        net_cents=income - spent - saved,
        prev_spent_cents=_total(records_between(conn, prev_first, prev_last), "expense"),
        by_category=_by_category(expenses),
        top=sorted(expenses, key=lambda r: (-_eur(r), r.on))[:TOP_COUNT],
        pots=list_pots(conn),
        budgets=list_budgets(conn, year, month),
        pending=sum(1 for r in records if r.pending),
        entries=len(records),
    )


def render_month(r: MonthReport) -> str:
    header = f"{MONTHS[r.month - 1]} {r.year}"
    if r.entries == 0:
        return f"{header}\n\nNo entries."
    blocks = [[header], _totals(r)]
    if r.by_category:
        blocks.append(_categories(r))
    if r.budgets:
        blocks.append(["Budgets", *(budget_line(b) for b in r.budgets)])
    if r.by_category:
        blocks.append(_top(r.top))
    if r.pots:
        blocks.append(_savings(r.pots))
    if r.pending:
        blocks.append([f"Not counted: {r.pending} pending (no rate). Use /rate to convert."])
    return "\n\n".join("\n".join(block) for block in blocks)


def _total(records: list[Record], kind: str) -> int:
    return sum(_eur(r) for r in records if r.kind == kind and not r.pending)


def _by_category(expenses: list[Record]) -> list[tuple[str, int]]:
    totals: defaultdict[str, int] = defaultdict(int)
    for r in expenses:
        totals[r.category or "Uncategorized"] += _eur(r)
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))


def _eur(record: Record) -> int:
    # Only non-pending records have an EUR amount; callers filter them out first.
    assert record.eur_cents is not None
    return record.eur_cents


def _share(part: int, whole: int, scale: int) -> int:
    if whole == 0:
        return 0
    return int((Decimal(part * scale) / whole).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _totals(r: MonthReport) -> list[str]:
    amounts = (r.income_cents, r.spent_cents, r.saved_cents, r.net_cents)
    width = max(len(format_cents(a)) for a in amounts)
    labels = ("Income", "Spent", "Saved", "Net")
    lines = [
        f"{label:<{LABEL_WIDTH}} {format_cents(a):>{width}} EUR"
        for label, a in zip(labels, amounts, strict=True)
    ]
    if r.prev_spent_cents:
        lines[1] += "  " + _change(r)
    return lines


def _change(r: MonthReport) -> str:
    diff = r.spent_cents - r.prev_spent_cents
    arrow = "▲" if diff >= 0 else "▼"
    percent = _share(abs(diff), r.prev_spent_cents, 100)
    return f"{arrow} {percent}% vs {MONTHS[(r.month - 2) % 12][:3]}"


def _categories(r: MonthReport) -> list[str]:
    name_w = max(len(name) for name, _ in r.by_category)
    amount_w = max(len(format_cents(a)) for _, a in r.by_category)
    largest = max(a for _, a in r.by_category)
    lines = []
    for name, amount in r.by_category:
        bar = "█" * max(1, _share(amount, largest, BAR_WIDTH))
        share = _share(amount, r.spent_cents, 100)
        lines.append(
            f"{name:<{name_w}}  {format_cents(amount):>{amount_w}}  {bar:<{BAR_WIDTH}}  {share}%"
        )
    return lines


def _top(top: list[Record]) -> list[str]:
    amount_w = max(len(format_cents(_eur(r))) for r in top)
    lines = ["Top expenses"]
    for r in top:
        day = f"{r.on.day:02d}.{r.on.month:02d}"
        lines.append(f"{day}  {format_cents(_eur(r)):>{amount_w}}  {r.note}")
    return lines


def _savings(pots: list[Pot]) -> list[str]:
    name_w = max(len(pot.name) for pot in pots)
    total_w = max(len(format_cents(pot.total_cents)) for pot in pots)
    lines = ["Savings"]
    for pot in pots:
        line = f"{pot.name.capitalize():<{name_w}}  {format_cents(pot.total_cents):>{total_w}}"
        if pot.goal_cents is not None:
            goal = format_cents(pot.goal_cents)
            line += f" / {goal} ({_share(pot.total_cents, pot.goal_cents, 100)}%)"
        lines.append(line)
    return lines
