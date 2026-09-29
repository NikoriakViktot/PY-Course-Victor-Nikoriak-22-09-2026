"""Частина 2. Розбір і перевірка вхідних даних (урок 13)."""
from datetime import datetime

from models import Delivery, Order


def parse_order(line, order_id):
    """Рядок каси "2024-07-19 18:30;540.00;50;2" → Order з номером order_id.

    Зіпсований рядок → ValueError з поясненням: не 4 поля, не число,
    неіснуюча дата, сума <= 0, чайові < 0, гостей < 1.
    """
    fields = line.split(";")
    if len(fields) != 4:
        raise ValueError(f"очікували 4 поля, а маємо {len(fields)}")
    time_text, bill_text, tip_text, guests_text = fields
    time = datetime.strptime(time_text, "%Y-%m-%d %H:%M")
    bill, tip, guests = float(bill_text), float(tip_text), int(guests_text)
    if bill <= 0:
        raise ValueError(f"сума чека має бути більшою за 0, а маємо {bill}")
    if tip < 0:
        raise ValueError(f"чайові не можуть бути від'ємними: {tip}")
    if guests < 1:
        raise ValueError(f"гостей має бути хоча б один, а маємо {guests}")
    return Order(order_id, time, bill, tip, guests)


def parse_delivery(fields):
    """["1", "Оболонь", "230", "D-3"] → Delivery(1, "Оболонь", 230, "D-3").

    Не 4 поля, номер чи вартість не цілі числа, вартість <= 0,
    порожній район чи водій → ValueError з поясненням.
    """
    if len(fields) != 4:
        raise ValueError(f"для доставки потрібно 4 значення: НОМЕР РАЙОН ВАРТІСТЬ ВОДІЙ, а маємо {len(fields)}")
    order_text, district, fare_text, driver = (field.strip() for field in fields)
    try:
        order_id, fare = int(order_text), int(fare_text)
    except ValueError:
        raise ValueError(f"номер замовлення і вартість мають бути цілими числами: {order_text}, {fare_text}")
    if fare <= 0:
        raise ValueError(f"вартість доставки має бути більшою за 0, а маємо {fare}")
    if not district or not driver:
        raise ValueError("район і водій не можуть бути порожніми")
    return Delivery(order_id, district, fare, driver)
