import html
from collections.abc import Sequence
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from finbot.budgets import Budget
from finbot.categories import MAX_NAME_LENGTH, Category
from finbot.drafts import DraftEntry
from finbot.ledger import Record
from finbot.money import format_cents, signed
from finbot.savings import Pot, PotMove, month_label, monthly_cents, months_left

AI_TOO_LONG = "Keep it under 1000 characters, or split it into two messages."
PHOTO_NEEDS_AI = "Receipt photos need the AI. Write it as 25 coffee."
PHOTO_UNREADABLE = "Could not read the photo. Send it again."
DRAFT_SAVE_FAILED = "Could not save. Nothing saved. Press Save again."
DRAFT_CANCELLED = "Cancelled. Nothing saved."
DRAFT_CANCEL_FAILED = "Could not cancel. Nothing changed. Press Cancel again."
DRAFT_REPLACED = "Replaced by the draft below. Nothing saved."
DRAFT_EARLIER_CLOSED = "The earlier draft is closed already. Save adds this as a new entry."
DRAFT_OTHER_OPEN = "Another draft is still open above. Cancel the one you do not want."
NOTHING_TO_UNDO = "Nothing to undo."
ALREADY_DELETED = "Already deleted."
NOTHING_DELETED = "Nothing deleted."
CLEAR_TOO_OLD = "This question is too old. Send /clear again."
_MAX_LISTED = 5
_BUTTON_LABEL_MAX = 20
MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

BOT_COMMANDS: list[tuple[str, str]] = [
    ("month", "Report for this month"),
    ("last", "Last 10 entries: change or delete"),
    ("undo", "Delete the last entry"),
    ("savings", "Savings pots and goals"),
    ("goal", "Set a goal: /goal emergency 10000 12.2027"),
    ("budget", "Monthly limits: /budget Rent 850.00"),
    ("category", "Add or rename: /category add Rent"),
    ("clear", "Delete a month's entries (asks first)"),
    ("rate", "Set a rate: /rate usd 0.92"),
    ("export", "All entries as a CSV file"),
    ("help", "How to write entries"),
]

_HELP_HEAD = [
    "25 coffee - expense in EUR",
    "1200 uah taxi - expense in UAH",
    "+3000 salary - income in EUR",
    "25 coffee yesterday - entry dated yesterday",
    "save 200 emergency - add 200 EUR to the emergency pot",
    "850.00 rent, 120 utilities - several entries (or one per line)",
]
_HELP_TAIL = [
    "/rate usd 0.92 - 1 USD = 0.92 EUR",
    "/month - report for the current month",
    "/goal emergency 10000 12.2027 - goal with a deadline",
    "/category add Rent - new category",
    "/budget Rent 850.00 - monthly limit for a category",
    "All commands: the Menu button next to the message field",
]
_AI_HELP = [
    "coffee with a friend yesterday 25 - free text: the bot drafts it, you press Save",
    "a receipt photo - one entry for the total, after you press Save",
    "how much did I spend on eating out in October? - ask about your money",
]
HELP = "\n".join([*_HELP_HEAD, *_HELP_TAIL])


def saved_text(r: Record, budget: Budget | None = None) -> str:
    line = f"Saved {_day(r.on)}: {signed(r.amount_cents, _is_inflow(r))} {r.currency}"
    if r.rate is not None and r.eur_cents is not None:
        line += f" (≈ {signed(r.eur_cents, _is_inflow(r))} EUR at {str(r.rate)})"
    line += f" · {r.note}"
    if r.category is not None:
        line += f" → {r.category}"
    lines = [line]
    if r.pending:
        lines.append(
            f"No {r.currency} rate yet. Send /rate {r.currency.lower()} <EUR per 1 {r.currency}>"
            " and I will convert it."
        )
    if r.category is None:
        if r.keyword:
            lines.append(f'New word "{r.keyword}" - pick a category:')
        else:
            lines.append("Pick a category:")
    if budget is not None:
        spent, limit = format_cents(budget.spent_cents), format_cents(budget.limit_cents)
        lines.append(
            f"{budget.category}: {spent} of {limit} in {MONTHS[r.on.month - 1]}"
            f" · {budget_left(budget)}"
        )
    return "\n".join(lines)


def draft_text(entries: Sequence[DraftEntry]) -> str:
    lines = ["Draft:"]
    for n, entry in enumerate(entries, start=1):
        lines.append(
            f"{n}. {signed(entry.amount_cents, entry.kind == 'income')} {entry.currency}"
            f" · {entry.category or 'no category'} · {entry.note}"
            f" · {entry.on.strftime('%d.%m.%Y')}"
        )
    return "\n".join(lines)


