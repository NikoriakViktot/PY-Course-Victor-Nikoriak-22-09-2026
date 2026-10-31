import sys

print(sys.path)

# Первый елемент sys.path - это путь к директории этого проекта
# Потому Python может импортировать модули из этой папки

# import prices

# При import prices когда она лежит в другой папке мы получим ошибку


sys.path.append(
    "/Users/rostyslav/beetroot_homework/homework-import/extra_modules"
)

import prices


print(prices.with_discount(100, 15))

# После запуска данной програмы мы получили нормальный вывод который нам был и нужен
# Добавление в список нового пути должен происходится до самого импорта потому что импорт должен проходится уже по новому списку
