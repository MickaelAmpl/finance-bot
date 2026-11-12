import sqlite3
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from finbot import drafts
from finbot.categories import find_category
from finbot.drafts import (
    DRAFT_TTL,
    DraftClosed,
    DraftEntry,
    DraftError,
    cancel_draft,
    check_draft,
    count_live_drafts,
    create_draft,
    get_draft,
    save_draft,
    set_draft_message,
)
from finbot.rates import set_rate

MESSAGE_DATE = date(2026, 11, 12)
NOW = datetime(2026, 11, 12, 10, 0, tzinfo=UTC)
TOO_MANY = "a draft holds 1 to 10 entries"
ONE_EXPENSE = "a receipt is exactly one expense"
AMOUNT = "entry 1: amount must be like 25 or 12.50, above zero, at most 10000000"


def entry(**overrides) -> dict:
    fields = {
        "kind": "expense",
        "amount": "25",
        "currency": "EUR",
        "category": "Eating out",
        "note": "coffee",
        "date": "2026-11-12",
    }
    fields.update(overrides)
    return fields


def raw(*entries: dict) -> dict:
    return {"entries": list(entries), "replaces_open_draft": False}


def refusal(conn, raw_input: dict, source: str = "text") -> str:
    with pytest.raises(DraftError) as info:
        check_draft(conn, raw_input, source, MESSAGE_DATE)
    return str(info.value)


def sample(**overrides) -> drafts.DraftEntry:
    fields = {
        "kind": "expense",
        "amount_cents": 2500,
        "currency": "EUR",
        "category_id": None,
        "category": None,
        "note": "coffee",
        "on": MESSAGE_DATE,
    }
    fields.update(overrides)
    return DraftEntry(**fields)


def status_of(conn, draft_id: int) -> str:
    draft = get_draft(conn, draft_id)
    assert draft is not None
    return draft.status


def category_id(conn, name: str) -> int:
    found = find_category(conn, name)
    assert found is not None
    return found.id


def test_valid_entry_is_normalised_and_gets_its_category(conn):
    entries = check_draft(
        conn,
        raw(entry(kind="Expense", currency="eur", amount="12,50", category="eating out")),
        "text",
        MESSAGE_DATE,
    )
    assert entries == (
        DraftEntry(
            kind="expense",
            amount_cents=1250,
            currency="EUR",
            category_id=category_id(conn, "Eating out"),
            category="Eating out",
            note="coffee",
            on=MESSAGE_DATE,
        ),
    )


@pytest.mark.parametrize("entries", [[], [entry()] * 11])
def test_entry_count_must_be_one_to_ten(conn, entries):
    assert refusal(conn, {"entries": entries}) == TOO_MANY


def test_missing_entries_list_counts_as_no_entries(conn):
    assert refusal(conn, {}) == TOO_MANY


def test_photo_must_be_exactly_one_expense(conn):
    assert refusal(conn, raw(entry(), entry()), source="photo") == ONE_EXPENSE
    assert refusal(conn, raw(entry(kind="income")), source="photo") == ONE_EXPENSE


def test_photo_with_one_expense_is_accepted(conn):
    assert len(check_draft(conn, raw(entry()), "photo", MESSAGE_DATE)) == 1


def test_kind_must_be_expense_or_income(conn):
    assert refusal(conn, raw(entry(kind="transfer"))) == ("entry 1: kind must be expense or income")
    assert refusal(conn, raw(entry(), entry(kind="save"))) == (
        "entry 2: kind must be expense or income"
    )


def test_currency_must_be_eur_usd_or_uah(conn):
    assert refusal(conn, raw(entry(currency="GBP"))) == (
        "entry 1: currency must be EUR, USD or UAH"
    )


@pytest.mark.parametrize("amount", ["0", "abc", "12.505", "10000001", "-5", 25, None])
def test_amount_must_be_a_positive_amount_in_range(conn, amount):
    assert refusal(conn, raw(entry(amount=amount))) == AMOUNT


