#AI log: Використала AI для підказки:
# 1. Попросила підказати загальну логіку гри та які основні частини повинні бути.
# 2. Попросила підказати, як організувати завершення гри після перемоги або нічиєї.
# 3. Попросила пояснити, як працюють winning_lines[i][0], [1] та [2] для доступу до клітинок ігрового поля.
winning_lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                 (0, 3, 6),(1, 4, 7), (2, 5, 8),
                 (0, 4, 8), (2, 4, 6)]

play_board = [" ", " ", " ", " ", " ", " ", " ", " ", " "]

game_over = False
while not game_over:

    player_number_1 = int(input("Введіть номер гравця 1: "))
    while (1 > player_number_1 or player_number_1 > 9) or play_board[player_number_1 - 1] != " ":
        print("Введіть інше число")
        player_number_1 = int(input("Введіть номер гравця 1: "))

    play_board[player_number_1 - 1] = "X"
    print(play_board[0:3])
    print(play_board[3:6])
    print(play_board[6:9])

    i = 0
    while i < len(winning_lines):
        if play_board[winning_lines[i][0]] == "X" and play_board[winning_lines[i][1]] == "X" and play_board[winning_lines[i][2]] == "X":
            print("Перемога! Гравець 1!")
            game_over = True
            break
        i += 1

    if game_over:
        break
    elif " " not in play_board:
        print("Нічия!")
        break

    player_number_2 = int(input("Введіть номер гравця 2: "))
    while (1 > player_number_2 or player_number_2 > 9) or play_board[player_number_2 - 1] != " ":
        print("Введіть інше число")
        player_number_2 = int(input("Введіть номер гравця 2: "))

    play_board[player_number_2 - 1] = "O"
    print(play_board[0:3])
    print(play_board[3:6])
    print(play_board[6:9])

    i = 0
    while i < len(winning_lines):
        if play_board[winning_lines[i][0]] == "O" and play_board[winning_lines[i][1]] == "O" and play_board[winning_lines[i][2]] == "O":
            print("Перемога! Гравець 2!")
            game_over = True
            break
        i += 1

    if game_over:
        break
    elif " " not in play_board:
        print("Нічия!")
        break

# play_board - list, тому що під час гри нам потрібна можливість змінювати значення окремих клітинок
# winning_lines - tuples, тому що це фіксовані значення і під час гри ми їх не змінюємо
