# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді
def math_func():
    try:
        a = float(input("Введіть a: "))
        b = float(input("Введіть b: "))
        return a**2 / b
    except ValueError:
        print("Помилка: потрібно ввести число")
    except ZeroDivisionError:
        print("Помилка: на нуль ділити не можна")

print(math_func())