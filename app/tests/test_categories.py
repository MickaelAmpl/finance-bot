import pytest

from finbot.categories import (
    Category,
    CategoryError,
    add_category,
    category_for_keyword,
    find_category,
    get_category,
    is_valid_name,
    list_categories,
    remember_keyword,
    rename_category,
)


def category_id(conn, name):
    return conn.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()["id"]


def test_expense_categories_in_position_order(conn):
    assert [c.name for c in list_categories(conn, "expense")] == [
        "Groceries",
        "Eating out",
        "Transport",
        "Housing",
        "Utilities",
        "Health",
        "Shopping",
        "Entertainment",
        "Travel",
        "Subscriptions",
        "Gifts",
        "Other",
    ]


def test_income_categories_in_position_order(conn):
    assert [c.name for c in list_categories(conn, "income")] == [
        "Salary",
        "Freelance",
        "Other income",
    ]


def test_get_category_returns_the_stored_row(conn):
    groceries = category_id(conn, "Groceries")
    assert get_category(conn, groceries) == Category(id=groceries, name="Groceries", kind="expense")


def test_get_category_unknown_id_raises_lookup_error(conn):
    with pytest.raises(LookupError):
        get_category(conn, 999)


def test_remembered_keyword_maps_to_its_category(conn):
    eating_out = category_id(conn, "Eating out")
    remember_keyword(conn, "coffee", eating_out)
    assert category_for_keyword(conn, "coffee", "expense") == Category(
        id=eating_out, name="Eating out", kind="expense"
    )


def test_remembering_a_keyword_again_overwrites_its_category(conn):
    remember_keyword(conn, "coffee", category_id(conn, "Eating out"))
    groceries = category_id(conn, "Groceries")
    remember_keyword(conn, "coffee", groceries)
    assert category_for_keyword(conn, "coffee", "expense") == Category(
        id=groceries, name="Groceries", kind="expense"
    )
    assert conn.execute("SELECT COUNT(*) FROM keywords").fetchone()[0] == 1


def test_unmapped_keyword_returns_none(conn):
    assert category_for_keyword(conn, "coffee", "expense") is None


def test_keyword_mapped_to_other_kind_returns_none(conn):
    salary = category_id(conn, "Salary")
    remember_keyword(conn, "salary", salary)
    assert category_for_keyword(conn, "salary", "expense") is None
    assert category_for_keyword(conn, "salary", "income") == Category(
        id=salary, name="Salary", kind="income"
    )


def test_find_category_ignores_case_and_surrounding_spaces(conn):
    eating_out = category_id(conn, "Eating out")
    expected = Category(id=eating_out, name="Eating out", kind="expense")
    assert find_category(conn, "Eating out") == expected
    assert find_category(conn, "  eating OUT ") == expected


def test_find_category_looks_in_both_kinds(conn):
    salary = category_id(conn, "Salary")
    assert find_category(conn, "salary") == Category(id=salary, name="Salary", kind="income")


def test_find_category_unknown_name_returns_none(conn):
    assert find_category(conn, "Rent") is None
    assert find_category(conn, "") is None


def test_find_category_ignores_case_outside_ascii(conn):
    added = add_category(conn, "Кафе", "expense")
    assert find_category(conn, "кафе") == added
    assert find_category(conn, "КАФЕ") == added


@pytest.mark.parametrize("name", ["Rent", "Eating out", "Кафе", "R2", "a" * 30, "3d print"])
def test_is_valid_name_accepts(name):
    assert is_valid_name(name)


@pytest.mark.parametrize("name", ["", " ", "a" * 31, "2026", "12 34", "/rent", "!!!"])
def test_is_valid_name_rejects(name):
    assert not is_valid_name(name)


def test_add_category_goes_last_in_its_kind(conn):
    rent = add_category(conn, "Rent", "expense")
    bonus = add_category(conn, "Bonus", "income")

    assert rent == Category(id=rent.id, name="Rent", kind="expense")
    assert bonus == Category(id=bonus.id, name="Bonus", kind="income")
    assert [c.name for c in list_categories(conn, "expense")][-2:] == ["Other", "Rent"]
    assert [c.name for c in list_categories(conn, "income")][-2:] == ["Other income", "Bonus"]
    positions = conn.execute(
        "SELECT kind, MAX(position) AS last FROM categories GROUP BY kind ORDER BY kind"
    ).fetchall()
    assert [tuple(row) for row in positions] == [("expense", 13), ("income", 4)]


def test_add_category_keeps_the_name_as_given(conn):
    add_category(conn, "rEnT", "expense")
    assert [c.name for c in list_categories(conn, "expense")][-1] == "rEnT"


def test_rename_category_keeps_id_position_and_keywords(conn):
    eating_out = category_id(conn, "Eating out")
    remember_keyword(conn, "coffee", eating_out)

    rename_category(conn, eating_out, "Food")

    assert get_category(conn, eating_out) == Category(id=eating_out, name="Food", kind="expense")
    assert [c.name for c in list_categories(conn, "expense")][:3] == [
        "Groceries",
        "Food",
        "Transport",
    ]
    assert category_for_keyword(conn, "coffee", "expense") == Category(
        id=eating_out, name="Food", kind="expense"
    )


