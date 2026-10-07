# Task 5


# AI log: Not used

wins_round = ((0, 1, 2), (3, 4, 5), (6, 7, 8),
              (0, 3, 6), (1, 4, 7), (2, 5, 8),
              (0, 4, 8), (2, 4, 6))

moves = [" ", " ", " ", " ", " ", " ", " ", " ", " "]
win = False


while True:

    print(moves[0], "|", moves[1], "|", moves[2])
    print("--|---|--")
    print(moves[3], "|", moves[4], "|", moves[5])
    print("--|---|--")
    print(moves[6], "|", moves[7], "|", moves[8])

    tic = int(input("Куда походить X(цифра от 1 до 9):")) - 1
    if moves[tic] == " ":
        moves[tic] = "X"
    else:
        print("клетка уже занята")
        continue

    ti = 0
    while ti <= 7:
        a, b, c = wins_round[ti]
        if moves[a] == "X" and moves[b] == "X" and moves[c] == "X":
            print("Выиграли крестики")
            win = True
            break


        ti += 1

    if win: break
    if " " not in moves:
        print("Ничья")
        break

    print(moves[0], "|", moves[1], "|", moves[2])
    print("--|---|--")
    print(moves[3], "|", moves[4], "|", moves[5])
    print("--|---|--")
    print(moves[6], "|", moves[7], "|", moves[8])

    toe = int(input("Куда походить 0(цифра от 1 до 9):")) - 1
    if moves[toe] == " ":
        moves[toe] = "0"
    else:
        print("клетка уже занята")
        continue

    ti = 0
    while ti <= 7:
        a, b, c = wins_round[ti]
        if moves[a] == "0" and moves[b] == "0" and moves[c] == "0":
            print("Выиграли нолики")
            win = True
            break
        ti += 1
        if " " not in moves:
            draw = True

    if win: break
    if " " not in moves:
        print("Ничья")
        break