@pytest.mark.parametrize(
    "on", ["2026-1-5", "12.11.2026", "2026-11-31", "2026-11-1x", "2026-W44-1", "2026-11-1 ", None]
)
def test_date_must_be_iso(conn, on):
    assert refusal(conn, raw(entry(date=on))) == "entry 1: date must be YYYY-MM-DD"


def test_date_after_the_message_date_is_refused(conn):
    assert refusal(conn, raw(entry(date="2026-11-13"))) == (
        "entry 1: 2026-11-13 is after the message date"
    )


def test_entry_dated_on_the_message_date_is_accepted(conn):
    assert check_draft(conn, raw(entry()), "text", MESSAGE_DATE)[0].on == MESSAGE_DATE


def test_category_of_the_other_kind_or_unknown_is_left_empty(conn):
    other_kind = check_draft(conn, raw(entry(category="Salary")), "text", MESSAGE_DATE)
    unknown = check_draft(conn, raw(entry(category="Nonsense")), "text", MESSAGE_DATE)
    assert (other_kind[0].category_id, other_kind[0].category) == (None, None)
    assert (unknown[0].category_id, unknown[0].category) == (None, None)


def test_income_uses_the_income_category(conn):
    found = check_draft(
        conn, raw(entry(kind="income", category="Salary", amount="3000")), "text", MESSAGE_DATE
    )
    assert (found[0].category, found[0].category_id) == ("Salary", category_id(conn, "Salary"))


def test_note_is_cleaned_of_spaces_and_leading_formula_characters(conn):
    found = check_draft(conn, raw(entry(note="=SUM(A1)\n  coffee")), "text", MESSAGE_DATE)
    assert found[0].note == "SUM(A1) coffee"


def test_long_note_is_cut_to_one_hundred_characters_with_an_ellipsis(conn):
    found = check_draft(conn, raw(entry(note="x" * 120)), "text", MESSAGE_DATE)
    assert len(found[0].note) == 100
    assert found[0].note == "x" * 99 + "…"


def test_empty_note_falls_back_to_the_category_name_or_receipt(conn):
    with_category = check_draft(conn, raw(entry(note="")), "text", MESSAGE_DATE)
    without_category = check_draft(conn, raw(entry(note="  ", category="")), "text", MESSAGE_DATE)
    assert with_category[0].note == "Eating out"
    assert without_category[0].note == "receipt"


def test_first_failing_entry_is_the_one_reported(conn):
    assert refusal(conn, raw(entry(kind="bad"), entry(amount="0"))) == (
        "entry 1: kind must be expense or income"
    )


def test_create_draft_without_replacing_keeps_the_open_text_draft(conn):
    first, replaced = create_draft(conn, (sample(),), "text", False, NOW)
    second, none_replaced = create_draft(conn, (sample(),), "text", False, NOW)
    assert replaced is None and none_replaced is None
    assert status_of(conn, first.id) == "open"
    assert status_of(conn, second.id) == "open"


def test_create_draft_replaces_the_only_live_open_text_draft(conn):
    only, _ = create_draft(conn, (sample(),), "text", False, NOW)
    new, replaced = create_draft(conn, (sample(),), "text", True, NOW)
    assert replaced is not None and replaced.id == only.id
    assert replaced.status == "replaced"
    assert status_of(conn, only.id) == "replaced"
    assert status_of(conn, new.id) == "open"


def test_create_draft_replaces_nothing_when_another_text_draft_is_open(conn):
    older, _ = create_draft(conn, (sample(),), "text", False, NOW)
    newest, _ = create_draft(conn, (sample(),), "text", False, NOW)
    new, replaced = create_draft(conn, (sample(),), "text", True, NOW)
    assert replaced is None
    assert status_of(conn, older.id) == "open"
    assert status_of(conn, newest.id) == "open"
    assert status_of(conn, new.id) == "open"


