# operation_mapper(«/»)(7, 2) - поверне 7/2 = 3.5
# operation_mapper(«**»)(2, 10) - поверне 2 піднесене до 10 = 1024

# operation_mapper не э декоратором, а замикачем, бо він приймає оператор, а не функцію, а повертає виконання функції


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


print(operation_mapper('+')(1, 2))      # 3
print(operation_mapper('/')(7, 2))      # 3.5
print(operation_mapper('**')(2, 10))    # 1024

# AI log: Самостійно написав структуру фабрики функцій.
# З ментором(AI) розібрали концепцію: чому це замикання, а не декоратор (приймає рядок, а не функцію).
