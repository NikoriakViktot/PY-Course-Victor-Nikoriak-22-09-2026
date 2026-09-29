"""Задача 4. Підрахунки за днями і прийомами їжі."""
from rules import day_name, meal_type


def revenue_by_day(orders):
    """Виторг за днями тижня: {"пт": 860.0, ...}. Лише дні, у які були чеки."""
    revenue = {}
    for order in orders:
        day = day_name(order.timestamp)
        revenue[day] = revenue.get(day, 0) + order.total_bill
    return revenue


def best_day(revenue):
    """День з найбільшим виторгом; для порожнього словника — None."""
    best = None
    for day, amount in revenue.items():
        if best is None or amount > revenue[best]:
            best = day
    return best


def count_by_meal(orders):
    """Кількість чеків за прийомом їжі: {"вечеря": 3, "обід": 1}."""
    counts = {}
    for order in orders:
        meal = meal_type(order.timestamp.hour)
        counts[meal] = counts.get(meal, 0) + 1
    return counts
