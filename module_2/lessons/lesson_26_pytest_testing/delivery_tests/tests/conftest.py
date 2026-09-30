"""Спільні fixtures: pytest знаходить цей файл сам, імпортувати його не треба."""

import pytest

from delivery.pricing import Tariff


@pytest.fixture
def day_tariff():
    return Tariff(base=40, per_km=12, min_fare=80)


@pytest.fixture
def log_lines():
    return [
        "17:58 D-1 97 delivered",
        "18:03 D-1 101 picked",
        "18:05 D-2 102 picked",
        "18:21 D-1 101 delivered",
        "18:24 ?? зламаний рядок",
        "18:29 D-2 102 delivered",
    ]


@pytest.fixture
def make_event():
    """Фабрика: створює подію, у якій треба вказати лише важливі для тесту поля."""
    def factory(order=1, kind="picked", time="18:00", courier="D-1"):
        return f"{time} {courier} {order} {kind}"
    return factory
