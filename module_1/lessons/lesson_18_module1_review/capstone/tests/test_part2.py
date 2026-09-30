"""Частина 2 — parsing.py."""
from datetime import datetime

from models import Delivery, Order
from parsing import parse_delivery, parse_order


def value_error(func, *args):
    try:
        func(*args)
    except ValueError as error:
        return str(error) != ""
    return False


def test_parse_order():
    assert parse_order("2024-07-19 18:30;540.00;50;2", 7) == Order(7, datetime(2024, 7, 19, 18, 30), 540.0, 50.0, 2)
    for line in ["2024-07-19 19:05;540,00;40;3", "2024-07-20 13:40;760.00", "2024-02-30 19:00;450.00;0;5",
                 "2024-07-21 18:00;-120.00;0;2", "2024-07-21 18:00;120.00;-5;2", "2024-07-21 14:20;610.00;60;0"]:
        assert value_error(parse_order, line, 1), f"очікували ValueError для {line!r}"


def test_parse_delivery():
    assert parse_delivery(["1", "Оболонь", "230", "D-3"]) == Delivery(1, "Оболонь", 230, "D-3")
    for fields in [["1", "Оболонь", "230"], ["один", "Оболонь", "230", "D-3"], ["1", "Оболонь", "сто", "D-3"],
                   ["1", "Оболонь", "0", "D-3"], ["1", "", "230", "D-3"], ["1", "Оболонь", "230", " "]]:
        assert value_error(parse_delivery, fields), f"очікували ValueError для {fields}"
