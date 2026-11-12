from datetime import date

import pytest

from finbot.parser import Entry, parse_entry
from finbot.savings import (
    Pot,
    SavingsError,
    apply_pot_entry,
    get_pot,
    list_pots,
    month_label,
    monthly_cents,
    months_left,
    recent_moves,
    set_goal,
)

DAY = date(2026, 11, 1)
UNKNOWN = "No pot named emergency yet. Start it with: save 100 emergency"


def _count_entries(conn) -> int:
    return conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]


def _pot(conn, name: str) -> Pot:
    pot = get_pot(conn, name)
    assert pot is not None
    return pot


def test_save_creates_pot_and_adds_to_total(conn):
    _, pot = apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    assert pot.name == "emergency"
    assert pot.total_cents == 20000
    assert pot.goal_cents is None
    assert pot.goal_month is None


def test_second_save_adds_to_same_pot(conn):
    apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    _, pot = apply_pot_entry(conn, parse_entry("save 100 emergency", DAY))
    assert pot.total_cents == 30000
    assert len(list_pots(conn)) == 1


def test_take_reduces_total(conn):
    apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    apply_pot_entry(conn, parse_entry("save 100 emergency", DAY))
    _, pot = apply_pot_entry(conn, parse_entry("take 50 emergency", DAY))
    assert pot.total_cents == 25000


def test_take_of_whole_balance_is_allowed(conn):
    apply_pot_entry(conn, parse_entry("save 150 emergency", DAY))
    _, pot = apply_pot_entry(conn, parse_entry("take 150 emergency", DAY))
    assert pot.total_cents == 0


def test_take_above_balance_is_rejected_and_stores_nothing(conn):
    apply_pot_entry(conn, parse_entry("save 150 emergency", DAY))
    with pytest.raises(SavingsError) as err:
        apply_pot_entry(conn, parse_entry("take 200 emergency", DAY))
    assert str(err.value) == "Emergency has 150.00 EUR, cannot take 200.00"
    assert _count_entries(conn) == 1
    assert _pot(conn, "emergency").total_cents == 15000


def test_take_one_cent_over_balance_is_rejected_and_exact_balance_accepted(conn):
    apply_pot_entry(conn, parse_entry("save 150 emergency", DAY))
    with pytest.raises(SavingsError) as err:
        apply_pot_entry(conn, parse_entry("take 150.01 emergency", DAY))
    assert str(err.value) == "Emergency has 150.00 EUR, cannot take 150.01"
    assert _count_entries(conn) == 1
    _, pot = apply_pot_entry(conn, parse_entry("take 150 emergency", DAY))
    assert pot.total_cents == 0


def test_take_from_unknown_pot_is_rejected_and_creates_nothing(conn):
    with pytest.raises(SavingsError) as err:
        apply_pot_entry(conn, parse_entry("take 50 emergency", DAY))
    assert str(err.value) == UNKNOWN
    assert _count_entries(conn) == 0
    assert list_pots(conn) == []


def test_set_goal_sets_target(conn):
    apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    pot = set_goal(conn, "emergency", 1_000_000)
    assert pot.goal_cents == 1_000_000
    assert _pot(conn, "emergency").goal_cents == 1_000_000


def test_set_goal_stores_the_month(conn):
    apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    pot = set_goal(conn, "emergency", 1_000_000, "2027-12")
    assert (pot.goal_cents, pot.goal_month) == (1_000_000, "2027-12")
    stored = _pot(conn, "emergency")
    assert (stored.goal_cents, stored.goal_month) == (1_000_000, "2027-12")
    assert [p.goal_month for p in list_pots(conn)] == ["2027-12"]


def test_set_goal_without_a_month_clears_the_month(conn):
    apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    set_goal(conn, "emergency", 1_000_000, "2027-12")
    pot = set_goal(conn, "emergency", 2_000_000)
    assert (pot.goal_cents, pot.goal_month) == (2_000_000, None)
    stored = _pot(conn, "emergency")
    assert (stored.goal_cents, stored.goal_month) == (2_000_000, None)


def test_goal_on_unknown_pot_is_rejected(conn):
    with pytest.raises(SavingsError) as err:
        set_goal(conn, "emergency", 1_000_000)
    assert str(err.value) == UNKNOWN
    assert list_pots(conn) == []


def test_recent_moves_returns_five_newest_by_date(conn):
    _, pot = apply_pot_entry(conn, parse_entry("save 10 emergency", date(2026, 11, 3)))
    for day in (1, 6, 2, 5, 4):
        apply_pot_entry(conn, parse_entry("save 10 emergency", date(2026, 11, day)))
    moves = recent_moves(conn, pot.id)
    assert [m.on for m in moves] == [date(2026, 11, d) for d in (6, 5, 4, 3, 2)]
    assert all(m.kind == "save" and m.amount_cents == 1000 for m in moves)


