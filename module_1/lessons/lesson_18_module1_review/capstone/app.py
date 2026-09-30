"""Смачно + Таксі: консольна система доставки. Цей файл дає викладач.

    python app.py add-order "2024-07-19 18:30;540.00;50;2"
    python app.py import kasa_2024_07.txt
    python app.py add-delivery 1 Оболонь 230 D-3
    python app.py find 1
    python app.py report
    python app.py voucher 500
"""
import sys

import commands
from storage import load_state, save_state

DATA_FILE = "data.json"


def read_lines(path):
    with open(path, encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def to_int(text, what):
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"{what} має бути цілим числом, а маємо {text}")


def run(command, args, orders, deliveries):
    """Виконує команду і повертає (текст, чи змінився стан)."""
    if command == "add-order" and len(args) == 1:
        return commands.add_order(orders, deliveries, args[0]), True
    if command == "import" and len(args) == 1:
        return commands.import_kasa(orders, deliveries, read_lines(args[0])), True
    if command == "add-delivery":
        return commands.add_delivery(orders, deliveries, args), True
    if command == "find" and len(args) == 1:
        return commands.find_order(orders, deliveries, to_int(args[0], "номер замовлення")), False
    if command == "report" and not args:
        return commands.report(orders, deliveries), False
    if command == "voucher" and len(args) == 1:
        return commands.voucher(orders, deliveries, to_int(args[0], "сума ваучера")), False
    raise ValueError("невідома команда або не ті аргументи")


def main(args, data_file=DATA_FILE):
    if len(args) < 2:
        print(__doc__)
        return 1
    try:
        orders, deliveries = load_state(data_file)
        text, changed = run(args[1], args[2:], orders, deliveries)
    except FileNotFoundError as error:
        print("Помилка: немає файлу", error.filename)
        return 1
    except ValueError as error:
        print("Помилка:", error)
        return 1
    if changed:
        save_state(data_file, orders, deliveries)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
