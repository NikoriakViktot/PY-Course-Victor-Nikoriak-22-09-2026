# print(add(4, 5)) поверне спочатку саму строку add called with 4, 5 а потім результат додавання 9
# Без functools.wraps, add.__name__ поверне wrapper, а з ним add

def logger(func):
    def wrapper(*args, **kwargs):
        pos_args = [str(arg) for arg in args]
        kw_parts = [f"{k}={v!r}" for k, v in kwargs.items()]
        all_args = ", ".join(pos_args + kw_parts)
        print(f"{func.__name__} called with {all_args}")
        return func(*args, **kwargs)
    return wrapper


@logger
def add(x, y):
    return x + y


@logger
def square_all(*args):
    return [arg**2 for arg in args]


@logger
def test_some2(a, b, c):
    return a


print(add(4, 5))

# AI log: Попросив пояснити мені логіку того як привести строку у точно той самий вигялд як в умові завдання