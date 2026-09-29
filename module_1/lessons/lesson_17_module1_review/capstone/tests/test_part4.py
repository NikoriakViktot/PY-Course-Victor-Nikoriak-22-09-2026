"""Частина 4 — cafe.py (спирається на частину 1)."""
from datetime import datetime

from cafe import cafe_stats
from models import Order

ORDERS = [
    Order(1, datetime(2024, 7, 19, 18, 30), 540.0, 50.0, 2),
    Order(2, datetime(2024, 7, 19, 12, 10), 320.0, 30.0, 1),
    Order(3, datetime(2024, 7, 20, 20, 15), 980.0, 120.0, 4),
]


def test_cafe_stats():
    assert cafe_stats(ORDERS) == {"orders": 3, "revenue": 1840.0, "average": 613.33, "best_day": "сб",
                                  "by_meal": {"вечеря": 2, "обід": 1}}, cafe_stats(ORDERS)


def test_empty():
    assert cafe_stats([]) == {"orders": 0, "revenue": 0, "average": 0.0, "best_day": None, "by_meal": {}}, cafe_stats([])
