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
# Перевірка додавання
print(make_operation("+", 7, 7, 2))
# Перевірка віднімання
print(make_operation("-", 5, 5, -10, -20))
# Перевірка множення
print(make_operation("*", 7, 6))
# Перед запуском передбачаємо результати:
# make_operation("-", 10) поверне 10.
# make_operation("*", 2, 0.5, 3) поверне 3.0.
print(make_operation("-", 10))
print(make_operation("*", 2, 0.5, 3))
# AI log: Попросив ШІ пояснити параметр *numbers,
# цикл for та виконання арифметичних операцій.
# Самостійно записав і перевірив код.