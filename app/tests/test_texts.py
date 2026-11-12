from dataclasses import replace
from datetime import date
from decimal import Decimal

from finbot.budgets import Budget
from finbot.categories import Category
from finbot.drafts import DraftEntry
from finbot.ledger import Record
from finbot.savings import Pot, PotMove
from finbot.texts import (
    AI_TOO_LONG,
    CLEAR_TOO_OLD,
    DRAFT_CANCEL_FAILED,
    DRAFT_CANCELLED,
    DRAFT_REPLACED,
    DRAFT_SAVE_FAILED,
    HELP,
    NOTHING_DELETED,
    NOTHING_TO_UNDO,
    PHOTO_NEEDS_AI,
    PHOTO_UNREADABLE,
    as_pre,
    budget_removed_text,
    budget_set_text,
    budgets_text,
    category_added_text,
    category_list_text,
    category_renamed_text,
    category_unknown_text,
    clear_ask_text,
    clear_button_text,
    clear_changed_text,
    clear_done_text,
    clear_nothing_text,
    draft_closed_text,
    draft_saved_text,
    draft_text,
    entry_line,
    help_text,
    last_button_text,
    last_text,
    pot_text,
    rate_set_text,
    removed_text,
    save_button_text,
    saved_text,
    savings_text,
    split_report,
)

DAY = date(2026, 11, 1)

COFFEE = Record(
    id=1,
    kind="expense",
    amount_cents=2500,
    currency="EUR",
    rate=None,
    eur_cents=2500,
    category="Eating out",
    pot=None,
    keyword="coffee",
    note="coffee",
    on=DAY,
)

POT_SAVE = Record(
    id=2,
    kind="save",
    amount_cents=20000,
    currency="EUR",
    rate=None,
    eur_cents=20000,
    category=None,
    pot="emergency",
    keyword="",
    note="",
    on=DAY,
)

USD_BOOK = Record(
    id=5,
    kind="expense",
    amount_cents=2500,
    currency="USD",
    rate=Decimal("0.9200"),
    eur_cents=2300,
    category=None,
    pot=None,
    keyword="book",
    note="book",
    on=DAY,
)

EMERGENCY = Pot(id=1, name="emergency", total_cents=140000, goal_cents=1000000)


def test_saved_text_eur_expense_with_category():
    assert saved_text(COFFEE) == "Saved 01.11: -25.00 EUR · coffee → Eating out"


def test_saved_text_is_dated_with_the_entry_day():
    yesterday = replace(COFFEE, on=date(2026, 10, 31))
    assert saved_text(yesterday) == "Saved 31.10: -25.00 EUR · coffee → Eating out"


def test_saved_text_converted_foreign_shows_eur_and_rate():
    taxi = Record(
        id=3,
        kind="expense",
        amount_cents=120000,
        currency="UAH",
        rate=Decimal("0.0220"),
        eur_cents=2640,
        category="Transport",
        pot=None,
        keyword="taxi",
        note="taxi",
        on=DAY,
    )
    assert saved_text(taxi) == (
        "Saved 01.11: -1,200.00 UAH (≈ -26.40 EUR at 0.0220) · taxi → Transport"
    )


def test_saved_text_income_uses_plus():
    salary = Record(
        id=4,
        kind="income",
        amount_cents=300000,
        currency="EUR",
        rate=None,
        eur_cents=300000,
        category="Salary",
        pot=None,
        keyword="salary",
        note="salary",
        on=DAY,
    )
    assert saved_text(salary) == "Saved 01.11: +3,000.00 EUR · salary → Salary"


def test_saved_text_pending_asks_for_rate():
    book = Record(
        id=5,
        kind="expense",
        amount_cents=2500,
        currency="USD",
        rate=None,
        eur_cents=None,
        category="Shopping",
        pot=None,
        keyword="book",
        note="book",
        on=DAY,
    )
    assert saved_text(book) == (
        "Saved 01.11: -25.00 USD · book → Shopping\n"
        "No USD rate yet. Send /rate usd <EUR per 1 USD> and I will convert it."
    )


def test_saved_text_uncategorized_asks_for_category():
    dm = replace(COFFEE, amount_cents=4200, eur_cents=4200, category=None, keyword="dm", note="dm")
    assert saved_text(dm) == 'Saved 01.11: -42.00 EUR · dm\nNew word "dm" - pick a category:'


