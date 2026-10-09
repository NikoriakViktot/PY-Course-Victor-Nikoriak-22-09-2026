# Помилка 1:
# помилка в тому, що метод .append повертає NoneType, якщо його визивати не для змінення наявного списку,
# а для присвоєння змінній в нашому випадку
# AttributeError: 'NoneType' object has no attribute 'append'

# Помилка 2:
# помилка в тому, що ми створили словник (dict), а не множина (set), і словник не має таких методів, які має масив,
# і щоб отримати set, треба написати set()
# AttributeError: 'dict' object has no attribute 'add'

import random

numbers = []
i = 0

while i < 10:
    numbers.append(random.randint(1, 5))
    i += 1

unique_numbers = set()
i = 0

while i < len(numbers):
    unique_numbers.add(numbers[i])
    i += 1

print("All numbers:", numbers)
print("Unique numbers:", unique_numbers)

# AI log: самостійно знайшов та виправив обидві помилки в коді.
# Після цього звернувся до ментора для перевірки свого рішення.
# Ментор підтвердив логіку і порадив оптимізацію синтаксису: не створювати
# порожній словник для перетворення set({}), а одразу ініціалізувати множину як set().
# Ментор AI (лише наштовхує мене на рішення, але не пише код за мене)
