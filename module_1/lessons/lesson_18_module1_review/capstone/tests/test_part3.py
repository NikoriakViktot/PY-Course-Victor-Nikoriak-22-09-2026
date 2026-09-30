"""Частина 3 — storage.py."""
import json
import os
import tempfile
from datetime import datetime

from models import Delivery, Order
from storage import load_state, save_state

ORDERS = [Order(1, datetime(2024, 7, 19, 18, 30), 540.0, 50.0, 2), Order(2, datetime(2024, 7, 20, 20, 15), 980.0, 120.0, 4)]
DELIVERIES = [Delivery(1, "Оболонь", 230, "D-3")]


def test_round_trip():
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "data.json")
        save_state(path, ORDERS, DELIVERIES)
        with open(path, encoding="utf-8") as file:
            text = file.read()
        assert load_state(path) == (ORDERS, DELIVERIES)
    data = json.loads(text)
    assert data["orders"][0]["time"] == "2024-07-19T18:30:00", "час — рядок isoformat()"
    assert "Оболонь" in text, "кирилиця як є: ensure_ascii=False"


def test_missing_and_broken_file():
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "data.json")
        assert load_state(path) == ([], []), "першого запуску файлу ще немає"
        with open(path, "w", encoding="utf-8") as file:
            file.write("{'orders': []}")
        try:
            load_state(path)
        except ValueError as error:
            assert "пошкоджено" in str(error), error
        else:
            raise AssertionError("для зіпсованого JSON очікували ValueError")
