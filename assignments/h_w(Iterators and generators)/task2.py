# AI log:# порівняння з range(), обидві функції створюють послідовність чисел,
# вбудована list(range(5, 1)) повертає порожню послідовність [], тому я хотіла доповнити
# in_range, щоб вона автоматично обирала напрямок рахунку, якщо step не вказано
# так функція може рахувати назад коли start > end
# також я додала перевірку, щоб step не дорівнював 0.

# просила ШІ давати підказки, як реалізувати умови, що я хотіла
# щодо умов рахунку при start > end та як розділити логіку всіх перевірок
def in_range(start, end, step = None):
    if step == 0:
        raise ValueError("step cannot be zero")
    if step is None:
        if start > end:
            step = -1
        else:
            step = 1

    if start < end:
        i = start
        while i < end:
            yield i
            i += step
    elif start > end:
        i = start
        while i > end:
            yield i
            i -= abs(step)


print(list(in_range(5, 1, 2)))
print(list(in_range(2, 7)))
print(list(in_range(10, 0, -3)))
print(list(in_range(5, 1)))
print(list(in_range(2, 7, 0)))





