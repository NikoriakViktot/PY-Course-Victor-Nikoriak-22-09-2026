# AI log: Виконав аналіз коду від ШІ. З'ясував, що перехоплення базового Exception є небезпечним,
# бо воно ховає трасбек і робить пошук одруківок (наприклад, NameError) майже неможливим.
# Закріпив правило: обробку винятків треба виносити з базової функції на рівень її виклику.

class SomethingWrong(Exception):
    pass


def check_password(password, max_length):

    if len(password) < max_length:
        raise SomethingWrong(f"Довжина паролю повинна бути більша за {max_length}")

# весія від ШІ без необхідності перехоплює асболютно всі помилки через Exception, через що викликання нашої raise,
# перекриється головнішим класом Exception, а також ми втрачаємо трасбек, який вкаже на місце де знаходиться помилка,
# я би виніс обробку помилки з функції, і переніс її в блок передавання функції, щоб можна було явно видно яку помилку ми отримуємо

# код від AI
# def check_password(password, max_length):
#     try:
#         if len(password) < max_length:
#             raise SomethingWrong(f"Довжина паролю повинна бути більша за {max_length}")
#     except Exception as e:
#         print(f"Виникла помилка під час перевірки пароля: {e}")


def input_password(password):

    try:
        check_password(password, 8)

    except SomethingWrong as e:
        return f"Помилка: {e}"

    finally:
        print(f"Пароль: {password}")


input_password('ef@fmN:!.L')
