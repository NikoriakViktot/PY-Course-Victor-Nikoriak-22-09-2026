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
    data = {
        "orders": [
            {"id": order.id, "time": order.time.isoformat(), "bill": order.bill,
             "tip": order.tip, "guests": order.guests}
            for order in orders
        ],
        "deliveries": [
            {"order_id": delivery.order_id, "district": delivery.district,
             "fare": delivery.fare, "driver": delivery.driver}
            for delivery in deliveries
        ],
    }
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_state(path):
    """Читає файл, записаний save_state → (список Order, список Delivery).

    Файлу ще немає → ([], []) — перший запуск.
    Зіпсований JSON → ValueError("файл даних пошкоджено: ...").
    """
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return [], []
    except json.JSONDecodeError as error:
        raise ValueError(f"файл даних пошкоджено: {error}")
    orders = [
        Order(item["id"], datetime.fromisoformat(item["time"]), item["bill"], item["tip"], item["guests"])
        for item in data["orders"]
    ]
    deliveries = [
        Delivery(item["order_id"], item["district"], item["fare"], item["driver"])
        for item in data["deliveries"]
    ]
    return orders, deliveries
