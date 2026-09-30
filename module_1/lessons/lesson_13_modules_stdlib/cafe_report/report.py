"""Звіт кафе: функції з уроку 7, тепер в окремому модулі."""
from collections import Counter

from rules import DAYS


def count_by_day(orders):
    """Кількість чеків у кожен день."""
    return Counter(order.day for order in orders)


def revenue_by_day(orders):
    """Сума чеків за кожен день."""
    revenue = {}
    for order in orders:
        revenue[order.day] = revenue.get(order.day, 0) + order.total_bill
    return revenue


def best_day(revenue):
    """День з найбільшим виторгом."""
    best = None
    for day, amount in revenue.items():
        if best is None or amount > revenue[best]:
            best = day
    return best


def print_report(orders):
    """Друкує звіт кафе за списком чеків."""
    counts = count_by_day(orders)
    revenue = revenue_by_day(orders)
    for day in DAYS:
        if day in revenue:
            average = revenue[day] / counts[day]
            print(f"{day} — чеків: {counts[day]:>2}, виторг: {revenue[day]:>9.2f}, середній: {average:.2f}")
    print("Найкращий день:", best_day(revenue))
    print("За прийомом їжі:", dict(Counter(order.time for order in orders).most_common()))


if __name__ == "__main__":
    from orders import Order

    demo = [
        Order(540.0, 50.0, "пт", "вечеря", 2),
        Order(320.0, 30.0, "пт", "обід", 1),
        Order(980.0, 120.0, "сб", "вечеря", 4),
    ]
    print_report(demo)
