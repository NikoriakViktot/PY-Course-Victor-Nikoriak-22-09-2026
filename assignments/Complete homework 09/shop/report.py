# AI log: Claude,використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді

from prices import with_discount, total

prices_list = [1200, 899, 450]
prices_list_discount_15 = []

for price in prices_list:
  prices_list_discount_15.append(with_discount(price, 15))

print(prices_list_discount_15)
print(total(prices_list_discount_15))

# prices.py вивів 75.0 і 1000 бо файл запущено "напряму"
# report.py вивів [1020.0, 764.15, 382.5] та 2166.65 (лише свої результати),
# його __name__ == "prices" і тестовий блок з prices.py не виконується