def test_saved_text_pending_and_uncategorized_gives_rate_line_then_category_line():
    dm = Record(
        id=6,
        kind="expense",
        amount_cents=10000,
        currency="UAH",
        rate=None,
        eur_cents=None,
        category=None,
        pot=None,
        keyword="dm",
        note="dm",
        on=DAY,
    )
    assert saved_text(dm) == (
        "Saved 01.11: -100.00 UAH · dm\n"
        "No UAH rate yet. Send /rate uah <EUR per 1 UAH> and I will convert it.\n"
        'New word "dm" - pick a category:'
    )


def test_pot_text_save_uses_plus():
    assert pot_text(EMERGENCY, "save", 20000, DAY) == (
        "Emergency pot 01.11: +200.00 EUR · total 1,400.00 EUR"
    )


def test_pot_text_take_uses_minus():
    assert pot_text(EMERGENCY, "take", 5000, DAY) == (
        "Emergency pot 01.11: -50.00 EUR · total 1,400.00 EUR"
    )


def test_pot_text_is_dated_with_the_entry_day():
    assert pot_text(EMERGENCY, "save", 20000, date(2026, 10, 28)) == (
        "Emergency pot 28.10: +200.00 EUR · total 1,400.00 EUR"
    )


def test_removed_text_expense():
    assert removed_text(COFFEE) == "Removed 01.11: -25.00 EUR · coffee"


def test_removed_text_is_dated_with_the_entry_day():
    yesterday = replace(COFFEE, on=date(2026, 10, 31))
    assert removed_text(yesterday) == "Removed 31.10: -25.00 EUR · coffee"


def test_removed_text_pot_save():
    assert removed_text(POT_SAVE) == "Removed 01.11: +200.00 EUR · emergency pot"


def test_removed_text_pot_take_uses_minus():
    take = replace(POT_SAVE, kind="take", amount_cents=5000, eur_cents=5000)
    assert removed_text(take) == "Removed 01.11: -50.00 EUR · emergency pot"


def test_removed_text_foreign_shows_own_currency():
    taxi = Record(
        id=3,
        kind="expense",
        amount_cents=120000,
        currency="UAH",
        rate=Decimal("0.0220"),
        eur_cents=2640,
        category="Transport",
        pot=None,
        keyword="taxi",
        note="taxi",
        on=DAY,
    )
    assert removed_text(taxi) == "Removed 01.11: -1,200.00 UAH · taxi"


def test_nothing_to_undo_text():
    assert NOTHING_TO_UNDO == "Nothing to undo."


def test_rate_set_text_without_conversion():
    assert rate_set_text("USD", Decimal("0.92"), []) == "Saved: 1 USD = 0.92 EUR."


def test_rate_set_text_keeps_rate_as_typed():
    assert rate_set_text("UAH", Decimal("0.022"), []) == "Saved: 1 UAH = 0.022 EUR."


def test_rate_set_text_one_converted_entry_is_listed_with_its_eur_amount():
    assert rate_set_text("USD", Decimal("0.92"), [USD_BOOK]) == (
        "Saved: 1 USD = 0.92 EUR.\n"
        "Converted 1 entry that was waiting for this rate:\n"
        "01.11 -25.00 USD book = -23.00 EUR"
    )


def test_rate_set_text_many_converted_entries_one_line_each_in_given_order():
    salary = replace(
        USD_BOOK,
        id=6,
        kind="income",
        amount_cents=10000,
        eur_cents=9200,
        keyword="salary",
        note="salary",
        on=date(2026, 10, 31),
    )
    entries = [replace(USD_BOOK, id=4, on=date(2026, 10, 30)), salary, USD_BOOK]
    assert rate_set_text("USD", Decimal("0.92"), entries) == (
        "Saved: 1 USD = 0.92 EUR.\n"
        "Converted 3 entries that were waiting for this rate:\n"
        "30.10 -25.00 USD book = -23.00 EUR\n"
        "31.10 +100.00 USD salary = +92.00 EUR\n"
        "01.11 -25.00 USD book = -23.00 EUR"
    )


def test_rate_set_text_lists_five_entries_then_how_many_more():
    line = "01.11 -25.00 USD book = -23.00 EUR"
    entries = [replace(USD_BOOK, id=i) for i in range(1, 8)]
    assert rate_set_text("USD", Decimal("0.92"), entries) == "\n".join(
        [
            "Saved: 1 USD = 0.92 EUR.",
            "Converted 7 entries that were waiting for this rate:",
            *[line] * 5,
            "...and 2 more",
        ]
    )


