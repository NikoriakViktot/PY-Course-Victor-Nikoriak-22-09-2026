import random
numbers = []
count = 0
while count < 10:
    number =random.randint(1, 100)
    numbers.append(number)
    count = count + 1
print(numbers)
current_max = numbers[0]
index = 1
while index < len(numbers):
    number = numbers[index]
    if number > current_max:
        current_max = number
    index = index + 1
print(current_max)
print(max(numbers))
# Trace:
# #1:33
# #2 :41
# #3 :41
# Al log: c помощью AI разбирал задание и пошагово вводил код.
# Мне не понравился такой способ работы.По этому мы разобрали каждую строку поэтапно,
# чтобы мне хоть чуть-чуть стало понятно.