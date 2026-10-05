import random
first_list = []
i = 0
while i < 10:
    first_list.append(random.randint(1, 10))
    i += 1

second_list = []
x = 0
while x < 10:
    second_list.append(random.randint(1, 10))
    x += 1

print(first_list)
print(second_list)

third_list = []
y = 0
while y < len(first_list):
    a = first_list[y]
    if a in second_list and a not in third_list:
        third_list.append(a)
    y += 1
print("Common: ", third_list)

# 1 - [2, 3, 4, 1, 10, 3, 8, 4, 2, 2]
# 2 - [7, 7, 6, 3, 4, 7, 3, 2, 2, 3]
# 3 - [2, 4, 3]
# вивело - [2, 3, 4]