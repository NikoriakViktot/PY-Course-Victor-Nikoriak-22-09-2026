"""Частина 3. Збереження стану в JSON (урок 14)."""
import json
from datetime import datetime

from models import Delivery, Order


def save_state(path, orders, deliveries):
    """Записує стан у JSON: {"orders": [...], "deliveries": [...]}.

    Замовлення — словник {"id", "time", "bill", "tip", "guests"}, час — рядок isoformat().
    Доставка — словник {"order_id", "district", "fare", "driver"}.
    Кирилиця як є (ensure_ascii=False), відступ 2.
    """
    raise NotImplementedError("частина 3: напиши save_state()")


def load_state(path):
    """Читає файл, записаний save_state → (список Order, список Delivery).

    Файлу ще немає → ([], []) — перший запуск.
    Зіпсований JSON → ValueError("файл даних пошкоджено: ...").
    """
    raise NotImplementedError("частина 3: напиши load_state()")
