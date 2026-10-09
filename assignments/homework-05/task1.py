# Trace:
# i = 0: поточне число 5, max_value = 5
# i = 1: поточне число 9, 9 > 5, тому max_value оновлюється до 9
# i = 2: поточне число 10, 10 > 9, тому max_value оновлюється до 10
# i = 3: поточне число 1, 1 не більше 10, тому max_value залишається 10

import random

numbers = []

i = 0

while i < 10:
    numbers.append(random.randint(0, 10))
    i += 1

max_value = numbers[0]

print(numbers)

i = 0

while i < len(numbers):

    if numbers[i] > max_value:
        max_value = numbers[i]

    i += 1

print(max_value)
print(max(numbers))

# AI log: довго боровся з логікою задачі. Розібрався, що range() не створює список сам по собі,
# і зрозумів, чому програма падала через неправильні умови циклу.
# Після розбору з ментором, самостійно виправив код і зібрав правильну логіку.
# Ментор AI (лише наштовхує мене на рішення, але не пише код за мене)
