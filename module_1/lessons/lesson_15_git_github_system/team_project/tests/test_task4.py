"""Задача 4 — stats.py. Залежить від задачі 1: day_name і meal_type тут замінено заглушками."""
from datetime import datetime

import stats
from models import RawOrder
from stats import best_day, count_by_meal, revenue_by_day
from tests.helpers import replaced

ORDERS = [
    RawOrder(540.0, 50.0, 2, datetime(2024, 7, 19, 18, 30)),
    RawOrder(320.0, 30.0, 1, datetime(2024, 7, 19, 12, 10)),
    RawOrder(980.0, 120.0, 4, datetime(2024, 7, 20, 20, 15)),
]


def fake_day_name(timestamp):
    """Заглушка задачі 1: знає лише 19 і 20 липня."""
    return {19: "пт", 20: "сб"}[timestamp.day]


def fake_meal_type(hour):
    """Заглушка задачі 1: знає лише години тестових чеків."""
    return {12: "обід", 18: "вечеря", 20: "вечеря"}[hour]


def test_revenue_by_day():
    with replaced(stats, day_name=fake_day_name):
        assert revenue_by_day(ORDERS) == {"пт": 860.0, "сб": 980.0}, revenue_by_day(ORDERS)
        assert revenue_by_day([]) == {}


def test_best_day():
    assert best_day({"пт": 860.0, "сб": 980.0, "нд": 100.0}) == "сб"
    assert best_day({}) is None


def test_count_by_meal():
    with replaced(stats, meal_type=fake_meal_type):
        assert count_by_meal(ORDERS) == {"вечеря": 2, "обід": 1}, count_by_meal(ORDERS)
        assert count_by_meal([]) == {}
