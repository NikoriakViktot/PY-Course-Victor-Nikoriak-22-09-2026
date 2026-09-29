"""Сповіщення клієнта. Шлюз SMS передається параметром — його легко підмінити в тесті."""


class SmsGateway:
    """Справжній шлюз: ходить у мережу й коштує гроші за кожне повідомлення."""

    def send(self, phone, text):
        raise ConnectionError("справжня мережа недоступна в навчальному проєкті")


def notify_client(order_id, phone, minutes, gateway):
    """Надсилає клієнту час доставки. Повертає True, якщо SMS пішло."""
    text = f"Замовлення №{order_id} буде за {minutes} хв"
    try:
        gateway.send(phone, text)
    except ConnectionError:
        return False
    return True
