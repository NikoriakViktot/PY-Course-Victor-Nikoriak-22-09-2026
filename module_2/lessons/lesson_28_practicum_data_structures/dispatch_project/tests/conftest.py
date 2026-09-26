import pytest

from dispatch import Dispatcher, Order


@pytest.fixture
def addresses():
    return ["Хрещатик, 1", "Хрещатик, 22", "Хорива, 5", "Оболонська, 12", "Олегівська, 3"]


@pytest.fixture
def dispatcher(addresses):
    return Dispatcher(addresses)


@pytest.fixture
def make_order():
    """Фабрика замовлень (урок 25): номери йдуть по черзі."""
    counter = iter(range(1, 1000))

    def make(address="Хорива, 5", deadline=None):
        return Order(next(counter), address, deadline)

    return make