def test_soft_deleted_move_is_excluded_from_total_and_recent(conn):
    first_id, pot = apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    second_id, _ = apply_pot_entry(conn, parse_entry("save 100 emergency", DAY))
    with conn:
        conn.execute(
            "UPDATE entries SET deleted_at = '2026-11-02T10:00:00Z' WHERE id = ?", (second_id,)
        )
    assert _pot(conn, "emergency").total_cents == 20000
    assert [m.entry_id for m in recent_moves(conn, pot.id)] == [first_id]


def test_pot_move_is_stored_as_eur_entry(conn):
    entry_id, pot = apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    assert row["kind"] == "save"
    assert row["amount_cents"] == 20000
    assert row["currency"] == "EUR"
    assert row["rate"] is None
    assert row["eur_cents"] == 20000
    assert row["pot_id"] == pot.id
    assert row["keyword"] == ""
    assert row["note"] == ""
    assert row["occurred_on"] == "2026-11-01"


def test_list_pots_is_ordered_by_name(conn):
    for name in ("travel", "emergency", "savings"):
        apply_pot_entry(conn, parse_entry(f"save 10 {name}", DAY))
    assert [p.name for p in list_pots(conn)] == ["emergency", "savings", "travel"]


def test_list_pots_hides_pot_whose_only_move_is_deleted(conn):
    typo_id, _ = apply_pot_entry(conn, parse_entry("save 200 emergncy", DAY))
    apply_pot_entry(conn, parse_entry("save 10 travel", DAY))
    with conn:
        conn.execute(
            "UPDATE entries SET deleted_at = '2026-11-02T10:00:00Z' WHERE id = ?", (typo_id,)
        )
    assert [p.name for p in list_pots(conn)] == ["travel"]
    assert _pot(conn, "emergncy").total_cents == 0


def test_list_pots_keeps_pot_with_a_live_move(conn):
    apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    second_id, _ = apply_pot_entry(conn, parse_entry("save 100 emergency", DAY))
    with conn:
        conn.execute(
            "UPDATE entries SET deleted_at = '2026-11-02T10:00:00Z' WHERE id = ?", (second_id,)
        )
    assert [p.name for p in list_pots(conn)] == ["emergency"]


def test_get_pot_is_none_for_unknown_name(conn):
    assert get_pot(conn, "emergency") is None


def test_set_goal_ignores_case(conn):
    apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    assert set_goal(conn, "Emergency", 1_000_000).goal_cents == 1_000_000
    assert _pot(conn, "emergency").goal_cents == 1_000_000


def test_get_pot_ignores_case(conn):
    apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    assert _pot(conn, "EMERGENCY").name == "emergency"


def test_entry_pot_name_is_lowercased_before_lookup(conn):
    apply_pot_entry(conn, parse_entry("save 200 emergency", DAY))
    _, pot = apply_pot_entry(conn, Entry("save", 10000, "EUR", "", "", "Emergency", DAY))
    assert pot.total_cents == 30000
    assert [p.name for p in list_pots(conn)] == ["emergency"]


def test_unknown_pot_message_uses_lowercase_name(conn):
    with pytest.raises(SavingsError) as err:
        set_goal(conn, "Travel", 100)
    assert str(err.value) == "No pot named travel yet. Start it with: save 100 travel"


@pytest.mark.parametrize(
    "entry",
    [
        Entry("expense", 1000, "EUR", "coffee", "coffee", None, DAY),
        Entry("save", 1000, "EUR", "", "", None, DAY),
    ],
)
def test_apply_rejects_entry_that_is_not_a_pot_move(conn, entry):
    with pytest.raises(ValueError):
        apply_pot_entry(conn, entry)
    assert _count_entries(conn) == 0


@pytest.mark.parametrize(
    ("today", "goal_month", "expected"),
    [
        (date(2026, 11, 1), "2027-12", 14),
        (date(2026, 11, 1), "2026-11", 1),
        (date(2026, 11, 30), "2026-11", 1),
        (date(2026, 12, 15), "2027-01", 2),
        (date(2026, 11, 1), "2027-10", 12),
        (date(2026, 11, 1), "2027-11", 13),
        (date(2026, 11, 1), "2026-10", 0),
        (date(2026, 11, 1), "2025-12", -10),
    ],
)
def test_months_left_counts_this_month_and_the_goal_month(today, goal_month, expected):
    assert months_left(goal_month, today) == expected


@pytest.mark.parametrize(
    ("remaining", "months", "expected"),
    [
        (970_000, 14, 69_286),
        (120_000, 2, 60_000),
        (120_000, 13, 9_231),
        (120_000, 1, 120_000),
        (1, 14, 1),
        (14, 14, 1),
        (15, 14, 2),
    ],
)
def test_monthly_cents_rounds_up_to_the_cent(remaining, months, expected):
    assert monthly_cents(remaining, months) == expected


def test_month_label_is_month_dot_year():
    assert month_label("2027-12") == "12.2027"
    assert month_label("2027-03") == "03.2027"
