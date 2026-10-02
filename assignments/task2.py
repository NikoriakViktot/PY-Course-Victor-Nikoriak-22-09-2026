# Expected first three numbers: 7, 14, 21
# 35 is not included because it is divisible by 5.
numbers = []
result = []
i = 1
while i <= 100:
    numbers.append(i)
    if i % 7==0 and i % 5 !=0:
        result.append(i)
    i = i + 1


print(numbers)
print(result)