class Defines:
    GRID_NUM = 21  # Number of the board, 19*19 plus edges.
    GRID_COUNT = 361  # Sum of the points in the board.
    BLACK = 1  # Black flag in the board.
    WHITE = 2  # White flag in the board.
    BORDER = 3  # Border flag in the board
    NOSTONE = 0  # Empty flag.
    MSG_LENGTH = 512  # Tamaño del mensaje
    LOG_FILE = "tia-lbe-engine.log"
    ENGINE_NAME = "lbe"
    # Max values in the evaluation.
    MAXINT = 20000
    MININT = -20000


class StonePosition:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, StonePosition):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(f'{self.x}{self.y}')

class StoneMove:
    def __init__(self, positions):
        self.positions = positions
        self.score = 0

    def __iter__(self):
        return iter(self.positions)

    def __eq__(self, other):
        if not isinstance(other, StoneMove):
            return False

        return set(self.positions) == set(other.positions)

    def __hash__(self):
        items_list = list()
        for item in self:
            items_list.append(hash(item))
        return hash(tuple(items_list))

    def __str__(self):
        if self.positions[0].x == self.positions[1].x and self.positions[0].y == self.positions[1].y:
            msg = f"{chr(ord('S') - self.positions[0].x + 1)}{chr(self.positions[0].y + ord('A') - 1)}"
            return msg
        else:
            msg = f"{chr(self.positions[0].y + ord('A') - 1)}{chr(ord('S') - self.positions[0].x + 1)}" \
                  f"{chr(self.positions[1].y + ord('A') - 1)}{chr(ord('S') - self.positions[1].x + 1)}"
            return msg