# Task 1

# AI log: Not used

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

all_price = 0

for item in prices.keys():
    all_price += prices[item] * stock[item]

print(f"Общая стоимость продуктов на складе: {all_price}")
