# Апельсин стоят 48,общая сумма 117
stock = {
    "banana": 6,
    "apple": 0,
    "orange": 32,
    "pear": 15
}
prices = {
    "banana": 4,
    "apple": 2,
    "orange": 1.5,
    "pear": 3
}
total = 0
for product in stock:
    quantity = stock[product]
    price = prices[product]
    total += quantity * price
print(total)
# Al log : С помощью AI писал код,так же спрашивал что такое переменая total.
# Определил что total= используеться для накопления общей суммы
#Код вводил самостоятельно