import json
import re
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, timedelta
from typing import Any, cast

from finbot.categories import find_category
from finbot.ledger import Record, get_record, insert_transaction
from finbot.money import CURRENCIES, parse_amount
from finbot.parser import MAX_ENTRIES, Entry, Kind

DRAFT_TTL = timedelta(hours=48)
MAX_DRAFT_ENTRIES = MAX_ENTRIES
_DATE_TEXT = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_NOTE_MAX = 100


@dataclass(frozen=True)
class DraftEntry:
    kind: str
    amount_cents: int
    currency: str
    category_id: int | None
    category: str | None
    note: str
    on: date


@dataclass(frozen=True)
class Draft:
    id: int
    source: str
    entries: tuple[DraftEntry, ...]
    status: str
    created_at: datetime
    message_id: int | None


class DraftError(ValueError):
    """The message is the reason sent back to the model."""


class DraftClosed(Exception):
    def __init__(self, status: str) -> None:
        super().__init__(status)
        self.status = status


def check_draft(
    conn: sqlite3.Connection, raw: Mapping[str, Any], source: str, message_date: date
) -> tuple[DraftEntry, ...]:
    items = raw.get("entries")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_DRAFT_ENTRIES:
        raise DraftError(f"a draft holds 1 to {MAX_DRAFT_ENTRIES} entries")
    if source == "photo" and (len(items) != 1 or _kind_of(items[0]) != "expense"):
        raise DraftError("a receipt is exactly one expense")
    entries = []
    for n, item in enumerate(items, start=1):
        fields: Mapping[str, Any] = item if isinstance(item, Mapping) else {}
        kind = _kind_of(item)
        if kind not in ("expense", "income"):
            raise DraftError(f"entry {n}: kind must be expense or income")
        currency = _text(fields.get("currency"))
        currency = currency.upper() if currency is not None else None
        if currency not in CURRENCIES:
            raise DraftError(f"entry {n}: currency must be EUR, USD or UAH")
        cents = _amount_cents(fields.get("amount"))
        if cents is None:
            raise DraftError(
                f"entry {n}: amount must be like 25 or 12.50, above zero, at most 10000000"
            )
        text = _text(fields.get("date"))
        if text is None or not _DATE_TEXT.fullmatch(text):
            raise DraftError(f"entry {n}: date must be YYYY-MM-DD")
        try:
            on = date.fromisoformat(text)
        except ValueError:
            raise DraftError(f"entry {n}: date must be YYYY-MM-DD") from None
        if on > message_date:
            raise DraftError(f"entry {n}: {text} is after the message date")
        name = _text(fields.get("category"))
        found = find_category(conn, name) if name else None
        if found is not None and found.kind != kind:
            found = None
        entries.append(
            DraftEntry(
                kind=kind,
                amount_cents=cents,
                currency=currency,
                category_id=None if found is None else found.id,
                category=None if found is None else found.name,
                note=_note(_text(fields.get("note")), found.name if found else None),
                on=on,
            )
        )
    return tuple(entries)


def create_draft(
    conn: sqlite3.Connection,
    entries: tuple[DraftEntry, ...],
    source: str,
    replace_open: bool,
    now: datetime,
) -> tuple[Draft, Draft | None]:
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        replaced_id: int | None = None
        if replace_open and source == "text":
            live = _live_draft_ids(conn, now)
            only = _fetch(conn, live[0]) if len(live) == 1 else None
            if only is not None and only.source == "text":
                replaced_id = only.id
                conn.execute("UPDATE drafts SET status = 'replaced' WHERE id = ?", (replaced_id,))
        cursor = conn.execute(
            "INSERT INTO drafts (source, entries, status, created_at) VALUES (?, ?, 'open', ?)",
            (source, json.dumps([_entry_json(e) for e in entries]), _utc_text(now)),
        )
    assert cursor.lastrowid is not None
    created = _fetch(conn, cursor.lastrowid)
    assert created is not None
    replaced = None if replaced_id is None else _fetch(conn, replaced_id)
    return created, replaced


def count_live_drafts(conn: sqlite3.Connection, now: datetime) -> int:
    return len(_live_draft_ids(conn, now))


