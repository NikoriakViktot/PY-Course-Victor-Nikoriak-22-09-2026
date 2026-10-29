# Task 3

# AI log: not used

def _add(a, b):
    return a + b


def _sub(a, b):
    return a - b


def _mul(a, b):
    return a * b


def _div(a, b):
    if b != 0:
        return a / b
    print("На ноль делить нельзя")


def _squ(a, b):
    return a ** b


def operation_mapper(operation):
    if operation == "+":
        return _add
    elif operation == "-":
        return _sub
    elif operation == "*":
        return _mul
    elif operation == "/":
        return _div
    elif operation == "**":
        return _squ


print(operation_mapper("*")(1, 2))  # выводит 2

# Функция operation_mapper это не декоратор, это функция высшего порядка по совместимости еще и
# фабрика функций которая возвращает опеределеную функцию в зависимости от заданых параметров