def save_button_text(count: int) -> str:
    return "Save" if count == 1 else f"Save {count} entries"


def draft_saved_text(count: int) -> str:
    return "Saved." if count == 1 else f"Saved {count} entries."


_DRAFT_CLOSED = {
    "saved": "Already saved.",
    "cancelled": "Already cancelled.",
    "replaced": "Replaced by a newer draft.",
    "expired": "This draft is too old. Nothing saved. Send it again.",
    "gone": "This draft is gone.",
}


def draft_closed_text(status: str) -> str:
    return _DRAFT_CLOSED[status]


def help_text(ai_on: bool) -> str:
    if not ai_on:
        return HELP
    return "\n".join([*_HELP_HEAD, *_AI_HELP, *_HELP_TAIL])


def pot_text(pot: Pot, kind: str, amount_cents: int, on: date) -> str:
    return (
        f"{pot.name.capitalize()} pot {_day(on)}: {signed(amount_cents, kind == 'save')} EUR"
        f" · total {format_cents(pot.total_cents)} EUR"
    )


def removed_text(r: Record) -> str:
    amount = signed(r.amount_cents, _is_inflow(r))
    return f"Removed {_day(r.on)}: {amount} {r.currency} · {_label(r)}"


def rate_set_text(currency: str, rate: Decimal, converted: list[Record]) -> str:
    lines = [f"Saved: 1 {currency} = {str(rate)} EUR."]
    if converted:
        header = (
            "Converted 1 entry that was waiting for this rate:"
            if len(converted) == 1
            else f"Converted {len(converted)} entries that were waiting for this rate:"
        )
        lines.append(header)
        lines.extend(_converted_line(r) for r in converted[:_MAX_LISTED])
        if len(converted) > _MAX_LISTED:
            lines.append(f"...and {len(converted) - _MAX_LISTED} more")
    return "\n".join(lines)


def savings_text(pots: list[Pot], moves: dict[int, list[PotMove]], today: date) -> str:
    if not pots:
        return "No pots yet. Start one with: save 100 emergency"
    return "\n\n".join(_pot_block(pot, moves.get(pot.id, []), today) for pot in pots)


def last_text(records: list[Record]) -> str:
    if not records:
        return "No entries yet."
    return "\n".join(_last_line(number, r) for number, r in enumerate(records, start=1))


def last_button_text(number: int, r: Record) -> str:
    label = _label(r)[:_BUTTON_LABEL_MAX].rstrip()
    return f"{number}. {label} {signed(r.amount_cents, _is_inflow(r))} {r.currency}"


def category_list_text(expense: list[Category], income: list[Category]) -> str:
    return "\n".join(
        [
            f"Expense: {', '.join(c.name for c in expense)}",
            f"Income: {', '.join(c.name for c in income)}",
            "Add: /category add Rent · Rename: /category rename Rent Housing",
        ]
    )


def category_added_text(category: Category) -> str:
    return f"Added {category.kind} category {category.name}."


def category_renamed_text(old_name: str, new_name: str) -> str:
    return f"Renamed {old_name} to {new_name}."


def category_unknown_text(name: str) -> str:
    return f"No category named {name[:MAX_NAME_LENGTH]}. See /category"


def budget_line(budget: Budget) -> str:
    spent, limit = format_cents(budget.spent_cents), format_cents(budget.limit_cents)
    return f"{budget.category}: {spent} of {limit} · {budget_left(budget)}"


def budget_left(budget: Budget) -> str:
    return _standing(budget, "{} left")


def budget_set_text(budget: Budget, today: date) -> str:
    return (
        f"{budget.category}: {format_cents(budget.limit_cents)} EUR a month."
        f" {MONTHS[today.month - 1]}: spent {format_cents(budget.spent_cents)},"
        f" {_standing(budget, 'left {}')}."
    )


def budget_removed_text(name: str) -> str:
    return f"{name}: budget removed."


def budgets_text(budgets: list[Budget], today: date) -> str:
    if not budgets:
        return "No budgets yet. Set one: /budget Rent 850.00"
    header = f"Budgets, {MONTHS[today.month - 1]} {today.year}:"
    return "\n".join([header, *(budget_line(b) for b in budgets)])


def clear_nothing_text(year: int, month: int) -> str:
    return f"Nothing to clear in {_month_year(year, month)}."


