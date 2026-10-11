# operation_mapper("/")(7, 2) поверне 3,5
# operation_mapper("**")(2, 10) поверне 1024
# operation_mapper не є декоратором, бо декоратор приймає функцію, а operation_mapper приймає звичайне значення


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
    if operation == '+':
        return _add
    elif operation == '-':
        return _sub
    elif operation == '*':
        return _mul
    elif operation == '/':
        return _div
    elif operation == '**':
        return _pow

print(operation_mapper("**")(2, 10))
print(operation_mapper("**")(3, 2))

# AI log: Попросив пояснити мені саму суть і логіку виконання цього завдання, код написав сам