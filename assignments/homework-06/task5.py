# cart краще зробити словником, він дозволяє легко оновлювати кількість за ключем,
# через список це буде робити не зручно, а також словник це робить дуже швидко

stock = {
    "banana": 6,
    "apple": 0,
    "orange": 32,
    "pear": 15,
    "strawberry": 20,
    "mango": 5,
    "plums": 7
}

prices = {
    "banana": 4,
    "apple": 2,
    "orange": 1.5,
    "pear": 3,
    "strawberry": 5,
    "mango": 6,
    "plums": 3
}

input_item = None
cart = {}

while True:

    input_item = input("Введіть товар: ")

    if input_item == "готово" or input_item == "done":
        break

    if input_item == "чек" or input_item == "receipt":
        break

    if input_item not in stock.keys():
        print("Введіть правильний товар")
        continue

    input_amount = int(input("Введіть кількість товару: "))

    if input_amount > stock[input_item]:
        print("Даного товару немає в даній кількості або він відсутній")
        continue

    stock[input_item] -= input_amount
    cart[input_item] = input_amount

for item, amount in cart.items():
    print(
        f"Ваш чек: товар {item}, кількість {amount}, ціна {prices[item]}, собівартість {prices[item] * 0.7}. Загальна сумма: {prices[item]*amount}")

print(f"Товари яких немає в наявності: {[item for item, amount in stock.items() if amount == 0]}")

# AI log: Це завдання виявилося складним і потребувало значної серії підказок від ментора(AI).
# 1. Порядок виконання: спочатку я запитував кількість товару до того, як перевіряв команду виходу ("done") та наявність товару на складі.
# 2. Словники: замінив помилковий перезапис cart = {...} на правильне оновлення за ключем cart[item] = amount.
# 3. KeyError у чеку: зрозумів проблему області видимості — використовував глобальну змінну (input_item) замість локальної змінної циклу (item).
# 4. List comprehension: виправив синтаксис (додав квадратні дужки та замінив присвоєння '=' на порівняння '==').
# Механіка роботи словників та циклів стала зрозумілішою.
