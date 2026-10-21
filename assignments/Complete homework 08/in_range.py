# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді
def in_range(start, end, step=1):
    if step > 0:
      while start < end:
        yield start
        start += step
    elif step < 0:
      while start > end:
        yield start
        start += step
print(list(in_range(0, 10, 1)))
print(list(in_range(0, -10, -1)))

list(in_range(10, 0, -3))
#[10, 7, 4, 1]
list(in_range(5, 1))
#нічого не передасть ([]), тому що при перевірці start < end (при кроці за замовчуванням 1) - нічого не спрацює