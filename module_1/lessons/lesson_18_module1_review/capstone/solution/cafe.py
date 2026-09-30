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
    revenue_by_day = {}
    for order in orders:
        day = day_name(order.time)
        revenue_by_day[day] = revenue_by_day.get(day, 0) + order.bill
    revenue = sum(order.bill for order in orders)
    best_day = None
    for day in DAYS:
        if day in revenue_by_day and (best_day is None or revenue_by_day[day] > revenue_by_day[best_day]):
            best_day = day
    return {
        "orders": len(orders),
        "revenue": round(revenue, 2),
        "average": round(revenue / len(orders), 2) if orders else 0.0,
        "best_day": best_day,
        "by_meal": dict(Counter(meal_type(order.time.hour) for order in orders).most_common()),
    }
