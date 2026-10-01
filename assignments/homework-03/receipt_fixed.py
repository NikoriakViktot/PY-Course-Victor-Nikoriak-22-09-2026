# AI log: none

# TypeError: 'str' object is not callable
# не можна використовувати назви змінних, які вже є частиною Python (str, int, print)
# замінюємо str на str1
str1 = "receipt"
item = "coffee"
price = "45.5"
quantity = 3

# метод не зберігається в змінну, тому вона не застосувалась
# присвоємо використання методу до змінної
item = item.upper()

# TypeError: can only concatenate str (not "int") to str
# не можна конкетувати строчний(str) тип даних та числовий(int)
# переводимо змінну quantity з int в str
print("Item: " + item + ", quantity: " + str(quantity))

# щоб не отримати виведення рядку price три рази, треба перевести price в float(чому не int, бо це число не ціле, а десяткове)
total = float(price) * quantity

# не можна конкетувати строчний тип даних та числовий
# переводимо змінну total з числа(int) в строку(str)
print("Total: " + str(total) + " UAH")

# TypeError: unsupported operand type(s) for /: 'str' and 'int'
# не можна виконувати математичні дії між строкою(str) та числом(int)
print(f"Average: {total / quantity:.2f}")
