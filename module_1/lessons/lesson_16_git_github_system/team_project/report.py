"""Задача 5. Звіт — словник лише з типів, які розуміє JSON."""
from collections import Counter

from models import DAYS
from stats import best_day, count_by_meal, revenue_by_day


def build_report(orders, errors):
    """Звіт за чеками й помилками. Ключі — рівно ці:

    "orders"      — кількість чеків (int)
    "skipped"     — кількість помилок (int)
    "revenue"     — сума чеків, round(..., 2)
    "average"     — середній чек, round(..., 2); 0.0, якщо чеків немає
    "best_day"    — день з найбільшим виторгом або None
    "by_day"      — {день: виторг, round(..., 2)} у порядку DAYS, лише дні з чеками
    "by_meal"     — {прийом їжі: кількість}, від більшого до меншого
    "first_order" — час першого чека, datetime.isoformat(), або None
    """
    raise NotImplementedError("задача 5: напиши build_report()")
