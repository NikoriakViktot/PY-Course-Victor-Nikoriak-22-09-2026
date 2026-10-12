# якщо перевіряти довжину раніше за тип, виклик create_slogan(12345) викличе помилку TypeError, бо len() не працює з int,
# тому порядок критичний: спочатку переконуємося, що це рядок, а потім міряємо довжину

def arg_rules(type_: type, max_length: int, contains: list):

    def decorator(func):

        def wrapper(*args, **kwargs):

            arg_value = args[0]

            # перевіряємо тип нашого значення і чи співпадає він задоному
            if not isinstance(arg_value, type_):
                print("Помилка, повинно бути значення типу -> int,str,float..")
                return False

            # перевіряємо чи довжина введеного значення, не більше за максимальне
            if len(arg_value) > max_length:
                print(f"Помилка, неправильна довжина рядка, потрібно менше {max_length} символів")
                return False

            # перевіряємо чи має введене значення, обов'язкові символи
            for word in contains:
                if word not in arg_value:
                    print("Помилка: рядок не містить обов'язкових символів")
                    return False

            return func(*args, **kwargs)

        return wrapper

    return decorator


@arg_rules(type_=str, max_length=15, contains=['05', '@'])
def create_slogan(name: str) -> str:
    return f"{name} п’є пепсі у своєму новенькому «BMW»!"


assert create_slogan('johndoe05@gmail.com') is False
assert create_slogan('S@SH05') == 'S@SH05 п’є пепсі у своєму новенькому «BMW»!'

# create_slogan(12345)


@arg_rules(type_=str, max_length=15, contains=['05', '@'])
def favorite_movie(name):
    return f"Мій улюблений фільм називається {name}"


new_string = 'Інтерстеллар'

print(favorite_movie(new_string))
favorite_movie('Dune')

# AI log: Саму ідею декоратора та перевірки через 'if' написав сам.
# Що я не міг зрозуміти: як правильно передати аргументи в декоратор і як "дістати" той самий рядок, який вводить користувач.
# Проблеми з якими зіткнувся:
# - зробив 2 рівні функції замість 3-х, через що загубив саму функцію func;
# - перевіряв налаштування декоратора (наприклад, вимірював довжину числа 15), а не сам введений рядок.
# Ментор(AI) вказав на помилки, і я самостійно виправив архітектуру та логіку перевірки.
