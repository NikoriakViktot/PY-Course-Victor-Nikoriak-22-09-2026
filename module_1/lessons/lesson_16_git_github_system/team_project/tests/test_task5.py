"""Задача 5 — report.py. Залежить від задачі 4: її функції тут замінено заглушками."""
import json
from datetime import datetime

import report
from models import RawOrder
from report import build_report
from tests.helpers import replaced

ORDERS = [
    RawOrder(1200.0, 150.0, 6, datetime(2024, 7, 21, 21, 30)),
    RawOrder(320.0, 30.0, 1, datetime(2024, 7, 19, 12, 10)),
    RawOrder(540.0, 50.0, 2, datetime(2024, 7, 19, 18, 30)),
]


def fake_revenue_by_day(orders):
    return {"нд": 1200.0, "пт": 860.0} if orders else {}     # навмисно не в порядку тижня


def fake_count_by_meal(orders):
    return {"обід": 1, "вечеря": 2} if orders else {}        # навмисно від меншого до більшого


def fake_best_day(revenue):
    return "нд" if revenue else None


FAKES = dict(revenue_by_day=fake_revenue_by_day, count_by_meal=fake_count_by_meal, best_day=fake_best_day)


def test_report_keys_and_values():
    with replaced(report, **FAKES):
        result = build_report(ORDERS, ["рядок 3: …", "рядок 5: …"])
    assert result == {
        "orders": 3,
        "skipped": 2,
        "revenue": 2060.0,
        "average": 686.67,
        "best_day": "нд",
        "by_day": {"пт": 860.0, "нд": 1200.0},
        "by_meal": {"вечеря": 2, "обід": 1},
        "first_order": "2024-07-19T12:10:00",
    }, result
    assert list(result["by_day"]) == ["пт", "нд"], "by_day — у порядку DAYS"
    assert list(result["by_meal"]) == ["вечеря", "обід"], "by_meal — від більшого до меншого"
    json.dumps(result)                                       # лише типи, які розуміє JSON


def test_empty_report():
    with replaced(report, **FAKES):
        result = build_report([], [])
    assert result == {"orders": 0, "skipped": 0, "revenue": 0, "average": 0.0, "best_day": None,
                      "by_day": {}, "by_meal": {}, "first_order": None}, result