def test_rate_set_text_exactly_five_entries_has_no_more_line():
    line = "01.11 -25.00 USD book = -23.00 EUR"
    entries = [replace(USD_BOOK, id=i) for i in range(1, 6)]
    assert rate_set_text("USD", Decimal("0.92"), entries) == "\n".join(
        [
            "Saved: 1 USD = 0.92 EUR.",
            "Converted 5 entries that were waiting for this rate:",
            *[line] * 5,
        ]
    )


def test_rate_set_text_six_entries_show_five_and_one_more():
    line = "01.11 -25.00 USD book = -23.00 EUR"
    entries = [replace(USD_BOOK, id=i) for i in range(1, 7)]
    assert rate_set_text("USD", Decimal("0.92"), entries) == "\n".join(
        [
            "Saved: 1 USD = 0.92 EUR.",
            "Converted 6 entries that were waiting for this rate:",
            *[line] * 5,
            "...and 1 more",
        ]
    )


def test_savings_text_without_pots():
    assert savings_text([], {}, DAY) == "No pots yet. Start one with: save 100 emergency"


def test_savings_text_pot_with_goal_and_moves_then_blank_line_then_next_pot():
    moves = {
        1: [
            PotMove(entry_id=3, kind="save", amount_cents=40000, on=date(2026, 10, 5)),
            PotMove(entry_id=4, kind="take", amount_cents=5000, on=date(2026, 10, 6)),
        ]
    }
    travel = Pot(id=2, name="travel", total_cents=30000, goal_cents=None)
    assert savings_text([EMERGENCY, travel], moves, DAY) == (
        "Emergency: 1,400.00 EUR of 10,000.00 (14%)\n"
        "  05.10 +400.00\n"
        "  06.10 -50.00\n"
        "\n"
        "Travel: 300.00 EUR"
    )


def test_savings_text_percent_rounds_half_up():
    rainy = Pot(id=3, name="rainy", total_cents=1, goal_cents=8)
    assert savings_text([rainy], {}, DAY) == "Rainy: 0.01 EUR of 0.08 (13%)"


def _goal_pot(total_cents: int, goal_cents: int, goal_month: str | None) -> Pot:
    return Pot(
        id=1,
        name="emergency",
        total_cents=total_cents,
        goal_cents=goal_cents,
        goal_month=goal_month,
    )


def test_savings_text_goal_month_adds_the_monthly_amount_rounded_up():
    # 9,700.00 left over 14 months (11.2026 to 12.2027) is 692.857... and rounds up to 692.86.
    pot = _goal_pot(30000, 1_000_000, "2027-12")
    assert savings_text([pot], {}, DAY) == (
        "Emergency: 300.00 EUR of 10,000.00 (3%) · by 12.2027: 692.86 EUR a month"
    )


def test_savings_text_one_cent_left_is_one_cent_a_month():
    pot = _goal_pot(999_999, 1_000_000, "2027-12")
    assert savings_text([pot], {}, DAY) == (
        "Emergency: 9,999.99 EUR of 10,000.00 (100%) · by 12.2027: 0.01 EUR a month"
    )


def test_savings_text_goal_reached_when_total_equals_or_exceeds_the_goal():
    equal = _goal_pot(1_000_000, 1_000_000, "2027-12")
    above = _goal_pot(1_200_000, 1_000_000, "2027-12")
    assert savings_text([equal], {}, DAY) == (
        "Emergency: 10,000.00 EUR of 10,000.00 (100%) · goal reached"
    )
    assert savings_text([above], {}, DAY) == (
        "Emergency: 12,000.00 EUR of 10,000.00 (120%) · goal reached"
    )


def test_savings_text_goal_month_in_the_past_says_it_has_passed():
    pot = _goal_pot(30000, 1_000_000, "2026-10")
    assert savings_text([pot], {}, DAY) == (
        "Emergency: 300.00 EUR of 10,000.00 (3%) · 10.2026 has passed"
    )


def test_savings_text_goal_reached_wins_over_a_passed_month():
    pot = _goal_pot(1_000_000, 1_000_000, "2026-10")
    assert savings_text([pot], {}, DAY).endswith(" · goal reached")


def test_savings_text_goal_without_month_has_no_deadline_part():
    pot = _goal_pot(30000, 1_000_000, None)
    assert savings_text([pot], {}, DAY) == "Emergency: 300.00 EUR of 10,000.00 (3%)"


