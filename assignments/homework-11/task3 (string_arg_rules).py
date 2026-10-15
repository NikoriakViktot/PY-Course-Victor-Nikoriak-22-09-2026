# AI log: З допомогою ментора(AI) розібрався, як працюють параметризовані декоратори.
# Головні труднощі були з синтаксисом (type hints) та логікою перевірок.

from functools import wraps


def string_arg_rules(max_length: int = 1, contains: tuple = (), exclude: tuple = ()):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            for arg in args:

                if not isinstance(arg, str):
                    raise TypeError(f'Помилка: значення повинно бути типу {str}')

                if len(arg) > max_length:
                    raise ValueError(f'Помилка: рядок повиннен бути довжиною менше {max_length}')

                for ex in exclude:

                    if ex in arg:
                        raise ValueError(f'Помилка: рядок не повиннен мати {ex}')

                for word in contains:

                    if word not in arg:
                        raise ValueError("Помилка: рядок не містить обов'язкових символів")

            return func(*args, **kwargs)

        return wrapper

    return decorator


@string_arg_rules(max_length=15, contains=('05', '@'), exclude=("S", 's'))
def create_slogan(name: str) -> str:
    return f"{name} п’є пепсі у своєму новенькому «BMW»!"


if __name__ == "__main__":
    create_slogan('peter@05')  # ok
    create_slogan('peter@06')  # ValueError: Arguments must contain '05'
    create_slogan('Seter@05')  # ValueError: Arguments must not contain 'S'
