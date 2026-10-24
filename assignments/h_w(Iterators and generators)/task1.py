# AI log: я попросила ШІ пояснити, чому результати двох викликів print() відрізняються
def with_index(iterable, start = 0):
    i = start
    for j in iterable:
        yield (i, j)
        i += 1

# print(with_index("abc", 1)) виведе представлення самого генератора
# print(list(with_index("abc", 1))) виведе список з усіма парами
# результати відрізняються, тому що list() перебирає генератор і збирає його значення

print(with_index("abc", 1))
print(list(with_index("abc", 1)))