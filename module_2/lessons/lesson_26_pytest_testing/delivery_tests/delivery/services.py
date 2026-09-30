"""Сервіс замовлень. Імпортує send_sms напряму — приклад для правила «patch where used»."""

from delivery.sms import send_sms


def confirm_order(order_id, phone):
    send_sms(phone, f"Замовлення №{order_id} прийнято")
    return "confirmed"
