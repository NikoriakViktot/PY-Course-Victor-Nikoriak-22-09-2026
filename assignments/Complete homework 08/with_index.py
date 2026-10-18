# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді
def with_index(iterable, start=0):
    for n in iterable:
      yield (start, n)
      start += 1

iterable = ['Lena', 'Alina', 'Natasha']
print(list(with_index(iterable)))

print(with_index("abc", 1))
#прогноз - [(1, 'a'), (2, 'b'), (3, 'c')]
#реально видало: <generator object with_index at 0x781884bdde50>
#тому що треба було загорнути в list
print(list(with_index("abc", 1)))
#ось так вже видало як прогнозувалося