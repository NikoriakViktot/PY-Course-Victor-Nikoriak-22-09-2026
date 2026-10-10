import random

numbers = []
i = 0
while i < 10:
    # Bug 1: append изменяет список  ,поэтому numbers = здесь лишнее.
    # Было: numbers = numbers.append(random.randint(1,5))
    numbers.append(random.randint(1, 5))
    i += 1
#Bug 2: {} создает словарь,а для Add() нужно множество set()
#Было: unique_numbers = {}
unique_numbers = set()
i = 0
while i < len(numbers):
    unique_numbers.add(numbers[i])
    i += 1

print("All numbers:", numbers)
print("Unique numbers:", unique_numbers)
# Bug 1: Ошибка : AttributeError: 'NoneType' object has no attribute 'append'
# Bug 2: Ошибка : AttributeError: 'dict' object has no attribute 'add'
# AI log :С помощью AI разбирал ошибки в программе и исправлял их по очереди