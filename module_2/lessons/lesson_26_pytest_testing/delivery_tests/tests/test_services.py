from unittest.mock import patch

from delivery.services import confirm_order


def test_confirm_order_sends_sms():
    # patch там, де ім'я ВИКОРИСТОВУЄТЬСЯ: delivery.services.send_sms
    with patch("delivery.services.send_sms") as fake_send:
        assert confirm_order(101, "+380501234567") == "confirmed"
    fake_send.assert_called_once_with("+380501234567", "Замовлення №101 прийнято")
