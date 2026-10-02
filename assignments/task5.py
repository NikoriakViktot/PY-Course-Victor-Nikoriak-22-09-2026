board = [" ", " ", " ", " ", " ", " ", " ", " ", " "]
current_player = "X"
print(board[0], board[1], board[2])
print(board[3], board[4], board[5])
print(board[6], board[7], board[8])
moves = 0
winning_lines = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 4, 8),
    (6, 4, 2),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8)
]
winner = False
while moves < 9 and winner == False:
    valid_move = False
    while valid_move == False:
        move = input("Choose a cell ")
        if move not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            print("Please enter a number from 1 to 9")
        else:
            move = int(move)
            if board[move - 1] != " ":
                print("This cell is already taken")
            else:
                valid_move = True
    board[move - 1] = current_player
    moves += 1
    print(board[0], board[1], board[2])
    print(board[3], board[4], board[5])
    print(board[6], board[7], board[8])
    line = 0
    while line < len(winning_lines):
        a, b, c = winning_lines[line]
        if board[a] == current_player and board[b] == current_player and board[c] == current_player:
            print(current_player, "WIN")
            winner = True
        line += 1
    if current_player == "X":
        current_player = "O"
    else:
        current_player = "X"
if winner == False:
    print("Draw")