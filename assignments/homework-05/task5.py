# до списку можна звертатись через індекс, він змінюваний, має методи зміни
# виграшна лінія кортежі, тому що вони не змінювані, їх не змінити, а лише перепризначити змінну

score = [" ", " ", " ",
         " ", " ", " ",
         " ", " ", " "]

winning_lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                 (0, 3, 6), (1, 4, 7), (2, 5, 8),
                 (0, 4, 8), (2, 4, 6)]


print(winning_lines[1])

is_winner = False

i = 0

t = '-' * 15

while i < len(score):

    print(t)

    move_number = i + 1
    print(f"Хід номер: {move_number}")

    print(t)

    print(score[:3])
    print(score[3:6])
    print(score[6:])

    print(t)

    square_input = int(input("Введіть ваше значення (1-9): "))
    square = square_input - 1

    if square_input > 9 or square_input < 1:
        print("Введено неправильне значення")
        continue

    if score[square] != " ":
        print("Ця клітинка вже була використана")
        continue

    if move_number % 2 == 0:
        score[square] = 'O'

    else:
        score[square] = 'X'

    j = 0

    while j < len(winning_lines):

        line = winning_lines[j]

        if score[line[0]] == score[line[1]] == score[line[2]] != " ":

            print(t)

            print(score[:3])
            print(score[3:6])
            print(score[6:])

            print(t)

            print("Перемога")

            is_winner = True

        j += 1

    if is_winner:
        break

    i += 1

if not is_winner:
    print(t)
    print("Нічия")

print(t)
print('ГРА ЗАВЕРШЕНА')
print(t)

# AI log: видалось доволі складне завдання, було багато запитань до ментора.
# Не міг сам придумати як мені реалізувати порівняння виграшних та реальних ходів, і в якому місці ставити певні блоки коду.
# Написав код, і потім ще раз його перезаписав з нуля, щоб закріпити, але знову були деякі запитання до ментора.
# Ментор AI (лише наштовхує мене на рішення, але не пише код за мене)
