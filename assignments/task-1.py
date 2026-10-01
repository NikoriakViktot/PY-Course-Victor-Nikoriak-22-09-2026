#Task 1

#AI log: Not used

# Добавил try-except что бы не было ошибки если вводишь значение float или string

try:
    number = int(input("Если число будет четное то выведет True, если нет выведет False\n"
                       "Введите число: "))

    if number % 2 == 0:
        is_even = True
    else:
        is_even = False

    print(is_even)

except ValueError:
    print("Число должно быть цельным и не должно быть букв")


