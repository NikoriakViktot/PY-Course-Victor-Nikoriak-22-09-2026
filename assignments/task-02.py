# Task 2

# AI log: Not used

from functools import wraps

def logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        arg_part = [repr(arg) for arg in args]
        arg_part += [f"{key}={value!r}" for key,value in kwargs.items()]
        arguments = ", ".join(arg_part)
        print(f"{func.__name__} called with {arguments}")
        return func(*args, **kwargs)
    return wrapper


@logger
def add(x, y):
    return x + y


@logger
def square_all(*args):
    return [arg ** 2 for arg in args]


@logger
def test_some2(a, b, c):
    return a


print(test_some2(2, b="y", c="e"))
