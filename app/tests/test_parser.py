from datetime import date

import pytest

from finbot.parser import Entry, ParseError, parse_entries, parse_entry

TODAY = date(2026, 11, 1)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("25 coffee", Entry("expense", 2500, "EUR", "coffee", "coffee", None, TODAY)),
        (
            "12,50 Lunch at work",
            Entry("expense", 1250, "EUR", "Lunch at work", "lunch", None, TODAY),
        ),
        ("+3000 salary", Entry("income", 300000, "EUR", "salary", "salary", None, TODAY)),
        ("1200 uah taxi", Entry("expense", 120000, "UAH", "taxi", "taxi", None, TODAY)),
        (
            "25 coffee yesterday",
            Entry("expense", 2500, "EUR", "coffee", "coffee", None, date(2026, 10, 31)),
        ),
        (
            "25 coffee 15.11",
            Entry("expense", 2500, "EUR", "coffee", "coffee", None, date(2025, 11, 15)),
        ),
        ("25 yesterday", Entry("expense", 2500, "EUR", "yesterday", "yesterday", None, TODAY)),
        ("save 200 emergency", Entry("save", 20000, "EUR", "", "", "emergency", TODAY)),
        ("take 50 Emergency", Entry("take", 5000, "EUR", "", "", "emergency", TODAY)),
    ],
)
def test_parse(text, expected):
    assert parse_entry(text, TODAY) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("25 save money", Entry("expense", 2500, "EUR", "save money", "save", None, TODAY)),
        ("25 coffee 200", Entry("expense", 2500, "EUR", "coffee 200", "coffee", None, TODAY)),
        (
            "25   lunch   at WORK",
            Entry("expense", 2500, "EUR", "lunch at WORK", "lunch", None, TODAY),
        ),
        (
            "25 coffee YESTERDAY",
            Entry("expense", 2500, "EUR", "coffee", "coffee", None, date(2026, 10, 31)),
        ),
        (
            "25 coffee 01.11",
            Entry("expense", 2500, "EUR", "coffee", "coffee", None, TODAY),
        ),
        (
            "25 coffee 02.11",
            Entry("expense", 2500, "EUR", "coffee", "coffee", None, date(2025, 11, 2)),
        ),
        (
            "25 coffee 05.11",
            Entry("expense", 2500, "EUR", "coffee", "coffee", None, date(2025, 11, 5)),
        ),
        (
            "+€25 salary",
            Entry("income", 2500, "EUR", "salary", "salary", None, TODAY),
        ),
        (
            "save €200 emergency",
            Entry("save", 20000, "EUR", "", "", "emergency", TODAY),
        ),
        (
            "save 200€ emergency",
            Entry("save", 20000, "EUR", "", "", "emergency", TODAY),
        ),
        (
            "save 200 € emergency",
            Entry("save", 20000, "EUR", "", "", "emergency", TODAY),
        ),
        (
            "save 200 eur emergency",
            Entry("save", 20000, "EUR", "", "", "emergency", TODAY),
        ),
        (
            "SAVE 200 Emergency",
            Entry("save", 20000, "EUR", "", "", "emergency", TODAY),
        ),
        (
            "save 200 emergency 28.10",
            Entry("save", 20000, "EUR", "", "", "emergency", date(2026, 10, 28)),
        ),
        (
            "take 50 emergency yesterday",
            Entry("take", 5000, "EUR", "", "", "emergency", date(2026, 10, 31)),
        ),
        (
            "save 200 yesterday",
            Entry("save", 20000, "EUR", "", "", "yesterday", TODAY),
        ),
    ],
)
def test_parse_more(text, expected):
    assert parse_entry(text, TODAY) == expected


@pytest.mark.parametrize("text", ["€25 coffee", "25€ coffee", "25 € coffee", "25 EUR coffee"])
def test_eur_forms(text):
    assert parse_entry(text, TODAY).currency == "EUR"


@pytest.mark.parametrize(
    "text,cur", [("25 usd book", "USD"), ("$5 tip", "USD"), ("₴100 metro", "UAH")]
)
def test_currencies(text, cur):
    assert parse_entry(text, TODAY).currency == cur


def test_dates():
    assert parse_entry("25 coffee 28.10", TODAY).on == date(2026, 10, 28)
    assert parse_entry("25 coffee 28.10.2025", TODAY).on == date(2025, 10, 28)


def test_full_date_in_future_is_rejected():
    with pytest.raises(ParseError) as exc:
        parse_entry("25 coffee 01.01.2030", TODAY)
    assert str(exc.value) == "That date is in the future. Use a date like 28.10 or 28.10.2026"


def test_full_date_tomorrow_is_rejected():
    with pytest.raises(ParseError, match="That date is in the future"):
        parse_entry("25 coffee 02.11.2026", TODAY)


