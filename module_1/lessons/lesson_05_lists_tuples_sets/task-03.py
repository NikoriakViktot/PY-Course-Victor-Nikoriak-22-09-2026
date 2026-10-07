import random
#Task 3

#AI log:Not used

first_list = []
second_list = []
third_list = []

i = 0

while i < 10:
    first_list.append(random.randint(1,10))
    second_list.append(random.randint(1,10))
    i+=1

i = 0
b = 0
n = 0

while i < len(first_list):
    n = first_list[i]
    while b < len(second_list):
        if n == second_list[b]:
            if n not in third_list:
                third_list.append(n)
        b+=1
    b = 0
    i+=1

print(first_list)
print(second_list)
print(third_list)