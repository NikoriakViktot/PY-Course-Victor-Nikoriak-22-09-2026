"""Спільні дані системи «Смачно + Таксі». Цей файл дає викладач."""
from datetime import datetime
from typing import NamedTuple

DAYS = ("пн", "вт", "ср", "чт", "пт", "сб", "нд")


class Order(NamedTuple):
    """Замовлення в кафе."""
    id: int
    time: datetime
    bill: float
    tip: float
    guests: int


class Delivery(NamedTuple):
    """Доставка замовлення таксі."""
    order_id: int
    district: str
    fare: int
    driver: str
