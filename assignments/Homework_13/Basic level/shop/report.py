# python prices.py вивів 80.0
#                        1715

# python report.py вивів [1020.0, 764.15, 382.5]
#                        2166.65
# Різне вони вивели, бо перший файл просто створює функції і знизу я тестив свої значення, а другий файл імпортує функції з першого і в них я тестив значення із завдання
# блок if __name__ == "__main__": із файлу prices.py при запуску report.py не виконається, бо при імпорті name вже не main а prices
# при запуску репорт я побачив тільки виконання того коду який я там написав, те що було в prices не відпрінтувалось


from prices import with_discount, total

original_prices = [1200, 899, 450]

my_list = [with_discount(i, 15) for i in original_prices]

print(my_list)

print(total(my_list))

# AI log: no AI
