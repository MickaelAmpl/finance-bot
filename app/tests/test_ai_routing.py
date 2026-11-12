from datetime import date

import pytest

from finbot.ai_routing import route

TODAY = date(2026, 11, 1)


@pytest.mark.parametrize(
    "text",
    [
        "25 coffee",
        "+3000 salary",
        "save 200 emergency",
        "SAVE 200 emergency",
        "€25 coffee",
        "850.00 rent, 120 utilities",
        "25 coffee yesterday",
        "12,50 lunch",
        "25 майка",
        "25 кофе",
        "30 internet",
        "120 utilities",
        "25 рубашка",
        "40 средство для посуды",
        "15 серединка",
        "25 четверка",
        "15 euroshop",
        "8 buckwheat",
        "9 dollarama",
        "30 poundland",
        "60 franchise",
    ],
)
def test_parser_examples(text):
    assert route(text, TODAY) == "parser"


@pytest.mark.parametrize(
    "text",
    [
        "20 фунтов обед",
        "100 злотых обед",
        "25 такси в долларах",
        "300 гривнах такси",
        "50 баксах такси",
        "25 кофе в долларах",
        "40 продукты в пятницу",
        "25 taxi on friday",
        "25 обед в понедельник",
        "25 taxi в субботу",
        "25 coffee tomorrow",
        "25 кофе два дня назад",
        "25 обед в п'ятницю",
        "20 pounds lunch",
        "25 taxi 10 dollars",
        "25 обед в среду",
        "25 обед у середу",
        "25 обед в четверг",
        "25 обід у четвер",
        "100 руб такси",
        "15 euro coffee",
    ],
)
def test_currency_weekday_and_relative_day_examples(text):
    assert route(text, TODAY) == "ai"


def test_exact_warning_word_routes_to_ai():
    assert route("25 coffee last week", TODAY) == "ai"


def test_currency_stem_routes_to_ai():
    assert route("25 кофе в гривнах", TODAY) == "ai"


def test_weekday_stem_routes_to_ai():
    assert route("25 обед во вторник", TODAY) == "ai"


@pytest.mark.parametrize(
    "text",
    [
        "вчера 25 на кофе с другом",
        "кофе 25",
        "300 грн такси",
        "50 баксов такси",
        "25 на кофе вчера",
        "2025 total?",
        "1 сентября сколько потратил",
        "25 coffee 3 people",
        "25 coffee in march",
        "1000 рублей",
        "1200 taxi uah",
        "25",
        "25 coffee?",
        "25 coffee, 30 такси грн",
        "",
        "   ",
    ],
)
def test_ai_examples(text):
    assert route(text, TODAY) == "ai"
