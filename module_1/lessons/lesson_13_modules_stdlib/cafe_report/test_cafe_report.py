"""Перевірки cafe_report: python test_cafe_report.py (або pytest)."""
import contextlib
import importlib
import io
from datetime import datetime

import main
import report
from orders import Order, RawOrder, generate_raw_orders, in_month, to_order
from report import best_day, count_by_day, revenue_by_day
from rules import MONTHS, day_from_timestamp, meal_type_from_hour


def test_meal_type_borders():
    assert meal_type_from_hour(10) == "інше"
    assert meal_type_from_hour(11) == "обід"
    assert meal_type_from_hour(15) == "обід"
    assert meal_type_from_hour(16) == "інше"
    assert meal_type_from_hour(17) == "вечеря"
    assert meal_type_from_hour(23) == "вечеря"


def test_day_and_month_names():
    assert day_from_timestamp(datetime(2024, 7, 19, 18, 30)) == "пт"
    assert day_from_timestamp(datetime(2024, 7, 21)) == "нд"
    assert MONTHS[0] == "" and MONTHS[7] == "липень" and len(MONTHS) == 13


def test_to_order():
    raw = RawOrder(540.0, 50.0, 2, datetime(2024, 7, 19, 18, 30))
    assert to_order(raw) == Order(540.0, 50.0, "пт", "вечеря", 2)
    assert in_month(raw, 2024, 7) and not in_month(raw, 2023, 7)


def test_generate_is_reproducible():
    first = generate_raw_orders(300, seed=42)
    assert first == generate_raw_orders(300, seed=42)
    assert first != generate_raw_orders(300, seed=7)
    assert all(9 <= raw.timestamp.hour <= 22 for raw in first)
    assert {raw.timestamp.year for raw in first} == {2023, 2024}
    assert all(150 <= raw.total_bill <= 1500 and 1 <= raw.size <= 6 for raw in first)


def test_report_functions():
    orders = [Order(540.0, 50.0, "пт", "вечеря", 2), Order(320.0, 30.0, "пт", "обід", 1),
              Order(980.0, 120.0, "сб", "вечеря", 4)]
    assert count_by_day(orders) == {"пт": 2, "сб": 1}
    assert revenue_by_day(orders) == {"пт": 860.0, "сб": 980.0}
    assert best_day(revenue_by_day(orders)) == "сб"
    assert best_day({}) is None


def test_import_prints_nothing():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        importlib.reload(report)
        importlib.reload(main)
    assert out.getvalue() == ""


def test_main_usage_and_report():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        main.main(["main.py"])
    assert out.getvalue().startswith("Використання:")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        main.main(["main.py", "2024", "7"])
    lines = out.getvalue().splitlines()
    assert lines[0] == "Звіт кафе: липень 2024, днів: 31, чеків: 86"
    assert lines[-2] == "Найкращий день: пн"


if __name__ == "__main__":
    for name, func in list(globals().items()):
        if name.startswith("test_"):
            func()
            print("OK", name)
