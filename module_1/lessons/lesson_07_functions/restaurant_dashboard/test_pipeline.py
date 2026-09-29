"""Перевірки pipeline.py на маленькому наборі чеків: python test_pipeline.py (або pytest).

Інтернет і seaborn не потрібні — чеки задані вручну.
"""
from pipeline import (
    Order, apply_filters, calc_kpis, enrich_all, enrich_order, group_by_day,
    group_by_size, group_by_time, run_pipeline, top_by_tip_pct,
)

ORDERS = [
    Order(20.0, 4.0, "Female", "No", "Sat", "Dinner", 2),
    Order(10.0, 1.0, "Male", "Yes", "Sat", "Dinner", 1),
    Order(30.0, 3.0, "Male", "No", "Sun", "Dinner", 4),
    Order(15.0, 3.0, "Female", "No", "Thur", "Lunch", 2),
]
ALL = dict(days=["Thur", "Fri", "Sat", "Sun"], times=["Lunch", "Dinner"], smoker=["No", "Yes"],
           size_range=(1, 6), bill_range=(0, 55), sexes=["Male", "Female"])


def test_filters():
    assert apply_filters(ORDERS, **ALL) == ORDERS
    only_sat = apply_filters(ORDERS, **{**ALL, "days": ["Sat"]})
    assert [o.total_bill for o in only_sat] == [20.0, 10.0]
    assert apply_filters(ORDERS, **{**ALL, "days": []}) == []
    assert len(apply_filters(ORDERS, **{**ALL, "size_range": (2, 2)})) == 2


def test_filters_do_not_change_input():
    before = list(ORDERS)
    apply_filters(ORDERS, **{**ALL, "smoker": ["Yes"]})
    assert ORDERS == before


def test_enrich():
    rich = enrich_order(ORDERS[0])
    assert rich.tip_pct == 20.0
    assert rich.bill_per_person == 10.0
    assert rich.day_ua == "Субота" and rich.time_ua == "Вечеря"
    assert len(enrich_all(ORDERS)) == len(ORDERS)


def test_reducers():
    rich = enrich_all(ORDERS)
    kpis = calc_kpis(rich)
    assert kpis["revenue"] == 75.0 and kpis["tips"] == 11.0 and kpis["count"] == 4
    assert kpis["avg_bill"] == 18.75
    assert calc_kpis([])["count"] == 0
    by_day = group_by_day(rich)
    assert [row["day"] for row in by_day] == ["Sat", "Sun", "Thur"]
    assert by_day[0]["orders"] == 2 and by_day[0]["revenue"] == 30.0
    assert [row["time"] for row in group_by_time(rich)] == ["Lunch", "Dinner"]
    assert [row["size"] for row in group_by_size(rich)] == [1, 2, 4]
    assert top_by_tip_pct(rich, 1)[0].tip_pct == 20.0


def test_pipeline_empty_and_full():
    empty = run_pipeline(ORDERS, **{**ALL, "sexes": []})
    assert empty["count"] == 0 and empty["by_day"] == [] and empty["top_tips"] == []
    full = run_pipeline(ORDERS, **ALL)
    assert full["count"] == 4 and full["kpis"]["revenue"] == 75.0


if __name__ == "__main__":
    for name, func in list(globals().items()):
        if name.startswith("test_"):
            func()
            print("OK", name)
