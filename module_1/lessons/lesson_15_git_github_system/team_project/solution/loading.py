"""Задача 3. Читання файлу каси і розбір усіх рядків."""
from parsing import parse_line


def read_lines(path):
    """Непорожні рядки файлу без пробілів і "\\n" по краях. Немає файлу → FileNotFoundError."""
    lines = []
    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                lines.append(line)
    return lines


def load_orders(lines):
    """Список рядків → (чеки, помилки).

    Чеки — RawOrder від parse_line у тому ж порядку.
    Помилки — рядки "рядок N: пояснення", N рахується з 1.
    """
    orders = []
    errors = []
    for number, line in enumerate(lines, start=1):
        try:
            orders.append(parse_line(line))
        except ValueError as error:
            errors.append(f"рядок {number}: {error}")
    return orders, errors
