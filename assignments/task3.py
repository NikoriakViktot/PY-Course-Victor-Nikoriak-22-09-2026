import random
first_list = []
second_list = []
result = []
i=0
while i < 10:
    first_list.append(random.randint(1,10))
    i=i+1
print(first_list)
i=0
while i < 10:
    second_list.append(random.randint(1,10))
    i=i+1
print(second_list)
i=0
while i < len(first_list):
    if first_list[i] in second_list and first_list[i] not in result:
        result.append(first_list[i])
    i = i + 1
print(result)