def test_full_date_today_is_accepted():
    assert parse_entry("25 coffee 01.11.2026", TODAY).on == TODAY


@pytest.mark.parametrize(
    "today,expected",
    [
        (date(2028, 1, 15), date(2024, 2, 29)),
        (date(2028, 3, 10), date(2028, 2, 29)),
        (date(2029, 1, 15), date(2028, 2, 29)),
    ],
)
def test_dd_mm_without_year_is_latest_past_date(today, expected):
    assert parse_entry("25 coffee 29.02", today).on == expected


def test_dd_mm_without_year_looks_back_at_most_4_years():
    with pytest.raises(ParseError, match="Use a date like"):
        parse_entry("25 coffee 29.02", date(2101, 1, 1))


@pytest.mark.parametrize("prefix", ["25 ", "+25 "])
def test_note_of_100_characters_is_accepted(prefix):
    assert parse_entry(prefix + "a" * 100, TODAY).note == "a" * 100


@pytest.mark.parametrize("prefix", ["25 ", "+25 "])
def test_note_over_100_characters_is_rejected(prefix):
    with pytest.raises(ParseError) as exc:
        parse_entry(prefix + "a" * 101, TODAY)
    assert str(exc.value) == "Keep the note under 100 characters, e.g. 25 coffee"


@pytest.mark.parametrize("verb", ["save", "take"])
def test_pot_name_of_30_letters_is_accepted(verb):
    assert parse_entry(f"{verb} 200 " + "a" * 30, TODAY).pot == "a" * 30


@pytest.mark.parametrize("verb", ["save", "take"])
def test_pot_name_over_30_letters_is_rejected(verb):
    with pytest.raises(ParseError) as exc:
        parse_entry(f"{verb} 200 " + "a" * 31, TODAY)
    assert str(exc.value) == "Pot name up to 30 letters, e.g. save 200 emergency"


@pytest.mark.parametrize("code", ["GBP", "CHF", "PLN", "CZK", "HUF", "TRY", "JPY"])
def test_unsupported_currency_right_after_amount(code):
    with pytest.raises(ParseError) as exc:
        parse_entry(f"25 {code.lower()} coffee", TODAY)
    assert str(exc.value) == f"{code} is not supported. Use EUR, USD or UAH"


def test_other_currency_word_after_attached_symbol_stays_in_note():
    assert parse_entry("€25 usd book", TODAY) == Entry(
        "expense", 2500, "EUR", "usd book", "usd", None, TODAY
    )


def test_same_currency_word_after_attached_symbol_is_consumed():
    assert parse_entry("€25 EUR coffee", TODAY) == Entry(
        "expense", 2500, "EUR", "coffee", "coffee", None, TODAY
    )


@pytest.mark.parametrize(
    "text,msg",
    [
        ("25", "Add a word after the amount"),
        ("25 eur", "Add a word after the amount"),
        ("", "Start with the amount"),
        ("coffee 25", "Start with the amount"),
        ("+ coffee", "Start with the amount"),
        ("1 200 taxi", "Write 1200 without spaces"),
        ("25 gbp beer", "GBP is not supported"),
        ("25 gbp", "GBP is not supported"),
        ("€25 gbp beer", "GBP is not supported"),
        ("25 coffee 31.02", "Use a date like"),
        ("25 31.02", "Use a date like"),
        ("3 water 1.5", "Use a date like"),
        ("25 coffee 28.10.26", "Use a date like"),
        ("25 coffee 5.11", "Use a date like"),
        ("1 200,50 taxi", "Write 1200 without spaces"),
        ("1 200.50 taxi", "Write 1200 without spaces"),
        ("1 200€ taxi", "Write 1200 without spaces"),
        ("25 15.11", "Write 1200 without spaces"),
        ("save 1 200", "Use: save 200 emergency"),
        ("take 5 28.10", "Use: save 200 emergency"),
        ("save emergency", "Use: save 200 emergency"),
        ("save", "Use: save 200 emergency"),
        ("save 200", "Use: save 200 emergency"),
        ("save 200 emergency extra", "Use: save 200 emergency"),
        ("save 200 emergency eur", "Use: save 200 emergency"),
        ("save 1 200 emergency", "Use: save 200 emergency"),
        ("save 200 emergency 31.02", "Use a date like"),
        ("save 200 usd emergency", "Pots are in EUR"),
        ("save 200 gbp emergency", "Pots are in EUR"),
        ("save $200 emergency", "Pots are in EUR"),
        ("25.999 x", "Amount must be like"),
        ("-25 coffee", "Amount must be like"),
        ("0 coffee", "Amount must be like"),
    ],
)
def test_errors(text, msg):
    with pytest.raises(ParseError, match=msg):
        parse_entry(text, TODAY)


