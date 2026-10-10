numbers = [(i, i ** 2) for i in range(1, 11)]
print(numbers)
numbers_for = []
for i in range(1, 11):
    numbers_for.append((i, i ** 2))
print(numbers_for)
# Al log : Верси 1 с comprehension удобней
# Версия 2 с for и append легче понять по шагам.
# Сначала я подумал что for нужно вводить каждую пару,но это происходит автоматически
# C помощью Ai разбирал задание и писал код маиостоятельно.