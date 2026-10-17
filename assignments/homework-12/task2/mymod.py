# AI log: за допомогою ментора(AI) розібрав причину PermissionError та роботу з відносними шляхами,
# самостійно оптимізував логіку підрахунку символів (прибрав зайвий цикл),
# дізнався про підрахунком символів у Python (len) та байтів у терміналі (wc).

def count_lines(name):

    with open(name, encoding='utf-8') as f:
        return len(f.readlines())


def count_chars(name):

    with open(name, encoding='utf-8') as f:
        return len(f.read())


def test(name):

    count = count_lines(name)
    print(f"Кількість рядків: {count}")

    count = count_chars(name)
    print(f"Загальна кількість символів: {count}")


if __name__ == '__main__':

    test('myfile.txt')  # Кількість рядків: 20 Загальна кількість символів: 494
    test('mymod.py')    # Кількість рядків: 41 Загальна кількість символів: 1261
    # $ wc -l -c mymod.py 41 1792 mymod.py
