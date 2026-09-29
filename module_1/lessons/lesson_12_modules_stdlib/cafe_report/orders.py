"""Чеки кафе: сирі записи з каси і перетворення на Order з уроку 7."""
import random
from datetime import datetime, timedelta
from typing import NamedTuple

from rules import day_from_timestamp, meal_type_from_hour


class RawOrder(NamedTuple):
    """Чек, як його віддає каса: з міткою часу."""
    total_bill: float
    tip: float
    size: int
    timestamp: datetime


class Order(NamedTuple):
    """Чек, як його рахує звіт з уроку 7."""
    total_bill: float
    tip: float
    day: str
    time: str
    size: int


def generate_raw_orders(n, seed=None):
    """n випадкових чеків за 2023–2024 роки, кафе працює з 9:00 до 23:00."""
    rng = random.Random(seed)
    start = datetime(2023, 1, 1)
    days = (datetime(2025, 1, 1) - start).days
    raw_orders = []
    for _ in range(n):
        timestamp = start + timedelta(days=rng.randrange(days),
                                      hours=rng.randint(9, 22),
                                      minutes=rng.randint(0, 59))
        bill = round(rng.uniform(150, 1500), 2)
        tip = round(bill * rng.uniform(0, 0.15), 2)
        raw_orders.append(RawOrder(bill, tip, rng.randint(1, 6), timestamp))
    return raw_orders


def in_month(raw, year, month):
    """Чи належить чек до вказаного місяця."""
    return raw.timestamp.year == year and raw.timestamp.month == month


def to_order(raw):
    """RawOrder -> Order: день і прийом їжі обчислюються з мітки часу."""
    return Order(
        total_bill=raw.total_bill,
        tip=raw.tip,
        day=day_from_timestamp(raw.timestamp),
        time=meal_type_from_hour(raw.timestamp.hour),
        size=raw.size,
    )