def test_savings_text_deadline_part_stays_on_the_pot_line_above_the_moves():
    pot = _goal_pot(30000, 1_000_000, "2027-12")
    moves = {1: [PotMove(entry_id=3, kind="save", amount_cents=30000, on=date(2026, 10, 5))]}
    assert savings_text([pot], moves, DAY) == (
        "Emergency: 300.00 EUR of 10,000.00 (3%) · by 12.2027: 692.86 EUR a month\n  05.10 +300.00"
    )


def test_savings_text_shows_at_most_five_moves_in_given_order():
    moves = [
        PotMove(entry_id=i, kind="save", amount_cents=10000, on=date(2026, 10, i))
        for i in range(1, 7)
    ]
    travel = Pot(id=2, name="travel", total_cents=60000, goal_cents=None)
    assert savings_text([travel], {2: moves}, DAY) == (
        "Travel: 600.00 EUR\n"
        "  01.10 +100.00\n"
        "  02.10 +100.00\n"
        "  03.10 +100.00\n"
        "  04.10 +100.00\n"
        "  05.10 +100.00"
    )


def test_last_text_without_entries():
    assert last_text([]) == "No entries yet."


def test_last_text_numbers_lines_and_shows_pot_moves_and_income():
    salary = Record(
        id=4,
        kind="income",
        amount_cents=300000,
        currency="EUR",
        rate=None,
        eur_cents=300000,
        category="Salary",
        pot=None,
        keyword="salary",
        note="salary",
        on=DAY,
    )
    assert last_text([COFFEE, POT_SAVE, salary]) == (
        "1. 01.11 -25.00 EUR coffee → Eating out\n"
        "2. 01.11 +200.00 EUR emergency pot\n"
        "3. 01.11 +3,000.00 EUR salary → Salary"
    )


def test_last_text_uncategorized_foreign_has_no_arrow():
    book = Record(
        id=5,
        kind="expense",
        amount_cents=2500,
        currency="USD",
        rate=Decimal("0.9200"),
        eur_cents=2300,
        category=None,
        pot=None,
        keyword="book",
        note="book",
        on=DAY,
    )
    assert last_text([book]) == "1. 01.11 -25.00 USD (≈ -23.00 EUR) book"


def test_last_text_pending_foreign_says_no_rate_yet():
    pending = replace(USD_BOOK, rate=None, eur_cents=None)
    assert last_text([pending]) == "1. 01.11 -25.00 USD (no rate yet) book"


def test_last_text_converted_foreign_shows_eur_then_label_and_category():
    taxi = Record(
        id=3,
        kind="expense",
        amount_cents=120000,
        currency="UAH",
        rate=Decimal("0.0220"),
        eur_cents=2640,
        category="Transport",
        pot=None,
        keyword="taxi",
        note="taxi",
        on=DAY,
    )
    assert last_text([taxi]) == "1. 01.11 -1,200.00 UAH (≈ -26.40 EUR) taxi → Transport"


def test_last_text_converted_foreign_income_shows_plus_on_both_amounts():
    salary = replace(
        USD_BOOK, kind="income", amount_cents=10000, eur_cents=9200, keyword="salary", note="salary"
    )
    assert last_text([salary]) == "1. 01.11 +100.00 USD (≈ +92.00 EUR) salary"


def test_entry_line_is_the_last_line_without_its_number():
    assert entry_line(COFFEE) == "01.11 -25.00 EUR coffee → Eating out"
    assert entry_line(POT_SAVE) == "01.11 +200.00 EUR emergency pot"
    assert entry_line(USD_BOOK) == "01.11 -25.00 USD (≈ -23.00 EUR) book"
    assert last_text([COFFEE]) == f"1. {entry_line(COFFEE)}"


def test_last_button_text_numbers_the_entry_with_label_sign_amount_and_currency():
    assert last_button_text(1, COFFEE) == "1. coffee -25.00 EUR"
    assert last_button_text(3, POT_SAVE) == "3. emergency pot +200.00 EUR"
    assert last_button_text(2, USD_BOOK) == "2. book -25.00 USD"


def test_last_button_text_cuts_the_label_to_20_characters():
    assert last_button_text(1, replace(COFFEE, note="a" * 20)) == f"1. {'a' * 20} -25.00 EUR"
    assert last_button_text(1, replace(COFFEE, note="a" * 21)) == f"1. {'a' * 20} -25.00 EUR"