def test_create_draft_replaces_nothing_when_a_photo_draft_is_also_open(conn):
    text, _ = create_draft(conn, (sample(),), "text", False, NOW)
    photo, _ = create_draft(conn, (sample(),), "photo", False, NOW)
    new, replaced = create_draft(conn, (sample(),), "text", True, NOW)
    assert replaced is None
    assert status_of(conn, text.id) == "open"
    assert status_of(conn, photo.id) == "open"
    assert status_of(conn, new.id) == "open"


def test_create_draft_replaces_nothing_when_the_only_live_draft_is_a_photo(conn):
    photo, _ = create_draft(conn, (sample(),), "photo", False, NOW)
    new, replaced = create_draft(conn, (sample(),), "text", True, NOW)
    assert replaced is None
    assert status_of(conn, photo.id) == "open"
    assert status_of(conn, new.id) == "open"


def test_photo_draft_never_replaces_an_open_text_draft(conn):
    text, _ = create_draft(conn, (sample(),), "text", False, NOW)
    photo, replaced = create_draft(conn, (sample(),), "photo", True, NOW)
    assert replaced is None
    assert status_of(conn, text.id) == "open"
    assert status_of(conn, photo.id) == "open"


def test_saved_draft_is_not_live_so_nothing_is_replaced(conn):
    old, _ = create_draft(conn, (sample(),), "text", False, NOW)
    save_draft(conn, old.id, NOW)
    new, replaced = create_draft(conn, (sample(),), "text", True, NOW)
    assert replaced is None
    assert status_of(conn, old.id) == "saved"
    assert status_of(conn, new.id) == "open"


def test_draft_older_than_48_hours_is_neither_replaced_nor_counted(conn):
    stale, _ = create_draft(conn, (sample(),), "text", False, NOW - DRAFT_TTL - timedelta(hours=1))
    new, replaced = create_draft(conn, (sample(),), "text", True, NOW)
    assert replaced is None
    assert status_of(conn, stale.id) == "open"
    assert count_live_drafts(conn, NOW) == 1


def test_count_live_drafts_counts_open_drafts_of_any_source(conn):
    assert count_live_drafts(conn, NOW) == 0
    create_draft(conn, (sample(),), "text", False, NOW)
    create_draft(conn, (sample(),), "photo", False, NOW)
    assert count_live_drafts(conn, NOW) == 2


def test_created_at_is_stored_in_utc_and_read_back_as_the_same_instant(conn):
    local = timezone(timedelta(hours=1))
    created, _ = create_draft(
        conn, (sample(),), "text", False, datetime(2026, 11, 12, 11, 0, tzinfo=local)
    )
    stored = conn.execute("SELECT created_at FROM drafts WHERE id = ?", (created.id,)).fetchone()
    assert stored[0] == "2026-11-12T10:00:00+00:00"
    loaded = get_draft(conn, created.id)
    assert loaded is not None and loaded.created_at == datetime(2026, 11, 12, 10, 0, tzinfo=UTC)


def test_draft_round_trips_its_entries_and_created_at(conn):
    created, _ = create_draft(conn, (sample(category_id=None),), "photo", False, NOW)
    loaded = get_draft(conn, created.id)
    assert loaded is not None
    assert loaded.source == "photo"
    assert loaded.created_at == NOW
    assert loaded.entries == (sample(),)
    assert loaded.message_id is None


def test_set_draft_message_stores_the_message_id(conn):
    created, _ = create_draft(conn, (sample(),), "text", False, NOW)
    set_draft_message(conn, created.id, 555)
    loaded = get_draft(conn, created.id)
    assert loaded is not None and loaded.message_id == 555


