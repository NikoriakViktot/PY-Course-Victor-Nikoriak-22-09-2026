import random

random.randint(1, 6)

#this is my random
#Traceback (most recent call last):
#  File "C:\Users\Admin\Desktop\DZ\game.py", line 3, in <module>
#    random.randint(1, 6)
#    ^^^^^^^^^^^^^^
#AttributeError: module 'random' has no attribute 'randint' (consider renaming 'C:\Users\Admin\Desktop\DZ\random.py' since it has the same name as the standard library module named 'random' and prevents importing that standard library module)

# Чому AttributeError а не ModuleNotFoundError? Бо я імпортував свій модуль який має ту ж назву що і вбудований, Python знайшов його першим і вбудований став недоступний. Тому модуль є, але атребутів у ньому таких немає звідси і помилка AttributeError

# AI log: no AI