@pytest.mark.parametrize(
    "text,msg",
    [
        ("25", "Add a word after the amount, e.g. 25 coffee"),
        ("coffee 25", "Start with the amount, e.g. 25 coffee"),
        ("25.999 x", "Amount must be like 25 or 12,50"),
        ("1 200 taxi", "Write 1200 without spaces, e.g. 1200 taxi"),
        ("25 gbp beer", "GBP is not supported. Use EUR, USD or UAH"),
        ("25 coffee 31.02", "Use a date like 28.10 or 28.10.2026"),
        ("save 200", "Use: save 200 emergency"),
        ("save 200 usd emergency", "Pots are in EUR for now"),
        ("1200 taxi uah", "Put the currency right after the amount, e.g. 1200 uah taxi"),
        ("25 book usd", "Put the currency right after the amount, e.g. 1200 uah taxi"),
        ("25 book USD", "Put the currency right after the amount, e.g. 1200 uah taxi"),
        ("25 book €", "Put the currency right after the amount, e.g. 1200 uah taxi"),
        ("1200 taxi uah yesterday", "Put the currency right after the amount, e.g. 1200 uah taxi"),
        ("25 beer gbp", "Put the currency right after the amount, e.g. 1200 uah taxi"),
        ("25 " + "a" * 101, "Keep the note under 100 characters, e.g. 25 coffee"),
        ("save 200 " + "a" * 31, "Pot name up to 30 letters, e.g. save 200 emergency"),
        ("25 coffee 01.01.2030", "That date is in the future. Use a date like 28.10 or 28.10.2026"),
    ],
)
def test_error_full_text(text, msg):
    with pytest.raises(ParseError) as exc:
        parse_entry(text, TODAY)
    assert str(exc.value) == msg


RENT = Entry("expense", 85000, "EUR", "rent", "rent", None, TODAY)
UTILITIES = Entry("expense", 12000, "EUR", "utilities", "utilities", None, TODAY)
INTERNET = Entry("expense", 3000, "EUR", "internet", "internet", None, TODAY)


def test_three_lines_are_three_entries():
    text = "850.00 rent\n120 utilities\n30 internet"

    assert parse_entries(text, TODAY) == [RENT, UTILITIES, INTERNET]


def test_commas_between_entries_make_three_entries():
    text = "850.00 rent, 120 utilities, 30 internet"

    assert parse_entries(text, TODAY) == [RENT, UTILITIES, INTERNET]


def test_commas_and_lines_can_be_mixed():
    text = "850.00 rent, 120 utilities\n30 internet"

    assert parse_entries(text, TODAY) == [RENT, UTILITIES, INTERNET]


def test_blank_lines_and_spaces_around_lines_are_ignored():
    text = "\n  850.00 rent  \n\n   \n120 utilities\n\n"

    assert parse_entries(text, TODAY) == [RENT, UTILITIES]


def test_comma_inside_a_note_does_not_split():
    [entry] = parse_entries("25 coffee, croissant", TODAY)

    assert entry.note == "coffee, croissant"


@pytest.mark.parametrize("text,cents", [("12,50 coffee", 1250), ("25 coffee,30 tea", 2500)])
def test_comma_without_a_space_after_it_does_not_split(text, cents):
    [entry] = parse_entries(text, TODAY)

    assert entry.amount_cents == cents


def test_comma_in_a_split_number_is_parsed_as_before():
    with pytest.raises(ParseError) as exc:
        parse_entries("1 200,50 taxi", TODAY)

    assert str(exc.value) == "Write 1200 without spaces, e.g. 1200 taxi"


@pytest.mark.parametrize(
    "text,parts",
    [
        ("25 coffee,  30 tea", 2),
        ("25 coffee , 30 tea", 2),
        ("25 coffee, +30 refund", 2),
        ("25 coffee, $30 book", 2),
        ("25 coffee, 12,50 tea", 2),
        ("25 coffee, saved up", 1),
        ("25 coffee, save", 1),
        ("25 coffee, taken", 1),
        ("25 coffee, take away", 1),
        ("25 coffee, save the date", 1),
        ("25 coffee, save €5 emergency", 2),
        ("25 coffee, take  5 emergency", 2),
        ("25 coffee, $ cash", 1),
        ("25 coffee, +", 1),
    ],
)
def test_comma_splits_only_before_something_that_starts_an_entry(text, parts):
    assert len(parse_entries(text, TODAY)) == parts


@pytest.mark.parametrize("text", ["25 coffee, take away", "25 coffee, save the date"])
def test_save_or_take_without_an_amount_stays_in_the_note(text):
    [entry] = parse_entries(text, TODAY)

    assert entry.note == text.removeprefix("25 ")


