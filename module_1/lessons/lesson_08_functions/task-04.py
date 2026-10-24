# Task 4

# AI log:Not used

import random

# Функция создания поля
def create_board(size):
    board = []
    for i in range(size):
        board.append(["*" for i in range(size)])
    return board

# Функция которая печатает поле
def print_board(board):
    print("   ", end="")
    for i in range(len(board)):
        print(i, end=" ")
    print(end="\n")
    for row in range(len(board)):
        print(row, end="  ")
        for item in board[row]:
            print(item, end=" ")
        print(end="\n")

# Функция создания бомб
def create_bombs(size, count=10):
    bombs = set()
    while count > len(bombs):
        bombs.add((random.randint(0, size - 1), random.randint(0, size - 1)))
    return bombs

# Функция высчитвает сколько бомб вокруг
def count_around(size, bombs, row, col):
    around = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            nr = row + dr
            nc = col + dc

            if dr == 0 and dc == 0:
                continue

            if nr < 0 or nr >= size or nc < 0 or nc >= size:
                continue

            if (nr, nc) in bombs:
                around += 1

    return around

# Функция валидация хода
def read_move(size):
    while True:
        move = input("Введите ряд и столбец на пример 3 4:").split()
        if len(move) != 2 or not move[0].isdigit() or not move[1].isdigit():
            print(f"Введите два числа от 0 до {size - 1}")
            continue
        row, col = (int(move[0]), int(move[1]))
        if row >= size or col >= size:
            print("Эта клетка пересекает черту поля")
            continue
        return row, col

# Функция рекурсии
def open_cell(size, bombs, row, col, board):
    if row >= size or col >= size or row < 0 or col < 0:
        return
    if board[row][col] != "*":
        return
    if (row, col) in bombs:
        return

    around = count_around(size, bombs, row, col)

    if around == 0:
        board[row][col] = "0"
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr = row + dr
                nc = col + dc

                if nr < 0 or nr >= size or nc < 0 or nc >= size:
                    continue

                if dr == 0 and dc == 0:
                    continue

                open_cell(size, bombs, nr, nc, board)

    else:
        board[row][col] = str(around)
        return

# Функция проверки победы
def check_win(size, bombs, board):
    safety = 0
    for row in range(size):
        for col in range(size):
            if board[row][col] == "*" and (row, col) not in bombs:
                safety += 1

    return safety == 0


SIZE = 8
board = create_board(SIZE)
bombs = create_bombs(SIZE)

# Главный цикл програмы
while True:
    print_board(board)
    row, col = read_move(SIZE)
    if (row, col) in bombs:
        print("Boom!!!")
        print("Проигришь!")
        for row, col in bombs:
            board[row][col] = "B"
        print_board(board)
        break
    if board[row][col] != "*":
        print("Клетка уже открыта!")
        continue
    open_cell(SIZE, bombs, row, col, board)
    if check_win(SIZE, bombs, board):
        print("Победа!!!!")
        for row, col in bombs:
            board[row][col] = "B"
        print_board(board)
        break
