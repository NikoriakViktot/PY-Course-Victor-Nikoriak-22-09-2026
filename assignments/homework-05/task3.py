# [9, 7, 7, 1, 4, 6, 9, 4, 2, 4]
# [6, 2, 8, 4, 4, 3, 10, 8, 3, 8]

# Спільні числа 6, 2, 4

import random

i = 0

first_list = []
second_list = []
third_list = []

while i < 10:

    a = random.randint(1, 10)
    first_list.append(a)

    b = random.randint(1, 10)
    second_list.append(b)

    i += 1

j = 0

while j < len(first_list):

    a = first_list[j]

    if a in second_list and a not in third_list:
        third_list.append(a)

    j += 1

print(first_list)
print(second_list)
print(third_list)

# AI log: задача далася важко, довго не міг зрозуміти логіку пошуку елементів між двома списками.
# Основна проблема була у спробі зробити все в одному циклі while.
# Після розбору помилок в архітектурі закоментував старий код і переписав код циклів з нуля, щоб точно зрозуміти логіку.
# Виправив межі randint() та самостійно застосував комбінацію in та not in для уникнення дублікатів.
# Ментор AI (лише наштовхує мене на рішення, але не пише код за мене)
