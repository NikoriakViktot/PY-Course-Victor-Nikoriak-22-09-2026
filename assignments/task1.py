import random
numbers = []
i = 0
while i < 10:
    n = random.randint(1, 10)
    numbers.append(n)
    i = i + 1

print(numbers)
max_num = numbers[0]
j = 1
while j < len(numbers):
    if numbers[j] > max_num:
        max_num = numbers[j]
    j = j + 1
print("Largest:", max_num)
print("Check with max():", max(numbers))