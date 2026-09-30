"""Спільні дані команди. Цей файл дає викладач — не змінюйте його без узгодження з усіма."""
from datetime import datetime
from typing import NamedTuple

DAYS = ("пн", "вт", "ср", "чт", "пт", "сб", "нд")


class RawOrder(NamedTuple):
    """Чек з каси."""
    total_bill: float
    tip: float
    size: int
    timestamp: datetime
