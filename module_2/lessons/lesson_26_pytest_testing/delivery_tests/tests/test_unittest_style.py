"""Ті самі перевірки тарифу в стилі unittest — pytest запускає і їх."""

import unittest

from delivery.pricing import Tariff, fare


class FareTest(unittest.TestCase):
    def setUp(self):
        self.tariff = Tariff(base=40, per_km=12, min_fare=80)

    def test_long_trip(self):
        self.assertEqual(fare(10, self.tariff), 160)

    def test_short_trip(self):
        self.assertEqual(fare(0.5, self.tariff), 80)

    def test_negative_distance(self):
        with self.assertRaises(ValueError):
            fare(-1, self.tariff)
