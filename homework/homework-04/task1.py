#AI log: none
import random
numbers = []

while len(numbers) < 10:
    numbers.append(random.randint(1, 10))
print(f"Our list: {numbers}")

number_max = numbers[0]

i = 0
while i < 10:
    if numbers[i] > number_max:
        number_max = numbers[i]
    i += 1
print(f"Max number: {number_max}")
print(max(numbers))