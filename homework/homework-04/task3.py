# AI Log: використовувала AI, щоб зрозуміти, як знайти спільні числа, підсказав використати in
# фінальний код написано самостійно

import random

i = 0
first_list = []
second_list = []
while i < 10:
    i += 1
    first_list.append(random.randint(1, 10))
    second_list.append(random.randint(1, 10))

print(first_list)
print(second_list)
# Згенеровано
# [5, 5, 5, 3, 6, 5, 1, 2, 4, 5]
# [5, 3, 9, 4, 4, 3, 8, 5, 10, 10]
# Очікую: [5, 3, 4]
n = 0
third_list = []
while n < len(first_list):
    if first_list[n] in second_list and (first_list[n] not in third_list):
        third_list.append(first_list[n])

    n += 1

print(third_list)