"""Тарифи й знижки."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tariff:
    base: int       # подача, грн
    per_km: int     # грн за кілометр
    min_fare: int   # мінімальна вартість поїздки, грн


def fare(km, tariff):
    """Вартість поїздки на km кілометрів, не менша за мінімальну."""
    if km < 0:
        raise ValueError(f"відстань не може бути від'ємною: {km}")
    return max(tariff.min_fare, round(tariff.base + tariff.per_km * km))


def apply_promo(amount, percent):
    """Сума після знижки percent % (від 0 до 50), округлена до гривні."""
    if not 0 <= percent <= 50:
        raise ValueError(f"знижка має бути від 0 до 50 %, а маємо {percent}")
    return round(amount * (100 - percent) / 100)
