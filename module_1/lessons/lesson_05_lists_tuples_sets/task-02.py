#Task 2
import random

#AI log: not used

numbers = []
number_output = []
i=1

while i <= 100:
    numbers.append(i)
    i+=1

i = 0

while i < len(numbers):
    if numbers[i] % 7 == 0:
        if numbers[i] % 5 != 0:
            number_output.append(numbers[i])
    i+=1

print(number_output)
