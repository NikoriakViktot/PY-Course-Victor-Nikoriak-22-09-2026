# Al log:I asked AI to explain the task and guide me step by step.I code myself
item = "coffee"
price = 45.5
quantity = 3

item = item.upper()
print(f"Item: {item}, quantity: {quantity}")

total = price * quantity
print(f"Total: {total} UAH")
print(f"Average: {total / quantity:.2f}")

# 1. str- удалил эту строку
# 2. item.upper()не сохранял результат
# 3. quantity-число,а его соединяли с текстом через +
# 4. price = "45.5" ,был текстом
# 5. total- число,а его соединяли текстом через +