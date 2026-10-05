# Агент AI пояснив про .randint
import random
numbers = []
i = 0
while i < 10:
    numbers.append(random.randint(1, 25))
    i += 1
print("My list of numbers:", numbers)
max_number = numbers[0]
i = 1
while i < len(numbers):
    if numbers[i] > max_number:
        max_number = numbers[i]
    i += 1

print("My max number:", max_number)
print("Check max():", max(numbers))