def test_last_button_text_drops_the_space_a_cut_leaves_at_the_end_of_the_label():
    cut_after_space = replace(COFFEE, note="a" * 19 + " bcd")

    assert last_button_text(1, cut_after_space) == f"1. {'a' * 19} -25.00 EUR"


def test_as_pre_wraps_plain_text():
    assert as_pre("Saved: -25.00 EUR") == "<pre>Saved: -25.00 EUR</pre>"


def test_as_pre_escapes_html():
    assert as_pre("a < b & c") == "<pre>a &lt; b &amp; c</pre>"


def test_help_has_one_line_per_example_in_order():
    examples = [
        "25 coffee",
        "1200 uah taxi",
        "+3000 salary",
        "25 coffee yesterday",
        "save 200 emergency",
        "850.00 rent, 120 utilities",
        "/rate usd 0.92",
        "/month",
        "/goal emergency 10000 12.2027",
        "/category add Rent",
        "/budget Rent 850.00",
    ]
    lines = HELP.split("\n")
    assert len(lines) == len(examples) + 1
    for line, example in zip(lines[:-1], examples, strict=True):
        assert line.startswith(f"{example} - ")
        assert len(line) > len(example) + len(" - ")
    assert lines[-1] == "All commands: the Menu button next to the message field"


def test_help_explains_several_entries_right_after_the_pot_line():
    lines = HELP.split("\n")

    assert lines[4:6] == [
        "save 200 emergency - add 200 EUR to the emergency pot",
        "850.00 rent, 120 utilities - several entries (or one per line)",
    ]


def test_category_list_text_shows_both_kinds_then_the_examples():
    expense = [Category(1, "Groceries", "expense"), Category(2, "Rent", "expense")]
    income = [Category(3, "Salary", "income"), Category(4, "Other income", "income")]

    assert category_list_text(expense, income).split("\n") == [
        "Expense: Groceries, Rent",
        "Income: Salary, Other income",
        "Add: /category add Rent · Rename: /category rename Rent Housing",
    ]


def test_category_added_text_names_the_kind():
    assert category_added_text(Category(1, "Rent", "expense")) == "Added expense category Rent."
    assert category_added_text(Category(2, "Bonus", "income")) == "Added income category Bonus."


def test_category_renamed_text():
    assert category_renamed_text("Eating out", "Food") == "Renamed Eating out to Food."


def test_category_unknown_text_points_to_the_list():
    assert category_unknown_text("Eating") == "No category named Eating. See /category"


def test_category_unknown_text_cuts_a_long_name_to_30_characters():
    assert category_unknown_text("a" * 100) == f"No category named {'a' * 30}. See /category"
    assert category_unknown_text("a" * 30) == f"No category named {'a' * 30}. See /category"


def test_saved_text_adds_the_budget_line_for_the_month_of_the_entry():
    budget = Budget("Eating out", 30000, 25000)
    assert saved_text(COFFEE, budget) == (
        "Saved 01.11: -25.00 EUR · coffee → Eating out\n"
        "Eating out: 250.00 of 300.00 in November · 50.00 left"
    )


def test_saved_text_budget_line_names_the_month_of_a_back_dated_entry():
    october = replace(COFFEE, on=date(2026, 10, 31))
    assert saved_text(october, Budget("Eating out", 30000, 25000)).endswith(
        "Eating out: 250.00 of 300.00 in October · 50.00 left"
    )


def test_saved_text_budget_line_when_over_the_limit():
    assert saved_text(COFFEE, Budget("Eating out", 85000, 90000)).endswith(
        "Eating out: 900.00 of 850.00 in November · over by 50.00"
    )


def test_saved_text_budget_line_exactly_at_the_limit():
    assert saved_text(COFFEE, Budget("Eating out", 30000, 30000)).endswith(
        "in November · 0.00 left"
    )


def test_saved_text_budget_line_uses_thousands_separators():
    assert saved_text(COFFEE, Budget("Eating out", 120000, 100000)).endswith(
        "Eating out: 1,000.00 of 1,200.00 in November · 200.00 left"
    )


def test_saved_text_without_a_budget_is_unchanged():
    assert saved_text(COFFEE, None) == saved_text(COFFEE)
    assert saved_text(COFFEE) == "Saved 01.11: -25.00 EUR · coffee → Eating out"


