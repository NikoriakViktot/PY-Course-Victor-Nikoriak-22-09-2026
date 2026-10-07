# AI log: використовувала для пояснень що краще використати для підрахунку
# oranges = 48
# total = 117

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

for subject in stock:
    total += stock[subject] * prices[subject]

print(total)

