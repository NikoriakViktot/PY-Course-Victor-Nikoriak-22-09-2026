# Task 3


# AI log: Not used

def make_operation(operation, *args):
    if not args:
        return "Нет чисел"
    answer = args[0]
    if operation == "+":
        for i in args[1:]:
            answer += i
    elif operation == "-":
        for i in args[1:]:
            answer -= i
    elif operation == "*":
        for i in args[1:]:
            answer *= i
    else:
        return "Неверный оператор"
    return answer


make_operation('-', 5, 5, -10, -20)
print(make_operation('*', 5, 5, -10, -20))