def clear_ask_text(count: int, year: int, month: int) -> str:
    what = "1 expense or income" if count == 1 else f"{count} expenses and incomes"
    return f"Delete all {what} of {_month_year(year, month)}? Savings stay."


def clear_button_text(count: int) -> str:
    return f"Delete {_entries(count)}"


def clear_done_text(count: int, year: int, month: int) -> str:
    return (
        f"Deleted {_entries(count)} of {_month_year(year, month)}. /undo will not bring them back."
    )


def clear_changed_text(year: int, month: int) -> str:
    return f"{_month_year(year, month)} changed since you asked. Send /clear again."


def split_report(text: str, limit: int = 4000) -> list[str]:
    """Cut a report into pieces of at most `limit` characters (Telegram allows 4096 per message).

    Blank lines are the preferred cut, then line breaks, then anywhere inside a line.
    """
    return _pack(text, limit, ("\n\n", "\n"))


def as_pre(text: str) -> str:
    return f"<pre>{html.escape(text)}</pre>"


def _pack(text: str, limit: int, separators: tuple[str, ...]) -> list[str]:
    if len(text) <= limit:
        return [text]
    if not separators:
        return [text[start : start + limit] for start in range(0, len(text), limit)]
    separator, finer = separators[0], separators[1:]
    pieces: list[str] = []
    current = ""
    for part in text.split(separator):
        for chunk in _pack(part, limit, finer):
            if current and len(current) + len(separator) + len(chunk) <= limit:
                current += separator + chunk
            else:
                if current:
                    pieces.append(current)
                current = chunk
    if current:
        pieces.append(current)
    return pieces


def _month_year(year: int, month: int) -> str:
    return f"{MONTHS[month - 1]} {year}"


def _entries(count: int) -> str:
    return "1 entry" if count == 1 else f"{count} entries"


def _standing(budget: Budget, left_form: str) -> str:
    # left_form is "{} left" or "left {}"; going over reads the same in both.
    if budget.left_cents < 0:
        return f"over by {format_cents(-budget.left_cents)}"
    return left_form.format(format_cents(budget.left_cents))


def _pot_block(pot: Pot, moves: list[PotMove], today: date) -> str:
    lines = [_pot_summary(pot, today)]
    for move in moves[:5]:
        lines.append(f"  {_day(move.on)} {signed(move.amount_cents, move.kind == 'save')}")
    return "\n".join(lines)


def _pot_summary(pot: Pot, today: date) -> str:
    line = f"{pot.name.capitalize()}: {format_cents(pot.total_cents)} EUR"
    if pot.goal_cents is not None:
        percent = (Decimal(pot.total_cents) * 100 / pot.goal_cents).quantize(
            Decimal(1), rounding=ROUND_HALF_UP
        )
        line += f" of {format_cents(pot.goal_cents)} ({percent}%)"
        if pot.goal_month is not None:
            line += _deadline(pot.goal_cents - pot.total_cents, pot.goal_month, today)
    return line


def _deadline(left_cents: int, goal_month: str, today: date) -> str:
    if left_cents <= 0:
        return " · goal reached"
    shown = month_label(goal_month)
    months = months_left(goal_month, today)
    if months < 1:
        return f" · {shown} has passed"
    return f" · by {shown}: {format_cents(monthly_cents(left_cents, months))} EUR a month"


def _last_line(number: int, r: Record) -> str:
    return f"{number}. {entry_line(r)}"


def entry_line(r: Record) -> str:
    line = f"{_day(r.on)} {signed(r.amount_cents, _is_inflow(r))} {r.currency}"
    if r.currency != "EUR":
        if r.pending:
            line += " (no rate yet)"
        else:
            assert r.eur_cents is not None
            line += f" (≈ {signed(r.eur_cents, _is_inflow(r))} EUR)"
    line += f" {_label(r)}"
    if r.category is not None:
        line += f" → {r.category}"
    return line


def _converted_line(r: Record) -> str:
    assert r.eur_cents is not None
    amount = signed(r.amount_cents, _is_inflow(r))
    eur = signed(r.eur_cents, _is_inflow(r))
    return f"{_day(r.on)} {amount} {r.currency} {_label(r)} = {eur} EUR"


def _is_inflow(r: Record) -> bool:
    return r.kind in ("income", "save")


def _label(r: Record) -> str:
    return r.note if r.pot is None else f"{r.pot} pot"


def _day(on: date) -> str:
    return on.strftime("%d.%m")
