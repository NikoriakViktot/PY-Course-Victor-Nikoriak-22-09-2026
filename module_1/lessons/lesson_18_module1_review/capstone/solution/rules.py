"""Частина 1. Правила кафе (урок 12)."""
from models import DAYS


def meal_type(hour):
    """Прийом їжі за годиною: 11–15 → "обід", 17–23 → "вечеря", решта → "інше"."""
    if 11 <= hour <= 15:
        return "обід"
    if 17 <= hour <= 23:
        return "вечеря"
    return "інше"


def day_name(time):
    """Короткий день тижня з DAYS: datetime(2024, 7, 19, 18, 30) → "пт"."""
    return DAYS[time.weekday()]
