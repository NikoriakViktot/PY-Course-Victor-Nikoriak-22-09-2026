# print(add(4, 5))
# виведе один рядок виконання декоратора - (add викликано з аргументами 4, 5), а інший результат виконання функції - (9)

import functools


def logger(func):

    # прописуємо для того щоб назва функції не змінилась на wrapper
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        args_ = list(map(str, args))                           # перетворюэмо args з кортежу на лист
        kwargs_ = [f"{k}={v}" for k, v in kwargs.items()]      # перетворюємо словник в лист
        arg_kw = args_ + kwargs_                               # об'єднуємо в один лист

        print(f"{func.__name__} викликано з аргументами {", ".join(arg_kw)}")

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


# print(add(4, 5))

add(4, 5)
test_some2(2, b='y', c='e')

# print(add.__name__)           # назва функції (wrapper) - без functools
# print(add.__name__)           # назва функції (add) - з functools

# AI log: Сам написав основу декоратора, але зіткнувся з проблемами:
# - загубив виклик оригінальної функції (декоратор повертав текст, а сама функція не виконувалась);
# - не міг красиво відформатувати аргументи: отримував SyntaxError у генераторі списків;
# - забув перетворити об'єкт map() на список через list().
# За допомогою підказок ментора(AI) виправив логіку виклику, склеїв аргументи через метод .join()
# та розібрався, як @functools.wraps зберігає ім'я функції.
