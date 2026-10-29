# Task 5
from tkinter.font import names


# AI log: not used

def arg_rules(type_: type, max_length: int, contains: list):
    def decorator(func):
        def examination(*args, **kwargs):
            if args:
                value = args[0]
            elif kwargs:
                value = list(kwargs.values())[0]
            else:
                print("Нет данных")
                return False
            if isinstance(value, type_):
                if len(value) <= max_length:
                    for item in contains:
                        if item not in value:
                            print(f'{item} данного символа нет в строке')
                            return False
                    return func(*args,**kwargs)
                else:
                    print("Превышено максимальное количество символов")
                    return False
            else:
                print("Неверный формат")
                return False

        return examination

    return decorator


@arg_rules(type_=str, max_length=15, contains=['05', '@'])
def create_slogan(name: str) -> str:
    return f"{name} drinks pepsi in his brand new BMW!"


assert create_slogan('johndoe05@gmail.com') is False
assert create_slogan('S@SH05') == 'S@SH05 drinks pepsi in his brand new BMW!'

