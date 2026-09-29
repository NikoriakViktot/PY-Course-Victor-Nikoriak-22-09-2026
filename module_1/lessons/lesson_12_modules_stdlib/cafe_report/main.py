"""Звіт кафе за місяць: python main.py РІК МІСЯЦЬ"""
import calendar
import sys

from orders import generate_raw_orders, in_month, to_order
from report import print_report
from rules import MONTHS


def main(args):
    if len(args) != 3:
        print("Використання: python main.py РІК МІСЯЦЬ, наприклад: python main.py 2024 7")
        return
    year, month = int(args[1]), int(args[2])
    raw_orders = generate_raw_orders(2000, seed=42)
    orders = [to_order(raw) for raw in raw_orders if in_month(raw, year, month)]
    days_in_month = calendar.monthrange(year, month)[1]
    print(f"Звіт кафе: {MONTHS[month]} {year}, днів: {days_in_month}, чеків: {len(orders)}")
    print_report(orders)


if __name__ == "__main__":
    main(sys.argv)