def test_budget_set_text_with_money_left():
    assert budget_set_text(Budget("Rent", 85000, 0), DAY) == (
        "Rent: 850.00 EUR a month. November: spent 0.00, left 850.00."
    )


def test_budget_set_text_when_already_over():
    assert budget_set_text(Budget("Rent", 80000, 90000), DAY) == (
        "Rent: 800.00 EUR a month. November: spent 900.00, over by 100.00."
    )


def test_budget_set_text_when_exactly_at_the_limit():
    assert budget_set_text(Budget("Rent", 80000, 80000), DAY) == (
        "Rent: 800.00 EUR a month. November: spent 800.00, left 0.00."
    )


def test_budget_removed_text():
    assert budget_removed_text("Rent") == "Rent: budget removed."


def test_budgets_text_lists_the_month_then_one_line_per_budget():
    budgets = [Budget("Rent", 85000, 80000), Budget("Eating out", 30000, 32000)]
    assert budgets_text(budgets, DAY).split("\n") == [
        "Budgets, November 2026:",
        "Rent: 800.00 of 850.00 · 50.00 left",
        "Eating out: 320.00 of 300.00 · over by 20.00",
    ]


def test_budgets_text_exactly_at_the_limit():
    assert budgets_text([Budget("Rent", 80000, 80000)], DAY).endswith(
        "Rent: 800.00 of 800.00 · 0.00 left"
    )


def test_budgets_text_without_budgets_says_how_to_set_one():
    assert budgets_text([], DAY) == "No budgets yet. Set one: /budget Rent 850.00"


def test_clear_nothing_text_names_the_month():
    assert clear_nothing_text(2026, 11) == "Nothing to clear in November 2026."


def test_clear_ask_text_with_many_entries():
    assert clear_ask_text(12, 2026, 11) == (
        "Delete all 12 expenses and incomes of November 2026? Savings stay."
    )


def test_clear_ask_text_with_one_entry():
    assert clear_ask_text(1, 2026, 10) == (
        "Delete all 1 expense or income of October 2026? Savings stay."
    )


def test_clear_button_text_counts_the_entries():
    assert clear_button_text(12) == "Delete 12 entries"
    assert clear_button_text(1) == "Delete 1 entry"


def test_clear_done_text_counts_the_deleted_entries_and_warns_about_undo():
    assert clear_done_text(12, 2026, 11) == (
        "Deleted 12 entries of November 2026. /undo will not bring them back."
    )
    assert clear_done_text(1, 2026, 11) == (
        "Deleted 1 entry of November 2026. /undo will not bring them back."
    )


def test_clear_changed_text_asks_to_send_clear_again():
    assert clear_changed_text(2026, 11) == (
        "November 2026 changed since you asked. Send /clear again."
    )


def test_nothing_deleted_text():
    assert NOTHING_DELETED == "Nothing deleted."


def test_clear_too_old_text_asks_to_send_clear_again():
    assert CLEAR_TOO_OLD == "This question is too old. Send /clear again."


def test_split_report_keeps_a_short_text_as_one_piece():
    assert split_report("November 2026\n\nNo entries.") == ["November 2026\n\nNo entries."]


def test_split_report_keeps_a_text_of_exactly_the_limit_as_one_piece():
    text = "a" * 49 + "\n\n" + "b" * 49

    assert split_report(text, 100) == [text]


def test_split_report_splits_on_blank_lines_and_keeps_the_block_order():
    blocks = ["a" * 40, "b" * 40, "c" * 40, "d" * 40]
    pieces = split_report("\n\n".join(blocks), 100)

    assert pieces == [f"{blocks[0]}\n\n{blocks[1]}", f"{blocks[2]}\n\n{blocks[3]}"]


def test_split_report_starts_a_new_piece_when_the_next_block_does_not_fit():
    blocks = ["a" * 60, "b" * 30, "c" * 60]
    pieces = split_report("\n\n".join(blocks), 100)

    assert pieces == [f"{blocks[0]}\n\n{blocks[1]}", blocks[2]]


def test_split_report_splits_one_huge_block_on_line_breaks():
    lines = [f"line {number:02d} " + "x" * 22 for number in range(10)]  # 30 characters each
    pieces = split_report("\n".join(lines), 100)

    assert pieces == ["\n".join(lines[0:3]), "\n".join(lines[3:6]), "\n".join(lines[6:9]), lines[9]]


