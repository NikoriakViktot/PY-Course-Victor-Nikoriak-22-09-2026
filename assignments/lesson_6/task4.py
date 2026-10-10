# Результат: {'я': 2, 'люблю': 1, 'python': 2, 'меня': 1, 'зовут': 1, 'саша': 1, 'и': 1, 'пришел': 1, 'учиться': 1}
sentence = "Я люблю Python меня зовут Саша и я пришел учиться Python"
words = sentence.split()
counts = {}
for word in words:
    word = word.lower()
    if word in counts:
        counts[word] = counts[word] + 1
    else:
        counts[word] = 1
print(counts)
# AI log :С помощью Ai разбирал код,код писал сам
