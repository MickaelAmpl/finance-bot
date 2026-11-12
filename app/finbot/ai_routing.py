import re
from datetime import date
from typing import Literal

from finbot.money import SYMBOLS
from finbot.parser import ParseError, parse_entries

AMOUNT_LED_RE = re.compile(rf"\+?[{re.escape(''.join(SYMBOLS))}]?\d")
DIGIT_OR_QUESTION_RE = re.compile(r"[\d?]")
WORD_RE = re.compile(r"\w+")
_APOSTROPHES = str.maketrans("", "", "'’ʼ")
_WARNING_TEXT = """вчера позавчера сегодня завтра вчора позавчора сьогодні today yesterday tomorrow
    назад тому ago last мая май мае january february march april may june july august
    september october november december monday tuesday wednesday thursday friday saturday
    sunday руб pound pounds buck bucks dollar dollars euro euros franc francs франк франка
    франков франки среда среду среды среде середа середу середи четвер"""
WARNING_WORDS = frozenset(_WARNING_TEXT.split())
CURRENCY_STEMS = (
    "грн",
    "гривн",
    "гривен",
    "гривень",
    "бакс",
    "доллар",
    "долар",
    "евро",
    "євро",
    "рубл",
    "фунт",
    "злот",
    "hryvn",
    "zlot",
)
WEEKDAY_STEMS = (
    "понедельник",
    "вторник",
    "четверг",
    "пятниц",
    "суббот",
    "воскресен",
    "понеділ",
    "вівтор",
    "субот",
    "неділ",
)
MONTH_STEMS = (
    "январ",
    "феврал",
    "март",
    "апрел",
    "июн",
    "июл",
    "август",
    "сентябр",
    "октябр",
    "ноябр",
    "декабр",
    "січн",
    "лют",
    "березн",
    "квітн",
    "травн",
    "червн",
    "липн",
    "серпн",
    "вересн",
    "жовтн",
    "листопад",
    "грудн",
)


def route(text: str, today: date) -> Literal["parser", "ai"]:
    tokens = text.split()
    if not tokens:
        return "ai"
    if tokens[0].lower() not in ("save", "take") and AMOUNT_LED_RE.match(tokens[0]) is None:
        return "ai"
    try:
        entries = parse_entries(text, today)
    except ParseError:
        return "ai"
    for entry in entries:
        if DIGIT_OR_QUESTION_RE.search(entry.note):
            return "ai"
        note = entry.note.lower().translate(_APOSTROPHES)
        if any(_is_warning(word) for word in WORD_RE.findall(note)):
            return "ai"
    return "parser"


def _is_warning(word: str) -> bool:
    return word in WARNING_WORDS or word.startswith(MONTH_STEMS + CURRENCY_STEMS + WEEKDAY_STEMS)
