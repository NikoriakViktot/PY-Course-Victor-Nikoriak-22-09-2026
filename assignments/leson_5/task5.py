numbers = [" "] * 9
player = "x"
winning_combinations = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 4, 8),
    (2, 4, 6),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8)
    ]
game_over = False
moves = 0

while not game_over:
    choice = input("Выбери клетку от 1 до 9:")

    if not choice.isdigit():
        print("Нужно ввести число от 1 до 9.")
        continue

    choice = int(choice)
    choice = choice - 1

    if choice <0 or choice > 8:
        print("Выбери число от 1 до 9.")
        continue

    if numbers[choice] != " ":
        print("Эта клетка уже занята!")
        continue

    numbers[choice] = player
    print(numbers[0], "|", numbers[1], "|", numbers[2])
    print("---------")
    print(numbers[3], "|", numbers[4], "|", numbers[5])
    print("---------")
    print(numbers[6], "|", numbers[7], "|", numbers[8])

    win_index = 0
    winner = False

    while win_index < len(winning_combinations):
        combination = winning_combinations[win_index]

        if numbers[combination[0]] == player and numbers[combination[1]] == player and numbers[combination[2]] == player:
            winner = True

        win_index += 1

    if winner:
        print("Победил", player)
        game_over = True

    elif moves == 9:
                print("Ничья!")

    else:
        if player == "x":
            player = "0"
        else:
            player = "x"
# AI log:
#  До 12 строки разбирал и писал код самостоятельно, всё было понятно.
#  В процессе попросил AI помочь написать оставшуюся часть кода,
#  после чего возникло много ошибок в синтаксисе и отступах.
#  Ошибки разбирали и исправляли постепенно, некоторые и сам находил
#  Это было самое долгое и сложное для меня задание.