"""Задача 2 — parsing.py. Залежить лише від models.py."""
from datetime import datetime

from models import RawOrder
from parsing import parse_line
from tests.helpers import raises_value_error


def test_good_line():
    order = parse_line("2024-07-19 18:30;540.00;50;2")
    assert order == RawOrder(540.0, 50.0, 2, datetime(2024, 7, 19, 18, 30)), order
    assert isinstance(order.total_bill, float) and isinstance(order.size, int)


def test_python_errors_become_value_error():
    assert raises_value_error(parse_line, "2024-07-19 19:05;540,00;40;3"), "кома замість крапки"
    assert raises_value_error(parse_line, "2024-07-20 13:40;760.00"), "лише 2 поля"
    assert raises_value_error(parse_line, "2024-02-30 19:00;450.00;0;5"), "30 лютого"
    assert raises_value_error(parse_line, "19.07.2024 18:30;540.00;50;2"), "не той формат дати"


def test_cafe_rules():
    assert raises_value_error(parse_line, "2024-07-21 18:00;-120.00;0;2"), "від'ємна сума"
    assert raises_value_error(parse_line, "2024-07-21 18:00;0;0;2"), "сума 0"
    assert raises_value_error(parse_line, "2024-07-21 18:00;120.00;-5;2"), "від'ємні чайові"
    assert raises_value_error(parse_line, "2024-07-21 14:20;610.00;60;0"), "0 гостей"
