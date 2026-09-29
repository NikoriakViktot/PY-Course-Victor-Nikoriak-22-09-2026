"""Допоміжне для тестів: тимчасова заміна чужої функції на «заглушку»."""
from contextlib import contextmanager


@contextmanager
def replaced(module, **fakes):
    """Усередині with модуль бачить fakes замість справжніх функцій, потім усе повертається.

    Так задачу 4 можна перевірити, навіть коли задача 1 ще не готова.
    """
    originals = {name: getattr(module, name) for name in fakes}
    for name, fake in fakes.items():
        setattr(module, name, fake)
    try:
        yield
    finally:
        for name, original in originals.items():
            setattr(module, name, original)


def raises_value_error(func, *args):
    """True, якщо func(*args) піднімає ValueError з непорожнім поясненням."""
    try:
        func(*args)
    except ValueError as error:
        return str(error) != ""
    return False
