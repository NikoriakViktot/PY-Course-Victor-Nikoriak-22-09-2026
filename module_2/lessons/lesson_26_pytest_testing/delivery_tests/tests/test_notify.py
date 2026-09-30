from unittest.mock import Mock

from delivery.notify import notify_client


def test_sms_text_and_phone():
    gateway = Mock()
    assert notify_client(101, "+380501234567", 25, gateway) is True
    gateway.send.assert_called_once_with("+380501234567", "Замовлення №101 буде за 25 хв")


def test_gateway_failure_does_not_crash_order():
    gateway = Mock()
    gateway.send.side_effect = ConnectionError("шлюз не відповідає")
    assert notify_client(101, "+380501234567", 25, gateway) is False
    assert gateway.send.call_count == 1


def test_fake_gateway_records_messages():
    class FakeGateway:
        def __init__(self):
            self.sent = []

        def send(self, phone, text):
            self.sent.append((phone, text))

    gateway = FakeGateway()
    notify_client(7, "+380670000000", 40, gateway)
    assert gateway.sent == [("+380670000000", "Замовлення №7 буде за 40 хв")]
