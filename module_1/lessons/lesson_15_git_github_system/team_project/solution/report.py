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
    revenue = sum(order.total_bill for order in orders)
    by_day = revenue_by_day(orders)
    by_meal = count_by_meal(orders)
    first = min(order.timestamp for order in orders).isoformat() if orders else None
    return {
        "orders": len(orders),
        "skipped": len(errors),
        "revenue": round(revenue, 2),
        "average": round(revenue / len(orders), 2) if orders else 0.0,
        "best_day": best_day(by_day),
        "by_day": {day: round(by_day[day], 2) for day in DAYS if day in by_day},
        "by_meal": dict(Counter(by_meal).most_common()),
        "first_order": first,
    }
