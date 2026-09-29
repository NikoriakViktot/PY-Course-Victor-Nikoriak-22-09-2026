"""Задача 4. Підрахунки за днями і прийомами їжі."""
from rules import day_name, meal_type


def revenue_by_day(orders):
    """Виторг за днями тижня: {"пт": 860.0, ...}. Лише дні, у які були чеки."""
    raise NotImplementedError("задача 4: напиши revenue_by_day()")


def best_day(revenue):
    """День з найбільшим виторгом; для порожнього словника — None."""
    raise NotImplementedError("задача 4: напиши best_day()")


def count_by_meal(orders):
    """Кількість чеків за прийомом їжі: {"вечеря": 3, "обід": 1}."""
    raise NotImplementedError("задача 4: напиши count_by_meal()")
