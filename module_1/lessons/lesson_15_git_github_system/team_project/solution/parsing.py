"""Задача 2. Розбір одного рядка каси."""
from datetime import datetime

from models import RawOrder


def parse_line(line):
    """Рядок "2024-07-19 18:30;540.00;50;2" → RawOrder.

    Поля через ";": час "%Y-%m-%d %H:%M", сума, чайові, кількість гостей.
    Зіпсований рядок → ValueError з поясненням людською мовою:
    не 4 поля, не число, неіснуюча дата, сума <= 0, чайові < 0, гостей < 1.
    """
    fields = line.split(";")
    if len(fields) != 4:
        raise ValueError(f"очікували 4 поля, а маємо {len(fields)}")
    time_text, bill_text, tip_text, size_text = fields
    timestamp = datetime.strptime(time_text, "%Y-%m-%d %H:%M")
    bill, tip, size = float(bill_text), float(tip_text), int(size_text)
    if bill <= 0:
        raise ValueError(f"сума чека має бути більшою за 0, а маємо {bill}")
    if tip < 0:
        raise ValueError(f"чайові не можуть бути від'ємними: {tip}")
    if size < 1:
        raise ValueError(f"гостей має бути хоча б один, а маємо {size}")
    return RawOrder(bill, tip, size, timestamp)
