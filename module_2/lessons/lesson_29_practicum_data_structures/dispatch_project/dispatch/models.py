from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    """Замовлення: незмінний запис-значення (урок 23)."""

    order_id: int
    address: str
    deadline: str | None = None   # "ГГ:ХХ" — такі рядки порівнюються як час

    def __str__(self):
        text = f"#{self.order_id} {self.address}"
        return f"{text} до {self.deadline}" if self.deadline else text
