from defines import *
import time


# Point (x, y) if in the valid position of the board.
def isValidPos(x, y):
    return 0 <= x < Defines.GRID_NUM and 0 <= y < Defines.GRID_NUM


def init_board(board):
    for i in range(21):
        board[i][0] = board[0][i] = board[i][Defines.GRID_NUM - 1] = board[Defines.GRID_NUM - 1][i] = Defines.BORDER
    for i in range(1, Defines.GRID_NUM - 1):
        for j in range(1, Defines.GRID_NUM - 1):
            board[i][j] = Defines.NOSTONE


def make_move(board, move, color):
    board[move.positions[0].x][move.positions[0].y] = color
    board[move.positions[1].x][move.positions[1].y] = color


def unmake_move(board, move):
    board[move.positions[0].x][move.positions[0].y] = Defines.NOSTONE
    board[move.positions[1].x][move.positions[1].y] = Defines.NOSTONE


def is_win_by_premove(board, preMove):
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1)]
    for pos in preMove.positions:
        for dx, dy in directions:
            count = 1  # Count the current stone
            # Check in the positive direction
            x, y = pos.x, pos.y
            while isValid(board, x + dx, y + dy) and board[x + dx][y + dy] == board[pos.x][pos.y] and board[x + dx][
                y + dy] != Defines.NOSTONE:
                count += 1
                x += dx
                y += dy
            # Check in the negative direction
            x, y = pos.x, pos.y
            while isValid(board, x - dx, y - dy) and board[x - dx][y - dy] == board[pos.x][pos.y] and board[x + dx][
                y + dy] != Defines.NOSTONE:
                count += 1
                x -= dx
                y -= dy
            # Winning condition
            if count >= 6:
                return True
    return False


def isValid(board, x, y):
    return 0 <= x < len(board) and 0 <= y < len(board[0]) and board[x][y] != Defines.BORDER


def log_to_file(msg):
    g_log_file_name = Defines.LOG_FILE
    try:
        with open(g_log_file_name, "a") as file:
            tm = time.time()
            ptr = time.ctime(tm)
            ptr = ptr[:-1]
            file.write(f"[{ptr}] - {msg}\n")
        return 0
    except Exception as e:
        print(f"Error: Can't open log file - {g_log_file_name}")
        return -1


def msg2move(msg):
    move = StoneMove([StonePosition(0, 0), StonePosition(0, 0)])
    if len(msg) == 2:
        move.positions[0].x = move.positions[1].x = ord('S') - ord(msg[1]) + 1
        move.positions[0].y = move.positions[1].y = ord(msg[0]) - ord('A') + 1
        move.score = 0
        return move
    else:
        move.positions[0].x = ord('S') - ord(msg[1]) + 1
        move.positions[0].y = ord(msg[0]) - ord('A') + 1
        move.positions[1].x = ord('S') - ord(msg[3]) + 1
        move.positions[1].y = ord(msg[2]) - ord('A') + 1
        move.score = 0
        return move


def print_board(board, preMove=None):
    print("   " + "".join([chr(i + ord('A') - 1) + " " for i in range(1, Defines.GRID_NUM - 1)]))
    for i in range(1, Defines.GRID_NUM - 1):
        print(f"{chr(ord('A') - 1 + i)}", end=" ")
        for j in range(1, Defines.GRID_NUM - 1):
            x = Defines.GRID_NUM - 1 - j
            y = i
            stone = board[x][y]
            if stone == Defines.NOSTONE:
                print(" -", end="")
            elif stone == Defines.BLACK:
                print(" O", end="")
            elif stone == Defines.WHITE:
                print(" *", end="")
            elif stone == Defines.POSSIBLE:
                print(" +", end="")
        print(" ", end="")
        print(f"{chr(ord('A') - 1 + i)}", end="\n")
    print("   " + "".join([chr(i + ord('A') - 1) + " " for i in range(1, Defines.GRID_NUM - 1)]))