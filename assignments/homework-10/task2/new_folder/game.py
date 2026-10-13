import random1
import random

print(random.randint(1, 6))

# AttributeError: module 'random' has no attribute 'randint'
# (consider renaming 'd:\VisualStudioProject\BeetRoot Academy\lesson 10 modules\homework-10\task2\new_folder\random.py' since it has the same name as the standard library module named 'random' and prevents importing that standard library module)

# запустивши файл game.py, ми імпортували наш модуль random.py, який вивів текст(this is my random),потім ми звертаємось до цього модуля,
# і хочем визвати фунцію randint(), але отримуємо помилку, яка каже що модуль random не має функції randint,
# це через те що коли ми імпортуємо власний файл random, він перекриває стандартну бібліотеку random,
# щоб це виправити треба перейменувати наш модуль, щоб він не перекривав стандартний

# AI log: none
