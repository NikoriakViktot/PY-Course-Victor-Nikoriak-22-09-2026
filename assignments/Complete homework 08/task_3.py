# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді
def even_squares(numbers):
    for n in numbers:
        if n % 2 == 0:
            yield n * n

evens = even_squares(range(10))
print(list(evens))

#на перший погляд помилок в коді не бачу
# Bug: TypeError: 'int' object is not iterable
#функція не ітерувалася, одразу повернула 0, тому замінила return на yield

squares = [n * n for n in range(5)]
print(max(squares))

print(sum(squares))

#генератор можна пройти один раз, повторно пройти його не можна, тому другий print (sum) не працює
# Bug: треба генератор замінити на список [], який збереже усі значення