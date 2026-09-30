import pytest

from delivery.pricing import Tariff, apply_promo, fare


def test_long_trip_is_base_plus_distance(day_tariff):
    # Arrange: тариф приходить із fixture
    km = 10
    # Act
    price = fare(km, day_tariff)
    # Assert
    assert price == 160


def test_short_trip_costs_min_fare(day_tariff):
    assert fare(0.5, day_tariff) == 80


@pytest.mark.parametrize(
    "km, expected",
    [
        (0, 80),       # нуль кілометрів — усе одно мінімум
        (3, 80),       # 40 + 36 = 76 < 80
        (3.5, 82),     # 40 + 42 = 82 — вже більше за мінімум
        (10, 160),
        (2.25, 80),    # 40 + 27 = 67
    ],
    ids=["zero", "below-min", "just-above-min", "long", "fraction"],
)
def test_fare_table(km, expected, day_tariff):
    assert fare(km, day_tariff) == expected


def test_negative_distance_is_rejected(day_tariff):
    with pytest.raises(ValueError, match="від'ємною"):
        fare(-1, day_tariff)


def test_night_tariff_is_independent():
    night = Tariff(base=60, per_km=15, min_fare=120)
    assert fare(4, night) == 120
    assert fare(5, night) == 135


@pytest.mark.parametrize("amount, percent, expected", [(340, 10, 306), (340, 0, 340), (99, 50, 50), (95, 15, 81)])
def test_apply_promo(amount, percent, expected):
    assert apply_promo(amount, percent) == expected


@pytest.mark.parametrize("percent", [-5, 51, 100])
def test_apply_promo_rejects_bad_percent(percent):
    with pytest.raises(ValueError):
        apply_promo(340, percent)


def test_average_check_is_approximately_right():
    checks = [340, 305, 410]
    assert sum(checks) / len(checks) == pytest.approx(351.67, abs=0.01)
