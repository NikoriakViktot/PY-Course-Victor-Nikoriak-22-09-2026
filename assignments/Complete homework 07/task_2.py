# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні, опрацьовуванні помилок в моєму коді

def logger(func):
    def wrapper(*args, **kwargs):
        print(f"{func.__name__} called with {', '.join(str(a) for a in args)}")
        return func(*args, **kwargs)
    return wrapper

@logger
def add(x, y):
    return x + y

# print(add(4, 5)) покаже: add called with 4, 5
# потім 9
print(add(4, 5))

print(add.__name__)
# без functools - wrapper

import functools

def logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"{func.__name__} called with {', '.join(str(a) for a in args)}")
        return func(*args, **kwargs)
    return wrapper

@logger
def add(x, y):
    return x + y

print(add.__name__)
# з functools - wrapper

@logger
def square_all(*args):
    return [arg ** 2 for arg in args]

@logger
def test_some2(a, b, c):
    return a


print(test_some2 (2, b='y', c='e'))
#test_some2 called with 2
#2