def test_split_report_fills_the_piece_of_the_short_block_before_a_huge_one():
    short = "Header"
    lines = [f"line {number} " + "x" * 18 for number in range(6)]  # 25 characters each
    pieces = split_report("\n\n".join([short, "\n".join(lines)]), 100)

    assert pieces == [f"{short}\n\n" + "\n".join(lines[0:3]), "\n".join(lines[3:6])]


def test_split_report_cuts_one_huge_line():
    assert split_report("x" * 250, 100) == ["x" * 100, "x" * 100, "x" * 50]


def test_split_report_limit_defaults_to_4000():
    pieces = split_report("x" * 8001)

    assert [len(piece) for piece in pieces] == [4000, 4000, 1]


def test_split_report_pieces_never_pass_the_limit():
    text = "\n\n".join(["a" * 90, "b\n" * 60 + "b", "c" * 250, "d", "e" * 100])
    pieces = split_report(text, 100)

    assert all(len(piece) <= 100 for piece in pieces)
    assert "".join(piece.replace("\n", "") for piece in pieces) == text.replace("\n", "")


def test_saved_text_empty_keyword_asks_for_category_without_a_word():
    no_word = replace(COFFEE, category=None, keyword="")
    assert saved_text(no_word) == "Saved 01.11: -25.00 EUR · coffee\nPick a category:"


def test_draft_texts_are_exact():
    assert AI_TOO_LONG == "Keep it under 1000 characters, or split it into two messages."
    assert PHOTO_NEEDS_AI == "Receipt photos need the AI. Write it as 25 coffee."
    assert PHOTO_UNREADABLE == "Could not read the photo. Send it again."
    assert DRAFT_SAVE_FAILED == "Could not save. Nothing saved. Press Save again."
    assert DRAFT_CANCELLED == "Cancelled. Nothing saved."
    assert DRAFT_CANCEL_FAILED == "Could not cancel. Nothing changed. Press Cancel again."
    assert DRAFT_REPLACED == "Replaced by the draft below. Nothing saved."


def test_draft_text_lists_each_entry_with_sign_category_note_and_date():
    entries = (
        DraftEntry(
            kind="expense",
            amount_cents=2500,
            currency="EUR",
            category_id=1,
            category="Eating out",
            note="кофе с другом",
            on=date(2026, 10, 31),
        ),
        DraftEntry(
            kind="income",
            amount_cents=300000,
            currency="EUR",
            category_id=2,
            category="Salary",
            note="зарплата",
            on=DAY,
        ),
    )
    assert draft_text(entries) == (
        "Draft:\n"
        "1. -25.00 EUR · Eating out · кофе с другом · 31.10.2026\n"
        "2. +3,000.00 EUR · Salary · зарплата · 01.11.2026"
    )


def test_draft_text_entry_without_category_says_no_category():
    book = DraftEntry(
        kind="expense",
        amount_cents=2500,
        currency="USD",
        category_id=None,
        category=None,
        note="book",
        on=DAY,
    )
    assert draft_text([book]) == "Draft:\n1. -25.00 USD · no category · book · 01.11.2026"


def test_save_button_text_counts_entries():
    assert save_button_text(1) == "Save"
    assert save_button_text(3) == "Save 3 entries"


def test_draft_saved_text_counts_entries():
    assert draft_saved_text(1) == "Saved."
    assert draft_saved_text(3) == "Saved 3 entries."


def test_draft_closed_text_for_every_closed_status():
    assert draft_closed_text("saved") == "Already saved."
    assert draft_closed_text("cancelled") == "Already cancelled."
    assert draft_closed_text("replaced") == "Replaced by a newer draft."
    assert draft_closed_text("expired") == ("This draft is too old. Nothing saved. Send it again.")
    assert draft_closed_text("gone") == "This draft is gone."


def test_help_text_without_ai_is_help_unchanged():
    assert help_text(False) == HELP


def test_help_text_with_ai_adds_three_lines_after_several_entries_and_keeps_menu_last():
    lines = help_text(True).split("\n")
    index = lines.index("850.00 rent, 120 utilities - several entries (or one per line)")
    assert lines[index + 1 : index + 4] == [
        "coffee with a friend yesterday 25 - free text: the bot drafts it, you press Save",
        "a receipt photo - one entry for the total, after you press Save",
        "how much did I spend on eating out in October? - ask about your money",
    ]
    assert lines[-1] == "All commands: the Menu button next to the message field"
    assert len(lines) == len(HELP.split("\n")) + 3
