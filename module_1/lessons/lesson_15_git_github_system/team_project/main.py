"""Звіт каси кафе: python main.py kasa_2024_07.txt

Цей файл дає викладач. Він лише з'єднує шість задач команди.
"""
import sys

from loading import load_orders, read_lines
from output import format_report, save_json
from report import build_report


def main(args):
    if len(args) != 2:
        print("Використання: python main.py ФАЙЛ_КАСИ, наприклад: python main.py kasa_2024_07.txt")
        return 1
    try:
        lines = read_lines(args[1])
    except FileNotFoundError:
        print("Немає файлу каси:", args[1])
        return 1
    orders, errors = load_orders(lines)
    report = build_report(orders, errors)
    save_json(report, "report.json")
    with open("errors.txt", "w", encoding="utf-8") as file:
        for message in errors:
            print(message, file=file)
    print(format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