ZERO_WIDTH_SPACE = "\u200b"


@pytest.mark.parametrize(
    ("name", "existing"),
    [
        ("Eating out", "Eating out"),
        ("eating OUT", "Eating out"),
        ("Groceries" + ZERO_WIDTH_SPACE, "Groceries"),
        ("Salary", "Salary"),
    ],
)
@pytest.mark.parametrize("kind", ["expense", "income"])
def test_add_category_refuses_a_name_either_kind_has(conn, name, existing, kind):
    with pytest.raises(CategoryError) as error:
        add_category(conn, name, kind)

    assert str(error.value) == f"There is already a category {existing}."
    assert conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 15


def test_add_category_allows_the_30th_and_refuses_the_31st_in_a_kind(conn):
    for number in range(17):
        add_category(conn, f"Extra {number}", "expense")

    add_category(conn, "Thirtieth", "expense")
    with pytest.raises(CategoryError) as error:
        add_category(conn, "Thirty first", "expense")

    assert str(error.value) == (
        "Up to 30 expense categories. Rename one instead: /category rename Old New"
    )
    assert len(list_categories(conn, "expense")) == 30
    add_category(conn, "Bonus", "income")


def test_add_category_limit_message_names_the_income_kind(conn):
    for number in range(27):
        add_category(conn, f"Extra {number}", "income")

    with pytest.raises(CategoryError) as error:
        add_category(conn, "Bonus", "income")

    assert str(error.value) == (
        "Up to 30 income categories. Rename one instead: /category rename Old New"
    )


def test_a_duplicate_is_reported_before_the_limit(conn):
    for number in range(18):
        add_category(conn, f"Extra {number}", "expense")

    with pytest.raises(CategoryError) as error:
        add_category(conn, "groceries", "expense")

    assert str(error.value) == "There is already a category Groceries."


def test_add_category_stores_a_cleaned_name(conn):
    added = add_category(conn, f"  Pet{ZERO_WIDTH_SPACE}   food\u200f ", "expense")

    assert added.name == "Pet food"
    assert list_categories(conn, "expense")[-1] == added


def test_add_category_stores_the_composed_form_and_finds_the_decomposed_one(conn):
    added = add_category(conn, "Cafe\u0301", "expense")

    assert added.name == "Caf\u00e9"
    assert find_category(conn, "Cafe\u0301") == added
    assert find_category(conn, "CAF\u00c9") == added
    with pytest.raises(CategoryError):
        add_category(conn, "Cafe\u0301", "income")


def test_find_category_ignores_invisible_characters(conn):
    groceries = category_id(conn, "Groceries")

    assert find_category(conn, "Gro" + ZERO_WIDTH_SPACE + "ceries") == Category(
        id=groceries, name="Groceries", kind="expense"
    )


@pytest.mark.parametrize("name", ["", ZERO_WIDTH_SPACE, "\u200b\u200f\ufeff", " \u200b "])
def test_a_name_made_only_of_invisible_characters_is_invalid(name):
    assert not is_valid_name(name)


@pytest.mark.parametrize(
    "name",
    [
        "Uncategorized",
        "uncategorized",
        "UNCATEGORIZED",
        "  Uncategorized  ",
        f"Uncategorized{ZERO_WIDTH_SPACE}",
    ],
)
def test_the_reports_label_for_entries_without_a_category_is_not_a_valid_name(name):
    assert not is_valid_name(name)


def test_a_name_that_only_contains_the_reserved_word_is_valid():
    assert is_valid_name("Uncategorized stuff")
    assert is_valid_name("Not uncategorized")


def test_is_valid_name_counts_the_cleaned_name():
    assert is_valid_name("a" * 30 + ZERO_WIDTH_SPACE)
    assert not is_valid_name("a" * 31 + ZERO_WIDTH_SPACE)
    assert not is_valid_name(ZERO_WIDTH_SPACE + "/rent")


def test_rename_category_returns_the_renamed_category_with_a_cleaned_name(conn):
    eating_out = category_id(conn, "Eating out")

    renamed = rename_category(conn, eating_out, f" Food{ZERO_WIDTH_SPACE}  court ")

    assert renamed == Category(id=eating_out, name="Food court", kind="expense")
    assert get_category(conn, eating_out) == renamed


@pytest.mark.parametrize(
    ("name", "existing"),
    [
        ("Groceries", "Groceries"),
        ("groceries", "Groceries"),
        ("Salary", "Salary"),
        ("Groceries" + ZERO_WIDTH_SPACE, "Groceries"),
    ],
)
def test_rename_category_refuses_a_name_another_category_has(conn, name, existing):
    eating_out = category_id(conn, "Eating out")

    with pytest.raises(CategoryError) as error:
        rename_category(conn, eating_out, name)

    assert str(error.value) == f"There is already a category {existing}."
    assert get_category(conn, eating_out).name == "Eating out"


def test_rename_category_may_change_only_the_case_of_its_own_name(conn):
    groceries = category_id(conn, "Groceries")

    renamed = rename_category(conn, groceries, "GROCERIES")

    assert renamed.name == "GROCERIES"
