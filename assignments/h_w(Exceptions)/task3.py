# AI log: Попросила підказки без готового коду та більш детальне пояснення завдання
from functools import wraps

def string_arg_rules(max_length = 1, contains = (), exclude= ()):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for a in args:
                if not isinstance(a, str):
                    raise TypeError("Argument must be a string")
                elif len(a) > max_length:
                    raise ValueError(f"String must not exceed {max_length} characters")
                for i in contains:
                    if i not in a:
                        raise ValueError(f"Arguments must contain: {i}")
                for j in exclude:
                    if j in a:
                        raise ValueError(f"String must not contain: {j}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


@string_arg_rules(max_length=15, contains=('05', '@'), exclude=("S", 's'))
def create_slogan(name: str) -> str:
    return f"{name} drinks pepsi in his brand new BMW!"

@string_arg_rules(max_length=10, contains=("@",), exclude=("s",))
def introduce(name, city):
    return f"{name} lives in {city}"


if __name__ == "__main__":
    try:
        create_slogan('peter@05')
    except ValueError as e:
        print(e)

    try:
        create_slogan('peter@06')
    except ValueError as e:
        print(e)

    try:
        create_slogan('Seter@05')
    except ValueError as e:
        print(e)

    try:
        create_slogan('HelloBeautifulWorld@05')
    except ValueError as e:
        print(e)

    try:
        print(introduce("Alina@", "Kyiv@"))
    except ValueError as e:
        print(e)


    try:
        print(introduce("Alina@", 25))
    except TypeError as e:
        print(e)

