import pytest

from dispatch import Order
from dispatch.__main__ import main
from dispatch.pricing import estimate_price


def test_order_str_with_and_without_deadline():
    assert str(Order(7, "Хорива, 5")) == "#7 Хорива, 5"
    assert str(Order(8, "Хрещатик, 1", "09:25")) == "#8 Хрещатик, 1 до 09:25"


def test_order_is_immutable_value():
    order = Order(7, "Хорива, 5")
    assert order == Order(7, "Хорива, 5")
    with pytest.raises(AttributeError):
        order.address = "інша"


@pytest.mark.parametrize("origin, destination, price", [
    ("Поділ", "Поділ", 60),
    ("Поділ", "Центр", 105),
    ("Центр", "Поділ", 105),       # відстань не залежить від напрямку
    ("Поділ", "Оболонь", 165),
])
def test_estimate_price(origin, destination, price):
    assert estimate_price(origin, destination) == price


def test_unknown_route_raises():
    with pytest.raises(KeyError):
        estimate_price("Поділ", "Бровари")


def test_demo_runs(capsys):
    main()
    out = capsys.readouterr().out
    assert "Оксана ← #104 Олегівська, 3 до 09:25" in out
    assert "{'hits': 1, 'misses': 2, 'size': 2}" in out
