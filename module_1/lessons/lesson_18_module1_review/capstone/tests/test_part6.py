"""Частина 6 — commands.py (спирається на частини 1, 2, 4, 5)."""
from datetime import datetime

import commands
from models import Delivery, Order


def fresh():
    orders = [Order(1, datetime(2024, 7, 19, 18, 30), 540.0, 50.0, 2),
              Order(2, datetime(2024, 7, 21, 21, 30), 1200.0, 150.0, 6)]
    return orders, [Delivery(1, "Оболонь", 230, "D-3")]


def raises(func, *args):
    try:
        func(*args)
    except ValueError as error:
        return str(error)
    raise AssertionError(f"очікували ValueError для {func.__name__}{args[2:]}")


def test_next_id_and_add_order():
    orders, deliveries = fresh()
    assert commands.next_id([]) == 1 and commands.next_id(orders) == 3
    text = commands.add_order(orders, deliveries, "2024-07-22 12:40;310.00;20;1")
    assert text == "Замовлення №3: пн, обід, 310.00 грн", text
    assert orders[-1].id == 3


def test_import_kasa():
    orders, deliveries = [], []
    text = commands.import_kasa(orders, deliveries, ["2024-07-19 18:30;540.00;50;2", "зіпсовано", "2024-07-20 20:15;980.00;120;4"])
    lines = text.splitlines()
    assert lines[0] == "Імпортовано: 2, пропущено: 1", text
    assert lines[1].startswith("  рядок 2: ") and [order.id for order in orders] == [1, 2]


def test_add_delivery():
    orders, deliveries = fresh()
    assert commands.add_delivery(orders, deliveries, ["2", "Поділ", "180", "D-1"]) == "Доставка №2: Поділ, 180 грн, водій D-1"
    assert "немає" in raises(commands.add_delivery, orders, deliveries, ["9", "Поділ", "100", "D-1"])
    assert "вже має доставку" in raises(commands.add_delivery, orders, deliveries, ["1", "Поділ", "100", "D-1"])
    assert len(deliveries) == 2


def test_find_order():
    orders, deliveries = fresh()
    assert commands.find_order(orders, deliveries, 1) == "№1 2024-07-19 18:30, 540.00 грн, гостей: 2, доставка: Оболонь (230 грн)"
    assert commands.find_order(orders, deliveries, 2).endswith("доставка: немає")
    raises(commands.find_order, orders, deliveries, 7)


def test_report_and_voucher():
    orders, deliveries = fresh()
    assert commands.report(orders, deliveries) == (
        "Замовлень: 2, з доставкою: 1\n"
        "Кафе: 1740.00 грн, середній чек 870.00 грн, найкращий день: нд\n"
        "Таксі: 230 грн за доставки\n"
        "Райони: Оболонь 1\n"
        "Разом: 1970.00 грн"), commands.report(orders, deliveries)
    assert commands.report([], []).splitlines()[3] == "Райони: —"
    assert commands.voucher(orders, deliveries, 500) == "Ваучер 500 грн: такої пари немає"
