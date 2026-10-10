import random
first_list = []
count = 0
while count <10:
    number = random.randint(1,10)
    first_list.append(number)
    count = count + 1
print(first_list)
second_list = []
count = 0
while count < 10:
    number = random.randint(1,10)
    second_list.append(number)
    count = count +1
print(second_list)
unique_list =[]
all_numbers = first_list + second_list
index = 0
while index < len(all_numbers):
    number = all_numbers[index]
    if number not in unique_list:
     unique_list.append(number)
    index = index + 1
print(unique_list)
# first_list = [1, 9, 4, 5, 4, 6, 9, 6, 10, 2]
# second_list = [4, 5, 9, 5, 4, 10, 2, 5, 6, 8]
# Ожидаем результат без дубликатов: 1, 9, 4, 5, 6, 10, 2, 8
# Al log: c помощью AI разбирал задание по шагам.
# Код писал сам, а когда  не пониал,AI помогал разобраться