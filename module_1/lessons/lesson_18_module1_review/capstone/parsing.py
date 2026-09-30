"""Частина 2. Розбір і перевірка вхідних даних (урок 13)."""
from datetime import datetime

from models import Delivery, Order


def parse_order(line, order_id):
    """Рядок каси "2024-07-19 18:30;540.00;50;2" → Order з номером order_id.

    Зіпсований рядок → ValueError з поясненням: не 4 поля, не число,
    неіснуюча дата, сума <= 0, чайові < 0, гостей < 1.
    """
    raise NotImplementedError("частина 2: напиши parse_order()")


def parse_delivery(fields):
    """["1", "Оболонь", "230", "D-3"] → Delivery(1, "Оболонь", 230, "D-3").

    Не 4 поля, номер чи вартість не цілі числа, вартість <= 0,
    порожній район чи водій → ValueError з поясненням.
    """
    raise NotImplementedError("частина 2: напиши parse_delivery()")
