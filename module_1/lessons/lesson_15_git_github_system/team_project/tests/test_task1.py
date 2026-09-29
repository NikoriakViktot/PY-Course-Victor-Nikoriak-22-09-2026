"""Задача 1 — rules.py. Ні від кого не залежить."""
from datetime import datetime

from models import DAYS
from rules import day_name, meal_type


def test_meal_type_borders():
    assert meal_type(10) == "інше", "10:00 — ще не обід"
    assert meal_type(11) == "обід", "обід починається об 11"
    assert meal_type(15) == "обід", "15 — ще обід"
    assert meal_type(16) == "інше", "16 — між обідом і вечерею"
    assert meal_type(17) == "вечеря", "вечеря починається о 17"
    assert meal_type(23) == "вечеря", "23 — ще вечеря"


def test_day_name():
    assert day_name(datetime(2024, 7, 15, 9, 0)) == "пн"
    assert day_name(datetime(2024, 7, 19, 18, 30)) == "пт"
    assert day_name(datetime(2024, 7, 21, 21, 30)) == "нд"
    assert all(day_name(datetime(2024, 7, day)) in DAYS for day in range(1, 32))
