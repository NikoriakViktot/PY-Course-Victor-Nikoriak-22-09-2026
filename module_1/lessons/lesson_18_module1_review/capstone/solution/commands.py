"""Частина 6. Команди системи: з'єднують кафе і таксі (уроки 7, 13, 15).

Кожна команда отримує стан (orders, deliveries) і аргументи,
змінює списки на місці, якщо треба, і повертає текст для людини.
Неправильні дані → ValueError з поясненням; друкує лише app.py.
"""
from cafe import cafe_stats
from parsing import parse_delivery, parse_order
from rules import day_name, meal_type
from taxi import delivery_index, top_districts, voucher_pair


def next_id(orders):
    """Номер для нового замовлення: на 1 більший за найбільший, 1 для порожнього списку."""
    return max((order.id for order in orders), default=0) + 1


def add_order(orders, deliveries, line):
    """Додає замовлення з рядка каси. → "Замовлення №1: пт, вечеря, 540.00 грн"."""
    order = parse_order(line, next_id(orders))
    orders.append(order)
    return f"Замовлення №{order.id}: {day_name(order.time)}, {meal_type(order.time.hour)}, {order.bill:.2f} грн"


def import_kasa(orders, deliveries, lines):
    """Додає всі правильні рядки каси. Перший рядок відповіді — "Імпортовано: 4, пропущено: 5",
    далі по рядку на кожен пропущений: "  рядок 3: пояснення"."""
    added = 0
    errors = []
    for number, line in enumerate(lines, start=1):
        try:
            orders.append(parse_order(line, next_id(orders)))
            added += 1
        except ValueError as error:
            errors.append(f"  рядок {number}: {error}")
    return "\n".join([f"Імпортовано: {added}, пропущено: {len(errors)}"] + errors)


def add_delivery(orders, deliveries, fields):
    """Додає доставку. Замовлення має існувати і ще не мати доставки, інакше ValueError.
    → "Доставка №1: Оболонь, 230 грн, водій D-3"."""
    delivery = parse_delivery(fields)
    if delivery.order_id not in {order.id for order in orders}:
        raise ValueError(f"замовлення №{delivery.order_id} немає")
    if delivery.order_id in delivery_index(deliveries):
        raise ValueError(f"замовлення №{delivery.order_id} вже має доставку")
    deliveries.append(delivery)
    return f"Доставка №{delivery.order_id}: {delivery.district}, {delivery.fare} грн, водій {delivery.driver}"


def find_order(orders, deliveries, order_id):
    """Замовлення і його доставка за номером. Немає → ValueError.
    → "№1 2024-07-19 18:30, 540.00 грн, гостей: 2, доставка: Оболонь (230 грн)"
    або "..., доставка: немає"."""
    by_id = {order.id: order for order in orders}
    if order_id not in by_id:
        raise ValueError(f"замовлення №{order_id} немає")
    order = by_id[order_id]
    delivery = delivery_index(deliveries).get(order_id)
    where = f"{delivery.district} ({delivery.fare} грн)" if delivery else "немає"
    return f"№{order.id} {order.time:%Y-%m-%d %H:%M}, {order.bill:.2f} грн, гостей: {order.guests}, доставка: {where}"


def report(orders, deliveries):
    """Спільний звіт кафе й таксі, 5 рядків:

    Замовлень: 4, з доставкою: 3
    Кафе: 3040.00 грн, середній чек 760.00 грн, найкращий день: нд
    Таксі: 700 грн за доставки
    Райони: Оболонь 2, Поділ 1
    Разом: 3740.00 грн
    """
    stats = cafe_stats(orders)
    taxi_total = sum(delivery.fare for delivery in deliveries)
    districts = ", ".join(f"{name} {count}" for name, count in top_districts(deliveries))
    return "\n".join([
        f"Замовлень: {stats['orders']}, з доставкою: {len(deliveries)}",
        f"Кафе: {stats['revenue']:.2f} грн, середній чек {stats['average']:.2f} грн, найкращий день: {stats['best_day'] or '—'}",
        f"Таксі: {taxi_total} грн за доставки",
        f"Райони: {districts or '—'}",
        f"Разом: {stats['revenue'] + taxi_total:.2f} грн",
    ])


def voucher(orders, deliveries, amount):
    """Дві доставки на суму ваучера. → "Ваучер 500 грн: доставки замовлень №1 і №3"
    або "Ваучер 500 грн: такої пари немає"."""
    pair = voucher_pair(deliveries, amount)
    if pair is None:
        return f"Ваучер {amount} грн: такої пари немає"
    return f"Ваучер {amount} грн: доставки замовлень №{pair[0]} і №{pair[1]}"
