"""Частина 5. Доставка таксі (уроки 11, 16)."""
from collections import Counter


def delivery_index(deliveries):
    """{номер замовлення: доставка} — щоб знаходити доставку за один крок."""
    return {delivery.order_id: delivery for delivery in deliveries}


def top_districts(deliveries, k=3):
    """k найпопулярніших районів: [("Оболонь", 2), ...], від більшого до меншого."""
    return Counter(delivery.district for delivery in deliveries).most_common(k)


def voucher_pair(deliveries, amount):
    """Номери замовлень двох доставок, які разом коштують рівно amount, або None.

    Один прохід зі словником (Two Sum). Порядок — як у списку доставок.
    """
    seen = {}
    for delivery in deliveries:
        need = amount - delivery.fare
        if need in seen:
            return seen[need], delivery.order_id
        seen[delivery.fare] = delivery.order_id
    return None
