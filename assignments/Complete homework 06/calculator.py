# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні, також для пояснення помилок в коді
def make_operation(operator, *numbers):
    result = numbers[0]
    for number in numbers[1:]:
        if operator == "+":
            result += number
        elif operator == "-":
            result -= number
        elif operator == "*":
            result *= number
    return result

print(make_operation('+', 7, 7, 2))
# 16
print(make_operation('-', 5, 5, -10, -20))
# 30
print(make_operation('*', 7, 6))
# 42
print(make_operation('-', 10))
# поверне 10, бо відсутні інші аргументи, перший запишеться одразу в result і функція його поверне
print(make_operation('*', 2, 0.5, 3))
# поверне 3.0, бо один з аргументів був float