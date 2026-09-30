"""Частина 6. Команди системи: з'єднують кафе і таксі (уроки 7, 13, 15).

Кожна команда отримує стан (orders, deliveries) і аргументи,
змінює списки на місці, якщо треба, і повертає текст для людини.
Неправильні дані → ValueError з поясненням; друкує лише app.py.
"""
from cafe import cafe_stats
from parsing import parse_delivery, parse_order
from rules import day_name, meal_type
from taxi import delivery_index, top_districts, voucher_pair


def next_id(orders):
    """Номер для нового замовлення: на 1 більший за найбільший, 1 для порожнього списку."""
    raise NotImplementedError("частина 6: напиши next_id()")


def add_order(orders, deliveries, line):
    """Додає замовлення з рядка каси. → "Замовлення №1: пт, вечеря, 540.00 грн"."""
    raise NotImplementedError("частина 6: напиши add_order()")


def import_kasa(orders, deliveries, lines):
    """Додає всі правильні рядки каси. Перший рядок відповіді — "Імпортовано: 4, пропущено: 5",
    далі по рядку на кожен пропущений: "  рядок 3: пояснення"."""
    raise NotImplementedError("частина 6: напиши import_kasa()")


def add_delivery(orders, deliveries, fields):
    """Додає доставку. Замовлення має існувати і ще не мати доставки, інакше ValueError.
    → "Доставка №1: Оболонь, 230 грн, водій D-3"."""
    raise NotImplementedError("частина 6: напиши add_delivery()")


def find_order(orders, deliveries, order_id):
    """Замовлення і його доставка за номером. Немає → ValueError.
    → "№1 2024-07-19 18:30, 540.00 грн, гостей: 2, доставка: Оболонь (230 грн)"
    або "..., доставка: немає"."""
    raise NotImplementedError("частина 6: напиши find_order()")


def report(orders, deliveries):
    """Спільний звіт кафе й таксі, 5 рядків:

    Замовлень: 4, з доставкою: 3
    Кафе: 3040.00 грн, середній чек 760.00 грн, найкращий день: нд
    Таксі: 700 грн за доставки
    Райони: Оболонь 2, Поділ 1
    Разом: 3740.00 грн
    """
    raise NotImplementedError("частина 6: напиши report()")


def voucher(orders, deliveries, amount):
    """Дві доставки на суму ваучера. → "Ваучер 500 грн: доставки замовлень №1 і №3"
    або "Ваучер 500 грн: такої пари немає"."""
    raise NotImplementedError("частина 6: напиши voucher()")