def test_save_writes_every_entry_in_draft_order_with_its_category(conn):
    set_rate(conn, "USD", Decimal("0.92"), MESSAGE_DATE)
    eating = category_id(conn, "Eating out")
    draft, _ = create_draft(
        conn,
        (
            sample(category_id=eating, category="Eating out", note="coffee", amount_cents=2500),
            sample(currency="USD", amount_cents=1000, note="book"),
            sample(currency="UAH", amount_cents=120000, note="taxi"),
        ),
        "text",
        False,
        NOW,
    )
    saved = save_draft(conn, draft.id, NOW)
    assert [(r.note, r.category, r.keyword, r.on) for r in saved] == [
        ("coffee", "Eating out", "", MESSAGE_DATE),
        ("book", None, "", MESSAGE_DATE),
        ("taxi", None, "", MESSAGE_DATE),
    ]
    assert [r.eur_cents for r in saved] == [2500, 920, None]
    assert [r.pending for r in saved] == [False, False, True]
    assert status_of(conn, draft.id) == "saved"


def test_second_save_is_refused_and_adds_nothing(conn):
    draft, _ = create_draft(conn, (sample(),), "text", False, NOW)
    save_draft(conn, draft.id, NOW)
    with pytest.raises(DraftClosed) as info:
        save_draft(conn, draft.id, NOW)
    assert info.value.status == "saved"
    assert conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 1


def test_save_of_a_cancelled_draft_is_refused(conn):
    draft, _ = create_draft(conn, (sample(),), "text", False, NOW)
    cancel_draft(conn, draft.id, NOW)
    with pytest.raises(DraftClosed) as info:
        save_draft(conn, draft.id, NOW)
    assert info.value.status == "cancelled"
    assert conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 0


def test_save_after_48_hours_expires_the_draft_and_keeps_the_expiry(conn):
    draft, _ = create_draft(conn, (sample(),), "text", False, NOW)
    with pytest.raises(DraftClosed) as info:
        save_draft(conn, draft.id, NOW + DRAFT_TTL + timedelta(seconds=1))
    assert info.value.status == "expired"
    assert status_of(conn, draft.id) == "expired"
    assert conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 0


def test_save_at_47_hours_59_minutes_is_accepted(conn):
    draft, _ = create_draft(conn, (sample(),), "text", False, NOW)
    saved = save_draft(conn, draft.id, NOW + timedelta(hours=47, minutes=59))
    assert len(saved) == 1


def test_save_of_an_unknown_draft_is_refused_as_gone(conn):
    with pytest.raises(DraftClosed) as info:
        save_draft(conn, 999, NOW)
    assert info.value.status == "gone"


def test_failed_entry_insert_rolls_back_the_whole_save(conn, monkeypatch):
    draft, _ = create_draft(conn, (sample(), sample()), "text", False, NOW)
    real_insert = drafts.insert_transaction
    calls = []

    def fail_second(*args, **kwargs):
        calls.append(1)
        if len(calls) == 2:
            raise sqlite3.IntegrityError("forced")
        return real_insert(*args, **kwargs)

    monkeypatch.setattr(drafts, "insert_transaction", fail_second)
    with pytest.raises(sqlite3.IntegrityError, match="forced"):
        save_draft(conn, draft.id, NOW)
    assert status_of(conn, draft.id) == "open"
    assert conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 0


def test_cancel_sets_cancelled(conn):
    draft, _ = create_draft(conn, (sample(),), "text", False, NOW)
    cancelled = cancel_draft(conn, draft.id, NOW)
    assert cancelled.status == "cancelled"
    assert status_of(conn, draft.id) == "cancelled"


def test_cancel_after_48_hours_expires_the_draft(conn):
    draft, _ = create_draft(conn, (sample(),), "text", False, NOW)
    with pytest.raises(DraftClosed) as info:
        cancel_draft(conn, draft.id, NOW + DRAFT_TTL + timedelta(seconds=1))
    assert info.value.status == "expired"
    assert status_of(conn, draft.id) == "expired"


def test_cancel_of_an_unknown_draft_is_refused_as_gone(conn):
    with pytest.raises(DraftClosed) as info:
        cancel_draft(conn, 999, NOW)
    assert info.value.status == "gone"
