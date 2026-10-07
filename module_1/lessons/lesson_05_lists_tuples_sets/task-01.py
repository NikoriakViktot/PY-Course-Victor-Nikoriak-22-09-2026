import random

#Task 1

#AI log: Not used

numbers = []

i = 0

while i < 10:
    numbers.append(random.randint(1, 100))
    i+=1

i = 0
max_number = 0

while i < len(numbers):
    if numbers[i] > max_number:
        max_number = numbers[i]
    i+=1


print(max_number)
print(max(numbers))
