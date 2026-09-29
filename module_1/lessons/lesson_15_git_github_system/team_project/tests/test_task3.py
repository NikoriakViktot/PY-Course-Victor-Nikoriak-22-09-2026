"""Задача 3 — loading.py. Залежить від задачі 2: parse_line тут замінено заглушкою."""
import os
import tempfile
from datetime import datetime

import loading
from loading import load_orders, read_lines
from models import RawOrder
from tests.helpers import replaced

GOOD_A = RawOrder(100.0, 10.0, 1, datetime(2024, 7, 1, 12, 0))
GOOD_B = RawOrder(200.0, 20.0, 2, datetime(2024, 7, 2, 19, 0))


def fake_parse_line(line):
    """Заглушка задачі 2: знає лише три тестові рядки."""
    if line == "a":
        return GOOD_A
    if line == "b":
        return GOOD_B
    raise ValueError("зіпсований рядок")


def test_read_lines():
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "kasa.txt")
        with open(path, "w", encoding="utf-8") as file:
            file.write("перший\n\n  другий  \n\n")
        assert read_lines(path) == ["перший", "другий"], read_lines(path)


def test_read_lines_missing_file():
    try:
        read_lines("no_such_kasa_file.txt")
    except FileNotFoundError:
        return
    raise AssertionError("для відсутнього файлу очікували FileNotFoundError")


def test_load_orders():
    with replaced(loading, parse_line=fake_parse_line):
        orders, errors = load_orders(["a", "погано", "b"])
        assert orders == [GOOD_A, GOOD_B], orders
        assert errors == ["рядок 2: зіпсований рядок"], errors
        assert load_orders([]) == ([], [])
