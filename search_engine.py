import hashlib
from tools import *


class SearchEngine:
    def __init__(self):
        self.m_board = None  # The game board
        self.m_chess_type = None  # The type of chess piece (black or white)
        self.m_alphabeta_depth = None  # Depth for the alpha-beta pruning
        self.m_total_nodes = 0  # Total nodes explored
        self.m_beta_pod = 0  # Beta cutoffs count
        self.transposition_table = {}  # Hash table for storing board positions

    def before_search(self, board, color, alphabeta_depth):
        # Initialize the search engine with the current state of the game
        self.m_board = [row[:] for row in board]  # Clone the board
        self.m_chess_type = color  # Set the current player's color
        self.m_alphabeta_depth = alphabeta_depth  # Set the search depth
        self.m_total_nodes = 0  # Reset the total nodes explored
        self.m_beta_pod = 0  # Reset beta cutoffs

    def hash_board(self):
        """ Generate a unique hash for the current board position. """
        return hashlib.sha256(str(self.m_board).encode()).hexdigest()

    def alpha_beta_search(self, depth, alpha, beta, ourColor, bestMove, preMove):
        # Alpha-beta pruning search algorithm
        self.m_total_nodes += 1  # Increment total nodes explored

        # Generate a hash for the current board state
        board_hash = self.hash_board()

        # Check if the result of this position is already computed
        if board_hash in self.transposition_table and self.transposition_table[board_hash]['depth'] >= depth:
            return self.transposition_table[board_hash]['score']

        # Check for the first move
        if self.check_first_move():
            # Set a default move if it's the first move
            bestMove.positions[0].x = 10
            bestMove.positions[0].y = 10
            bestMove.positions[1].x = 10
            bestMove.positions[1].y = 10
            return Defines.MAXINT

        # Check if the pre-move is a winning move
        if is_win_by_premove(self.m_board, preMove):
            return Defines.MAXINT

        # If reached the desired depth, evaluate the position
        if depth == 0:
            return self.evaluate_position(ourColor, preMove)

        # Generate possible moves for the first stone
        move_possibilities = self.generate_moves(bestMove)

        best_score = float('-inf')
        best_position_first = None
        best_position_second = None

        # Search for the best move for the first stone
        for position_first in move_possibilities:
            tempMove = StoneMove([position_first, position_first])
            make_move(self.m_board, tempMove, ourColor)
            score_first = self.evaluate_position(ourColor, position_first)

            # Search for the best move for the second stone
            for position_second in move_possibilities:
                if position_second == position_first:
                    continue
                tempMove = StoneMove([position_first, position_second])
                make_move(self.m_board, tempMove, ourColor)
                score_second = self.evaluate_position(ourColor, position_second)

                # Recursive call for the next depth level
                if depth > 1:
                    score_second -= self.alpha_beta_search(depth - 1, -beta, -alpha, 3 - ourColor, bestMove, tempMove)

                total_score = score_first + score_second
                unmake_move(self.m_board, tempMove)

                if total_score > best_score:
                    best_score = total_score
                    best_position_first = position_first
                    best_position_second = position_second

                if best_score > alpha:
                    alpha = best_score

            unmake_move(self.m_board, StoneMove([position_first, position_first]))
            if alpha >= beta:
                self.m_beta_pod += 1
                break  # Alpha-beta cutoff

        # Save the best move
        if best_position_first and best_position_second:
            bestMove.positions[0] = best_position_first
            bestMove.positions[1] = best_position_second

        bestMove.score = best_score

        # Save the result in the transposition table
        self.transposition_table[board_hash] = {'score': best_score, 'depth': depth}

        return best_score

    def generate_moves(self, lastMove):
        # Generate possible moves based on the last move
        possible_positions = set()

        # Set a fixed radius around the stones of the last move
        radius = 3

        # Iterate through cells around each stone of the last move
        for pos in lastMove.positions:
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    new_x, new_y = pos.x + dx, pos.y + dy
                    if isValidPos(new_x, new_y) and self.m_board[new_x][new_y] == Defines.NOSTONE:
                        possible_positions.add(StonePosition(new_x, new_y))

        # Add moves within a radius of 1 from each enemy stone
        enemy_color = 3 - self.m_chess_type
        for i in range(len(self.m_board)):
            for j in range(len(self.m_board[i])):
                if self.m_board[i][j] == enemy_color:
                    for dx in range(-1, 2):  # Radius of 1
                        for dy in range(-1, 2):
                            new_x, new_y = i + dx, j + dy
                            if isValidPos(new_x, new_y) and self.m_board[new_x][new_y] == Defines.NOSTONE:
                                possible_positions.add(StonePosition(new_x, new_y))

        return list(possible_positions)

    def evaluate_position(self, ourColor, position):
        # Evaluate the board position
        WIN_SCORE = float('inf')
        BLOCK_SCORE = 1000  # High score for blocking the opponent's winning line
        THREAT_MULTIPLIER = 20  # Weight for our own lines
        CENTER_BONUS = 10

        def count_in_direction(x, y, dx, dy, color):
            # Count stones in a specific direction
            count = 0
            while isValidPos(x, y) and self.m_board[x][y] == color:
                count += 1
                x += dx
                y += dy
            return count

        def evaluate_direction(x, y, color, own_color):
            # Evaluate threats and winning positions around a given position
            for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1), (-1, 0), (0, -1)]:
                count = count_in_direction(x + dx, y + dy, dx, dy, color) + count_in_direction(x - dx, y - dy, -dx, -dy,
                                                                                               color) + 1
                if color == own_color and count >= 6:
                    return WIN_SCORE  # Win by our move
                elif color != own_color and count >= 5:
                    return BLOCK_SCORE  # Block opponent's winning line
            return 0

        x, y = position.x, position.y
        our_win_score = evaluate_direction(x, y, ourColor, ourColor)
        if our_win_score == WIN_SCORE:
            return WIN_SCORE

        enemy_color = 3 - ourColor
        block_score = evaluate_direction(x, y, enemy_color, ourColor)
        if block_score == BLOCK_SCORE:
            return BLOCK_SCORE

        # Evaluate the length of our own lines
        total_score = 0
        for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1), (-1, 0), (0, -1)]:
            count = count_in_direction(x + dx, y + dy, dx, dy, ourColor) + count_in_direction(x - dx, y - dy, -dx, -dy,
                                                                                              ourColor) + 1
            if 2 <= count < 6:
                total_score += THREAT_MULTIPLIER ** count

        # Calculate reward for proximity to the center
        center_x, center_y = 9, 9
        distance_to_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        center_bonus = CENTER_BONUS / (1 + distance_to_center)

        return total_score + center_bonus

    def check_first_move(self):
        # Check if it's the first move of the game
        for i in range(1, len(self.m_board) - 1):
            for j in range(1, len(self.m_board[i]) - 1):
                if self.m_board[i][j] != Defines.NOSTONE:
                    return False
        return True
