# Агент AI пояснив помилки, не могла розібратися
import random

numbers = []
i = 0
while i < 10:
    numbers = numbers.append(random.randint(1, 5))
    i += 1

unique_numbers = set()
i = 0
while i < len(numbers):
    unique_numbers.add(numbers[i])
    i += 1

print("All numbers:", numbers)
print("Unique numbers:", unique_numbers)

# 1: AttributeError: 'NoneType' object has no attribute 'append'
# прибрала присвоєння в циклі
# 2: AttributeError: 'dict' object has no attribute 'add'
# У словника немає методу add(), тому треба set()