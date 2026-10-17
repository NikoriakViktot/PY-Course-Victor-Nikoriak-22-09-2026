# AI log: попросила пояснити використання `raise` всередині `except`

def total_of(numbers):
    total = 0
    for n in numbers:
        try:
            total += n # nubmer не вірно вказано імʼя змінної перебору зі списку
            # name 'nubmer' is not defined

        except NameError as m: # з pass програма приховує помилку та повертає неправильний результат
                               # тому вловлюємо помилку NameError
            print(m)
            raise
    return total

numbers = [1, 2, 3]
print(total_of(numbers))

# Якщо під час обробки 10 000 записів приховувати помилки
# програма може повернути неправильний результат, а ми не помітимo

