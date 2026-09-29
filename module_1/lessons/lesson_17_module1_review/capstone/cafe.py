"""Частина 4. Аналітика кафе (уроки 6, 7, 12)."""
from collections import Counter

from models import DAYS
from rules import day_name, meal_type


def cafe_stats(orders):
    """Статистика кафе — словник з ключами:

    "orders"   — кількість замовлень
    "revenue"  — сума чеків, round(..., 2)
    "average"  — середній чек, round(..., 2); 0.0 без замовлень
    "best_day" — день тижня з найбільшим виторгом або None
    "by_meal"  — {прийом їжі: кількість}, від більшого до меншого
    """
    raise NotImplementedError("частина 4: напиши cafe_stats()")
