import random
import random_text

print(random.randint(1, 6))

# this is my random
# Traceback (most recent call last):
#   File "/Users/rostyslav/beetroot_homework/homework-import/random_experiments/game.py", line 3, in <module>
#     print(random.randint(1, 6))
#           ^^^^^^^^^^^^^^
# AttributeError: module 'random' has no attribute 'randint' (consider renaming '/Users/rostyslav/beetroot_homework/homework-import/random_experiments/random.py' since it has the same name as the standard library module named 'random' and prevents importing that standard library module)


# Проблему решила переименовка файла random в random_text
# Ошибка была в том что python находил модуль random но в нем не было метода radint