"""Задача 1. Правила кафе: день тижня і прийом їжі."""
from models import DAYS


def meal_type(hour):
    """Прийом їжі за годиною: 11–15 → "обід", 17–23 → "вечеря", решта → "інше".

    >>> meal_type(12), meal_type(16), meal_type(18)
    ('обід', 'інше', 'вечеря')
    """
    if 11 <= hour <= 15:
        return "обід"
    if 17 <= hour <= 23:
        return "вечеря"
    return "інше"


def day_name(timestamp):
    """Короткий день тижня з DAYS: datetime(2024, 7, 19, 18, 30) → "пт"."""
    return DAYS[timestamp.weekday()]
