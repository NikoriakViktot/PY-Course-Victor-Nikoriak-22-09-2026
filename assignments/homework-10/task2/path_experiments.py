# першим елементом цього списку є поточна тека в якій знаходиться виконуваний файл, бо першим чином при пошуці пайтон обирає цей варіант
# ['d:\\VisualStudioProject\\BeetRoot Academy\\lesson 10 modules\\homework-10', 'C:\\Users\\mwfgo\\AppData\\Local\\Python\\pythoncore-3.14-64\\python314.zip', 'C:\\Users\\mwfgo\\AppData\\Local\\Python\\pythoncore-3.14-64\\DLLs', 'C:\\Users\\mwfgo\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib', 'C:\\Users\\mwfgo\\AppData\\Local\\Python\\bin', 'C:\\Users\\mwfgo\\AppData\\Local\\Python\\pythoncore-3.14-64', 'C:\\Users\\mwfgo\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages']

# Чи можна змінити його зсередини Python?
# так можна, він працює як простий лист, його можна змінювати, наприклад sys.path[0], sys.path.append('')

# Якщо так, чи впливає це на те, де Python шукає файли модулів?
# так впливає, адже перший елемент є текою виконуваного файлу, змінивши його пайтон не зможе найти ті файли, які були в теці з виконуваним файлом

# пересістив файл prices в іншу папку, при його імпортуванні отримав помилку ModuleNotFoundError: No module named 'prices'
# додавши шлях до цієї папки через sys.path.append(), все знову запрацювало

import sys

print(sys.path)
print('\n')
print(sys.path[0])

# AI log: none
