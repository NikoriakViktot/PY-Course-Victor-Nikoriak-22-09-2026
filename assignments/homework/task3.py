# AI log: запитувала, як перебирати елементи, які передаються через *args
def make_operation(let, *numbers):
    result = numbers[0]
    for n in numbers[1:]:
        if let == "+":
            result += n
        elif let == "-":
            result -= n
        elif let == "*":
            result *= n
    return result

print(make_operation("+", 7, 7, 2))
print(make_operation("-", 5, 5, -10, -20))
print(make_operation("*", 7, 6))

print(make_operation("-", 10))
# Очікую виводу 10, тому що список починаючи з [1:] порожній
print(make_operation("*", 2, 0.5, 3))
# Очікую виводу 3, тому що 2 * 0.5 * 3 = 3