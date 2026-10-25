# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді

def _add(a, b):
    return a + b

def _sub(a, b):
    return a - b

def _mul(a, b):
    return a * b

def _div(a, b):
    return a / b

def _pow(a, b):
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
        return _pow
    else:
        raise ValueError(f"Unknown operation: {operation}. Allowed: +, -, *, /, **")


if __name__ == "__main__":
    print(operation_mapper("+")(1, 2))
    print(operation_mapper("**")(2, 10))

    try:
        print(operation_mapper("%"))
    except ValueError as e:
        print("ValueError:", e)

    try:
        print(operation_mapper("/")(1, 0))
    except ZeroDivisionError as e:
        print("ZeroDivisionError:", e)


# для оператора, якого немає в нашомі списку раніше спрацьовувала умова else і тихо повертала None без помилки
# тепер функція буде виводити помилку ValueError з описом Unknown operation
# перевірка на ділення на 0 буде працювати вже у викликаній ф-ції