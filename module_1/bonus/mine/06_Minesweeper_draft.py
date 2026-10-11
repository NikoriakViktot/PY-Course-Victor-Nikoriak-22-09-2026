# Minesweeper – draft from the Lesson 6 live coding session.
# Topics of Lessons 4–6 only: while, for, lists, sets, dictionaries, comprehensions. No functions yet.
# In Lesson 7 you will split this code into functions: notice that the board is printed in two places.
#
# How to play: type a row and a column, for example 3 5. Open all cells without bombs to win.

import random

SIZE = 8
BOMBS = 10

# Bombs: a set of (row, col) tuples, so one cell cannot get two bombs
bombs = set()
while len(bombs) < BOMBS:
    bombs.add((random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)))

# How many bombs touch each safe cell: {(row, col): count}
counts = {}
for row in range(SIZE):
    for col in range(SIZE):
        if (row, col) in bombs:
            continue
        around = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if (row + dr, col + dc) in bombs:
                    around += 1
        counts[(row, col)] = around

# The board the player sees. Every row must be a NEW list:
# [["."] * SIZE] * SIZE would repeat one and the same row 8 times
hidden = [["." for col in range(SIZE)] for row in range(SIZE)]
opened = 0

while opened < SIZE * SIZE - BOMBS:
    print("   0 1 2 3 4 5 6 7")
    for row in range(SIZE):
        line = str(row) + " "
        for cell in hidden[row]:
            line += " " + cell
        print(line)

    answer = input("Row and column, for example 3 5: ").split()
    if len(answer) != 2 or not answer[0].isdigit() or not answer[1].isdigit():
        print("Type two numbers from 0 to 7")
        continue
    row, col = int(answer[0]), int(answer[1])
    if row >= SIZE or col >= SIZE:
        print("This cell is outside the board")
        continue
    if hidden[row][col] != ".":
        print("This cell is already open")
        continue
    if (row, col) in bombs:
        print("Boom! Game over.")
        break
    hidden[row][col] = str(counts[(row, col)])
    opened += 1
else:
    print("You win!")

# Show where the bombs were
for row, col in bombs:
    hidden[row][col] = "*"
print("   0 1 2 3 4 5 6 7")
for row in range(SIZE):
    line = str(row) + " "
    for cell in hidden[row]:
        line += " " + cell
    print(line)
