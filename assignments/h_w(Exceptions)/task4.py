# AI log: розібралася, чому невідому операцію потрібно обробляти через ValueError
# а помилку ділення на нуль- під час виконання повернутої функції
def operation_mapper(oper):
    def operation(a, b):
        if oper == "+":
            return a + b
        elif oper == "-":
            return a - b
        elif oper == "/":
            return a / b
        elif oper == "*":
            return a * b
        elif oper == "**":
            return a ** b
        else:
            raise ValueError(f"Unknown operation: {oper}")
    return operation

print(operation_mapper("+")(1, 2))
print(operation_mapper("/")(7, 2))
print(operation_mapper("**")(2, 10))
# KeyError виник би через відсутній ключа у словнику
# a ValueError ми викликаємо, щоб повідомити про непідтримувану операцію
try:
    print(operation_mapper("%"))
except ValueError as e:
    print(e)
# operation_mapper тільки обирає операцію
# а аргументи a і b отримує функція operation яка виконує ділення
try:
    print(operation_mapper("/")(1, 0))
except ZeroDivisionError as z:
    print(z)
