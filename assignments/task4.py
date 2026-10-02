import random
numbers = []
i = 0
while i < 10:
    # AttributeError: 'NoneType' object has no attribute 'append'
    # Bug: append() already adds the number to the list, so numbers = is not needed.
    numbers.append(random.randint(1, 5))
    i += 1
# AttributeError: 'list' object has no attribute 'add'
# Bug: add() is used with a set, not a list. A set also stores only unique values.
unique_numbers = set()
i = 0
while i < len(numbers):
    unique_numbers.add(numbers[i])
    i += 1
print("All numbers:", numbers)
print("Unique numbers:", unique_numbers)