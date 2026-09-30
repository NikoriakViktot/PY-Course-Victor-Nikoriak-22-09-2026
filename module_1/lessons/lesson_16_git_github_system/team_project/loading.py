"""Задача 3. Читання файлу каси і розбір усіх рядків."""
from parsing import parse_line


def read_lines(path):
    """Непорожні рядки файлу без пробілів і "\\n" по краях. Немає файлу → FileNotFoundError."""
    raise NotImplementedError("задача 3: напиши read_lines()")


def load_orders(lines):
    """Список рядків → (чеки, помилки).

    Чеки — RawOrder від parse_line у тому ж порядку.
    Помилки — рядки "рядок N: пояснення", N рахується з 1.
    """
    raise NotImplementedError("задача 3: напиши load_orders()")
