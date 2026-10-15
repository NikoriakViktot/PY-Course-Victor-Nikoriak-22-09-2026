# AI log: Ментор(AI) пояснив, чому не варто ховати помилки всередині дрібних функцій.

# якби я використав словник з значенняси операцій замість if, то при викликанні ключа якого не має в словнику, ми би отримали KeyError,
# що для користувача не дуже зрозуміло, що це за помилка, тому краще викликати самому ValueError

# викликаючи operation_mapper("/")(1, 0), ми отримуємо виняток ZeroDivisionError, обробляти цю помилку повинен користувач, а не сама функція,
# бо вона лише виконує дію, і не знає всього контексту всієї програми, а нам потрбіно щоб вона виконалася, і вже потім видала помилку

def _add(a, b):
    print("Виконується додавання")
    return a + b


def _minus(a, b):
    print("Виконується віднімання")
    return a - b


def _mult(a, b):
    print("Виконується множення")
    return a * b


def _div(a, b):
    print("Виконується ділення")
    return a / b


def _sq(a, b):
    print("Виконується піднесення до степення")
    return a**b


def operation_mapper(operation):

    if operation not in ['+', '-', '/', '*', '**']:
        raise ValueError("Введіть правильний знак операції (+, -, /, *, **)")

    def wrapper(a, b):

        if operation == '+':
            return _add(a, b)

        if operation == '-':
            return _minus(a, b)

        if operation == '*':
            return _mult(a, b)

        if operation == '/':
            return _div(a, b)

        if operation == '**':
            return _sq(a, b)

    return wrapper


# print(operation_mapper("/")(1, 0))
print(operation_mapper("+")(1, 2))   # 3
print(operation_mapper("**")(2, 10))  # 1024
# print(operation_mapper("%"))         # should not silently fail — see below
