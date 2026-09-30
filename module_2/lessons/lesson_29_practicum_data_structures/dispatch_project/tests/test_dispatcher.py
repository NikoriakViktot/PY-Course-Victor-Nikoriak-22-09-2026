import pytest

from dispatch import Dispatcher
from dispatch.structures import EmptyError


def test_regular_orders_first_come_first_served(dispatcher, make_order):
    first, second = make_order(), make_order()
    dispatcher.receive(first)
    dispatcher.receive(second)
    assert dispatcher.assign("Оксана") == first
    assert dispatcher.assign("Тарас") == second


def test_urgent_orders_by_earliest_deadline(dispatcher, make_order):
    regular = make_order()
    late = make_order(deadline="09:40")
    early = make_order(deadline="09:25")
    dispatcher.receive(regular)
    dispatcher.receive(late, urgent=True)
    dispatcher.receive(early, urgent=True)
    assert [dispatcher.assign("x") for _ in range(3)] == [early, late, regular]


def test_urgent_order_needs_deadline(dispatcher, make_order):
    with pytest.raises(ValueError, match="без дедлайну"):
        dispatcher.receive(make_order(), urgent=True)


def test_undo_returns_order_to_the_front(dispatcher, make_order):
    first, second = make_order(), make_order()
    dispatcher.receive(first)
    dispatcher.receive(second)
    dispatcher.assign("Оксана")
    assert dispatcher.undo() == ("Оксана", first)
    assert dispatcher.assigned_to("Оксана") == []
    assert dispatcher.assign("Марія") == first      # скасоване — першим


def test_nothing_to_assign_or_undo(dispatcher):
    with pytest.raises(EmptyError):
        dispatcher.assign("Оксана")
    with pytest.raises(EmptyError):
        dispatcher.undo()


def test_len_counts_waiting_orders(dispatcher, make_order):
    dispatcher.receive(make_order())
    dispatcher.receive(make_order(deadline="10:00"), urgent=True)
    assert len(dispatcher) == 2
    dispatcher.assign("Оксана")
    assert len(dispatcher) == 1


def test_suggest_addresses(dispatcher):
    assert dispatcher.suggest("Хр") == ["Хрещатик, 1", "Хрещатик, 22"]
    assert dispatcher.suggest("Х", limit=1) == ["Хорива, 5"]


def test_route_price_is_cached():
    calls = []

    def slow_price(origin, destination):
        calls.append((origin, destination))
        return 100

    dispatcher = Dispatcher(price_function=slow_price, cache_size=2)
    for route in [("Поділ", "Центр"), ("Поділ", "Центр"), ("Центр", "Оболонь"), ("Поділ", "Центр")]:
        assert dispatcher.route_price(*route) == 100
    assert calls == [("Поділ", "Центр"), ("Центр", "Оболонь")]
    assert dispatcher.cache_stats == {"hits": 2, "misses": 2, "size": 2}
