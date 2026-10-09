# Раніше в коді було два виведення дошки, тому ми винесли його у функцію print_board()
# read_move() може використовувати return замість break, тому що return повертає значення та завершує цикл
# AI log: Довго не могла зрозуміти, як розділити код на функції та як вони взаємодіють між собою
# питала, що кожна функція отримує і повертає, куди передається результат та куди він далі йде
import random

SIZE = 8
BOMBS = 10

def create_bombs(size, count=10):
    bombs = set()
    while len(bombs) < count:
        bombs.add((random.randint(0, size - 1), random.randint(0, size - 1)))
    return bombs

bombs = create_bombs(SIZE)

def count_around(bombs, row, col):
    around = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if (row + dr, col + dc) in bombs:
                around += 1
    return around


def create_board(size):
    hidden = [["." for col in range(size)] for row in range(size)]
    return hidden

hidden = create_board(SIZE)

opened = 0
def print_board(board):
    print("   0 1 2 3 4 5 6 7")
    for row in range(len(board)):
        line = str(row) + " "
        for cell in board[row]:
            line += " " + cell
        print(line)


def read_move(size):
    while True:
        answer = input("Row and column, for example 3 5: ").split()
        if len(answer) != 2 or not answer[0].isdigit() or not answer[1].isdigit():
            print("Type two numbers from 0 to 7")
            continue

        row, col = int(answer[0]), int(answer[1])

        if row >= size or col >= size:
            print("This cell is outside the board")
            continue

        return row, col


while opened < SIZE * SIZE - BOMBS:

    print_board(hidden)

    row, col = read_move(SIZE)

    if hidden[row][col] != ".":
        print("This cell is already open")
        continue

    if (row, col) in bombs:
        print("Boom! Game over.")
        break

    hidden[row][col] = str(count_around(bombs, row, col))
    opened += 1
else:
    print("You win!")

for row, col in bombs:
    hidden[row][col] = "*"

print_board(hidden)
