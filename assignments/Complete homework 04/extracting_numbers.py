# Агент AI пояснив про перші три очікувані числа
# Перші три очікувані числа: 7, 14, 21
# 35 немає у списку, бо воно кратне і 7 і 5

numbers = []
i = 1
while i <= 100:
    numbers.append(i)
    i += 1

result = []
i = 0
while i < len(numbers):
    if numbers[i] % 7 == 0 and numbers[i] % 5 != 0:
        result.append(numbers[i])
    i += 1

print(result)