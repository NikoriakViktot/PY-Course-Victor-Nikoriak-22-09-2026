# Task 5

# AI log: Not used


stocks = {
    "banana": 6,
    "apple": 0,
    "orange": 32,
    "pear": 15,
    "watermelon": 10,
    "guava": 7
}

prices = {
    "banana": 4,
    "apple": 2,
    "orange": 1.5,
    "pear": 3,
    "watermelon": 6,
    "guava": 9
}

End_of_shopping = False
all_price= 0
check = {}



while True:
    print("Вот товар который есть в наличии:")
    for name, stock in stocks.items():
        print(name, "—", stock, "шт")
    while True:
        while True:
            name_fruit = input("Введите название товара который вам нужен:").lower()
            if stocks[name_fruit] == 0:
                print("Товара нет в наличии!")
                continue
            elif name_fruit not in stocks:
                print("такого товара нет на складе")
                continue
            else:
                check[name_fruit] = 0
                break
        while True:
            try:
                stock_fruits = int(input("Введите количество которое вам нужно:"))
                if stock_fruits > stocks[name_fruit]:
                    print("Такого количества нет на складе")
                    continue
                else:
                    check[name_fruit] = stock_fruits
                    stocks[name_fruit] -= stock_fruits
                    break
            except ValueError:
                print("Введенно неверное значение!")
        while True:
            done_buy = input("Это все?(Yes/No)").lower()
            if done_buy == "yes":
                End_of_shopping = True
                break
            elif done_buy == "no":
                break
            else:
                print("Повторите ввод")
        if End_of_shopping:
            break
        else:
            continue
    if End_of_shopping:
        break

for name, stock in check.items():
    all_price+=prices[name]*stock
    print(name, "—", stock, "шт", "Цена:",(prices[name]*stock))

print(f"Общая сума чека: {all_price}")

print("Осталось на складе:")
for name, stock in stocks.items():
    print(name, "—", stock, "шт")