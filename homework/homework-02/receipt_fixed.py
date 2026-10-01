#AI log: none

receipt = "receipt"
item = "coffee"
price = "45.5"
quantity = 3

item = item.upper()
print("Item: " + item + ", quantity: " + str(quantity))

total = float(price) * quantity
print("Total: " + str(total) + " UAH")
print(f"Average: {total / quantity:.2f}")

# Помилки:
# line1: назва змінної str, як назва вбудованого типу даних у Python
# line6: тип даних str є незмінним, а метод upper() повертає новий рядок, тому значення змінної треба переприсвоїти
# line7: quantity - це число, а не можемо додавати строки до чисел, тому перетворюємо quantity на строку
# line9: price - є строкою, не можна множити строки на числа, тому перетворюємо на float
# line10: total - є числом, тому для поєднання його з str перетворюємо на строку
