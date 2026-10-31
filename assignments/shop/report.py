from extra_modules.prices import with_discount, total

prices = [1200, 899, 450]

new_prices = []

for price in prices:
    new_prices.append(with_discount(price, 15))

print(f"Новые цены: {new_prices}\nОбщий счет: {total(new_prices)}")