def test_income_then_expense():
    assert parse_entries("+3000 salary, 30 internet", TODAY) == [
        Entry("income", 300000, "EUR", "salary", "salary", None, TODAY),
        INTERNET,
    ]


def test_currency_symbols_start_an_entry():
    assert parse_entries("€5 tip, $3 gum", TODAY) == [
        Entry("expense", 500, "EUR", "tip", "tip", None, TODAY),
        Entry("expense", 300, "USD", "gum", "gum", None, TODAY),
    ]


def test_pot_move_then_expense():
    assert parse_entries("save 200 emergency, 30 internet", TODAY) == [
        Entry("save", 20000, "EUR", "", "", "emergency", TODAY),
        INTERNET,
    ]


def test_pot_word_in_any_case_starts_an_entry():
    assert parse_entries("30 internet, TAKE 50 emergency", TODAY) == [
        INTERNET,
        Entry("take", 5000, "EUR", "", "", "emergency", TODAY),
    ]


def test_pot_move_after_a_comma_splits_in_either_order():
    assert parse_entries("30 internet, take 50 emergency", TODAY) == [
        INTERNET,
        Entry("take", 5000, "EUR", "", "", "emergency", TODAY),
    ]


def test_a_comma_at_the_start_of_a_line_leaves_no_empty_part():
    assert parse_entries("25 tea\n, 30 coffee", TODAY) == [
        Entry("expense", 2500, "EUR", "tea", "tea", None, TODAY),
        Entry("expense", 3000, "EUR", "coffee", "coffee", None, TODAY),
    ]


def test_a_lone_leading_comma_gives_the_plain_start_hint():
    with pytest.raises(ParseError) as exc:
        parse_entries(", 25 coffee", TODAY)

    assert str(exc.value) == "Start with the amount, e.g. 25 coffee"


@pytest.mark.parametrize(
    "text,notes",
    [
        ("850.00 rent,\n120 utilities", ["rent", "utilities"]),
        ("25 coffee, 30 tea,", ["coffee", "tea"]),
        ("25 coffee , 30 tea ,\n40 pie", ["coffee", "tea", "pie"]),
        ("25 coffee,\n,\n30 tea", ["coffee", "tea"]),
    ],
)
def test_a_trailing_comma_is_dropped_from_each_of_several_entries(text, notes):
    assert [entry.note for entry in parse_entries(text, TODAY)] == notes


def test_a_single_entry_keeps_its_trailing_comma():
    assert parse_entries("25 coffee,", TODAY) == [parse_entry("25 coffee,", TODAY)]
    assert parse_entries("25 coffee,", TODAY)[0].note == "coffee,"


def test_one_entry_behaves_like_parse_entry():
    assert parse_entries("25 coffee 28.10", TODAY) == [parse_entry("25 coffee 28.10", TODAY)]
    assert parse_entries("\n25 coffee\n\n", TODAY) == [parse_entry("25 coffee", TODAY)]


@pytest.mark.parametrize("text", ["coffee 25", "", "   ", "\n \n"])
def test_a_message_without_an_entry_gets_the_start_hint(text):
    with pytest.raises(ParseError) as exc:
        parse_entries(text, TODAY)

    assert str(exc.value) == "Start with the amount, e.g. 25 coffee"


def test_ten_entries_are_accepted():
    text = "\n".join(f"{number} item" for number in range(1, 11))

    assert len(parse_entries(text, TODAY)) == 10


def test_eleven_entries_are_refused_before_any_is_checked():
    text = "\n".join(["oops"] + [f"{number} item" for number in range(1, 11)])

    with pytest.raises(ParseError) as exc:
        parse_entries(text, TODAY)

    assert str(exc.value) == (
        "Up to 10 entries in one message. Nothing saved: send them in two messages."
    )


def test_a_bad_part_refuses_everything_and_names_the_entry():
    with pytest.raises(ParseError) as exc:
        parse_entries("25 coffee\n1 200 taxi\n30 lunch", TODAY)

    assert str(exc.value) == (
        'Nothing saved. Entry 2 "1 200 taxi": Write 1200 without spaces, e.g. 1200 taxi'
    )


def test_the_first_bad_part_is_the_one_named():
    with pytest.raises(ParseError, match='Entry 1 "coffee 25"'):
        parse_entries("coffee 25\n1 200 taxi", TODAY)


@pytest.mark.parametrize("length", [40, 41, 50])
def test_a_bad_part_over_40_characters_is_quoted_as_39_characters_and_an_ellipsis(length):
    part = "0 " + "x" * (length - 2)
    quoted = part if length == 40 else part[:39] + "…"

    with pytest.raises(ParseError) as exc:
        parse_entries(f"25 coffee\n{part}", TODAY)

    assert str(exc.value) == f'Nothing saved. Entry 2 "{quoted}": Amount must be like 25 or 12,50'
