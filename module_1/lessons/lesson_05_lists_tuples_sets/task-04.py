#Task 4

#AI log: Not used

import random

numbers = []
i = 0
while i < 10:
    numbers.append(random.randint(1, 5))
    i += 1

unique_numbers = []
# Проблема было в том что создавался словарь где формат хранения ключ-пара
i = 0
while i < len(numbers):
    if numbers[i] not in unique_numbers:
        unique_numbers.append(numbers[i])
    i += 1

# В цикле же не хватало проверки для установления уникального числа, а также был использовал метод add
# которого в принципе не существует, он был изменен на метод append который подходит для работы с этим типом данных

print("All numbers:", numbers)
print("Unique numbers:", unique_numbers)

# AttributeError: 'NoneType' object has no attribute 'append'
# AttributeError: 'dict' object has no attribute 'add'