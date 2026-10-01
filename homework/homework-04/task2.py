#AI log: none
i = 0
numbers = list(range(1,101))
new_list = []
while i < len(numbers):
    if numbers[i] % 7 == 0 and not numbers[i] % 5 == 0:
        new_list.append(numbers[i])
    i += 1

print(new_list)
# 35 не входить тому, що кратне 5