def set_draft_message(conn: sqlite3.Connection, draft_id: int, message_id: int) -> None:
    with conn:
        conn.execute("UPDATE drafts SET message_id = ? WHERE id = ?", (message_id, draft_id))


def get_draft(conn: sqlite3.Connection, draft_id: int) -> Draft | None:
    return _fetch(conn, draft_id)


def save_draft(conn: sqlite3.Connection, draft_id: int, now: datetime) -> list[Record]:
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        draft = _open_draft(conn, draft_id, now)
        if draft is not None:
            conn.execute("UPDATE drafts SET status = 'saved' WHERE id = ?", (draft_id,))
            saved = []
            for item in draft.entries:
                entry = Entry(
                    kind=cast(Kind, item.kind),
                    amount_cents=item.amount_cents,
                    currency=item.currency,
                    note=item.note,
                    keyword="",
                    pot=None,
                    on=item.on,
                )
                record = get_record(conn, insert_transaction(conn, entry, item.category_id))
                assert record is not None
                saved.append(record)
            return saved
    # Raised outside `with`: the expiry written above must commit.
    raise DraftClosed("expired")


def cancel_draft(conn: sqlite3.Connection, draft_id: int, now: datetime) -> Draft:
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        draft = _open_draft(conn, draft_id, now)
        if draft is not None:
            conn.execute("UPDATE drafts SET status = 'cancelled' WHERE id = ?", (draft_id,))
            return replace(draft, status="cancelled")
    raise DraftClosed("expired")


def _open_draft(conn: sqlite3.Connection, draft_id: int, now: datetime) -> Draft | None:
    """The draft if it is still open and unexpired; an expired one is marked and gives None."""
    draft = _fetch(conn, draft_id)
    if draft is None:
        raise DraftClosed("gone")
    if draft.status != "open":
        raise DraftClosed(draft.status)
    if now - draft.created_at > DRAFT_TTL:
        conn.execute("UPDATE drafts SET status = 'expired' WHERE id = ?", (draft_id,))
        return None
    return draft


def _live_draft_ids(conn: sqlite3.Connection, now: datetime) -> list[int]:
    """Open drafts not older than DRAFT_TTL, newest first."""
    rows = conn.execute(
        "SELECT id, created_at FROM drafts WHERE status = 'open' ORDER BY id DESC"
    ).fetchall()
    return [
        row["id"] for row in rows if now - datetime.fromisoformat(row["created_at"]) <= DRAFT_TTL
    ]


def _fetch(conn: sqlite3.Connection, draft_id: int) -> Draft | None:
    row = conn.execute(
        "SELECT id, source, entries, status, created_at, message_id FROM drafts WHERE id = ?",
        (draft_id,),
    ).fetchone()
    if row is None:
        return None
    return Draft(
        id=row["id"],
        source=row["source"],
        entries=tuple(
            DraftEntry(
                kind=item["kind"],
                amount_cents=item["amount_cents"],
                currency=item["currency"],
                category_id=item["category_id"],
                category=item["category"],
                note=item["note"],
                on=date.fromisoformat(item["on"]),
            )
            for item in json.loads(row["entries"])
        ),
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        message_id=row["message_id"],
    )


def _entry_json(entry: DraftEntry) -> dict[str, Any]:
    return {
        "kind": entry.kind,
        "amount_cents": entry.amount_cents,
        "currency": entry.currency,
        "category_id": entry.category_id,
        "category": entry.category,
        "note": entry.note,
        "on": entry.on.isoformat(),
    }


def _utc_text(now: datetime) -> str:
    return now.astimezone(UTC).isoformat()


def _text(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _kind_of(item: object) -> str | None:
    if not isinstance(item, Mapping):
        return None
    kind = _text(item.get("kind"))
    return None if kind is None else kind.lower()


def _amount_cents(value: object) -> int | None:
    if not isinstance(value, str):
        return None
    try:
        return parse_amount(value)
    except ValueError:
        return None


def _note(text: str | None, category: str | None) -> str:
    note = " ".join((text or "").split()).lstrip("=+-@ ")
    if len(note) > _NOTE_MAX:
        note = note[: _NOTE_MAX - 1] + "…"
    return note or category or "receipt"
