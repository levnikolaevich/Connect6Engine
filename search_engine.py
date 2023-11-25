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
        self.transposition_table = {}

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

        # Generate possible moves for the first stone
        move_possibilities = self.generate_moves(bestMove)

        best_score = float('-inf')
        best_position_first = None
        best_position_second = None

        # Search for the best move for the first stone
        # evaluated_moves = set()  # Set to store evaluated positions of the first stone
        for position_first in move_possibilities:
            # Create a temporary move with the first stone
            tempMove = StoneMove([position_first, position_first])
            make_move(self.m_board, tempMove, ourColor)
            # Evaluate the board position after placing the first stone
            score_first = self.evaluate_position(ourColor, position_first)

            # Search for the best move for the second stone
            for position_second in move_possibilities:
                if position_second == position_first:
                    continue  # Skip if it's the same as the first position

                # Add the second stone and evaluate the board position
                tempMove = StoneMove([position_first, position_second])

                # SIN TABLA + SIN evaluated_moves AB Time:	29.850
                # if tempMove in evaluated_moves:
                # continue

                # evaluated_moves.add(tempMove)

                make_move(self.m_board, tempMove, ourColor)
                score_second = self.evaluate_position(ourColor, position_second)

                # Recursive call for the next depth level
                if depth > 1:
                    # Adjust score based on the minimax search for the next level
                    score_second -= self.alpha_beta_search(depth - 1, -beta, -alpha, 3 - ourColor, bestMove, tempMove)
                    # else:
                    #  print_board(self.m_board)
                total_score = score_first + score_second
                # Revert the move after evaluation
                unmake_move(self.m_board, tempMove)

                # Update the best score and best positions if the current score is higher
                if total_score > best_score:
                    best_score = total_score
                    best_position_first = position_first
                    best_position_second = position_second

                # Update alpha value for alpha-beta pruning
                if best_score > alpha:
                    alpha = best_score

                # Alpha-beta cutoff
                if alpha >= beta:
                    self.m_beta_pod += 1
                    break

            # Revert the initial move with only the first stone
            unmake_move(self.m_board, StoneMove([position_first, position_first]))

        # Save the best move
        if best_position_first and best_position_second:
            bestMove.positions[0] = best_position_first
            bestMove.positions[1] = best_position_second

        bestMove.score = best_score

        # Save the result in the transposition table
        # SIN AB Time: 12.014 Node: 2257
        # CON AB Time: 5.914 Node: 2257
        self.transposition_table[board_hash] = {'score': best_score, 'depth': depth}

        return best_score

    def generate_moves(self, lastMove):
        # Generate possible moves based on the last move
        possible_positions = set()

        # Set a fixed radius around the stones of the last move
        radius = 2

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
        WIN_SCORE = float('inf')
        LOSE_SCORE = float('-inf')
        LINE_MULTIPLIER = [0, 1, 10, 50, 200, 500]  # Scores for different line lengths
        CENTER_BONUS = 10
        BLOCK_THREAT_MULTIPLIER = 1000  # Increased weight for blocking opponent's line

        def count_in_direction(x, y, dx, dy, color):
            # Count stones in a specific direction and open ends
            count, open_ends = 0, 0
            while isValidPos(x, y) and self.m_board[x][y] == color:
                count += 1
                x += dx
                y += dy
            if isValidPos(x, y) and self.m_board[x][y] == Defines.NOSTONE:
                open_ends += 1
            return count, open_ends

        x, y = position.x, position.y
        enemy_color = 3 - ourColor

        total_score = 0
        for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1), (-1, 0), (0, -1)]:
            our_count, our_open_ends = count_in_direction(x + dx, y + dy, dx, dy, ourColor)
            our_count_reverse, our_open_ends_reverse = count_in_direction(x - dx, y - dy, -dx, -dy, ourColor)
            our_total_count = our_count + our_count_reverse
            our_total_open_ends = our_open_ends + our_open_ends_reverse

            enemy_count, enemy_open_ends = count_in_direction(x + dx, y + dy, dx, dy, enemy_color)
            enemy_count_reverse, enemy_open_ends_reverse = count_in_direction(x - dx, y - dy, -dx, -dy, enemy_color)
            enemy_total_count = enemy_count + enemy_count_reverse
            enemy_total_open_ends = enemy_open_ends + enemy_open_ends_reverse

            if our_total_count >= 6:
                return WIN_SCORE  # Winning condition
            if enemy_total_count >= 6:
                return LOSE_SCORE  # Losing condition

            # Scoring our lines
            if our_total_open_ends > 0:  # Only score if there are open ends
                total_score += LINE_MULTIPLIER[our_total_count] * our_total_open_ends

            # Scoring for blocking opponent's lines
            if enemy_total_count >= 5 and enemy_total_open_ends > 0:  # Blocking strong enemy lines
                total_score += BLOCK_THREAT_MULTIPLIER

        # Bonus for being closer to the center of the board
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
