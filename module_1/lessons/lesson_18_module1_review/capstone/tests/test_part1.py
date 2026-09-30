"""Частина 1 — rules.py."""
from datetime import datetime

from rules import day_name, meal_type


def test_meal_type_borders():
    assert [meal_type(h) for h in (10, 11, 15, 16, 17, 23)] == ["інше", "обід", "обід", "інше", "вечеря", "вечеря"]


def test_day_name():
    assert day_name(datetime(2024, 7, 15)) == "пн"
    assert day_name(datetime(2024, 7, 19, 18, 30)) == "пт"
    assert day_name(datetime(2024, 7, 21)) == "нд"
