#AI log: none
import random

numbers = []
i = 0
while i < 10:
    # AttributeError: 'NoneType' object has no attribute 'append'
    # append вже додає число в список, не потрібно ще раз присвоювати в numbers
    numbers.append(random.randint(1, 5))
    i += 1

unique_numbers = set()
i = 0
while i < len(numbers):
    #AttributeError: 'dict' object has no attribute 'add'
    # unique_numbers = {} має тип даних dict, а словник не має методу 'add' тому змінюємо dict на set
    unique_numbers.add(numbers[i])
    i += 1

print("All numbers:", numbers)
print("Unique numbers:", unique_numbers)