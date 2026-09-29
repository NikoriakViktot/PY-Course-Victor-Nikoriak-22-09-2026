"""dispatch — диспетчерська «Смачно + Таксі»: артефакт модуля 2 (урок 28)."""

from dispatch.models import Order
from dispatch.service import Dispatcher

__all__ = ["Dispatcher", "Order"]
