"""Частина 5 — taxi.py."""
from models import Delivery
from taxi import delivery_index, top_districts, voucher_pair

DELIVERIES = [Delivery(1, "Оболонь", 230, "D-3"), Delivery(2, "Поділ", 180, "D-1"),
              Delivery(3, "Оболонь", 270, "D-3"), Delivery(5, "Печерськ", 320, "D-2")]


def test_delivery_index():
    index = delivery_index(DELIVERIES)
    assert index[3] == DELIVERIES[2] and 4 not in index and len(index) == 4


def test_top_districts():
    assert top_districts(DELIVERIES, 2) == [("Оболонь", 2), ("Поділ", 1)], top_districts(DELIVERIES, 2)
    assert top_districts([]) == []


def test_voucher_pair():
    assert voucher_pair(DELIVERIES, 500) == (1, 3), voucher_pair(DELIVERIES, 500)
    assert voucher_pair(DELIVERIES, 500 + 1) is None
    assert voucher_pair([], 500) is None
