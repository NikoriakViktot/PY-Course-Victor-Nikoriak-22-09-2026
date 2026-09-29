"""Задача 2. Розбір одного рядка каси."""
from datetime import datetime

from models import RawOrder


def parse_line(line):
    """Рядок "2024-07-19 18:30;540.00;50;2" → RawOrder.

    Поля через ";": час "%Y-%m-%d %H:%M", сума, чайові, кількість гостей.
    Зіпсований рядок → ValueError з поясненням людською мовою:
    не 4 поля, не число, неіснуюча дата, сума <= 0, чайові < 0, гостей < 1.
    """
    raise NotImplementedError("задача 2: напиши parse_line()")
