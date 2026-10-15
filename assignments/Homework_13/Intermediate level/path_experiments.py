import sys

print(sys.path)
# Першим елементом є 'C:\\Users\\Admin\\Desktop', тому що це тека самого скрипта

sys.path.append("C:\\Users\\Admin\\Desktop\\secret_folder")
import prices
# Спочатку вилізла помилка (ModuleNotFoundError: No module named 'prices'), після зміни sys.path помилка зникла. Це відбулось через те що Python не міг знайти теку зі скриптом бо вона не знаходилась пору і не була вбудованим модулем

# AI log: no AI