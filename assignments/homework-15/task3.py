# AI log: обговорив як краще оптимізувати код (прибрати зайві цикли, яке краще рішення обрати), обговорив складність ф-цій (довели, що це O(n)),
# допомагав мені реалізувати правильно консольне меню (тут були проблеми з if/else).

# для початку сама ф-ція caesar має складність O(n), бо має один цикл for, цикл in фіксований(константа),
# ф-ція crack вже має певну к-ть циклів, це 0(1), але при виклику caesar вона стане O(n)

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def caesar(text='Цезарь', shift=2, action=1):
    result = ""

    if action == 2:  # action = 1 (шифрування), action = 2 (розшифрування)
        shift = -shift

    for ch in text:

        if ch.isupper() and ch.lower() in ALPHABET:
            position = (ALPHABET.index(ch.lower()) + shift) % 26
            result += ALPHABET[position].upper()

        elif ch in ALPHABET:
            position = (ALPHABET.index(ch) + shift) % 26
            result += ALPHABET[position]

        else:
            result += ch

    return result


def crack(text):  # підбір слова
    for i in range(len(ALPHABET)):
        print(f"Підбір слова: {caesar(text, i, 2)}, крок зсуву {i}")


def start_program(text=None, shift=None, action=None):
    """Програма для шифрування/дешифрування слів"""

    try:

        if action is None:
            action = int(input("Введіть дію (1 - шифрування, 2 - дешифрування, 4 - підбір): "))

        if action == 4:
            if text is None:
                text = input("Введіть слово для підбору: ")
            crack(text)
            return

        else:

            if text is None:
                text = input("Введіть слово для шифрування: ")

            if shift is None:
                try:
                    shift = int(input("Введіть число на яке літера буде зсуватися: "))

                except ValueError:
                    print("Введіть число!")
                    return

    except ValueError:
        print("Помилка, ведіть дію (1 - шифрування, 2 - дешифрування, 4 - підбір)")
        return

    print(f"Ваше зашифроване/дешифроване слово: {caesar(text, shift, action)}")


start_program("Brother it`s important, password Jackie Chan", 5, 1)

start_program(text="Gwtymjw ny`x nrutwyfsy, ufxxbtwi Ofhpnj Hmfs", action=4)
