import numpy as np
import random
from enum import Enum
from utils import log

# This enum is designed so that, when a block is placed, each of its cell values can be updated by incrementing by 1.
# (similarly, if a cell is cleared, its value can be decremented by 1)
# Value 2 is skipped intentionally, to act as an error indicator (it is not possible to fill a false positive or clear a false negative)
class CellValue(Enum):
    EMPTY=0             # The cell is not selected and not filled
    FALSE_POSITIVE=1    # The cell is filled, but not selected
    FALSE_NEGATIVE=3    # The cell is selected, but not filled
    FILLED=4            # The cell is both selected and filled

def is_filled(cell_value: CellValue):
    return cell_value == CellValue.FILLED.value or cell_value == CellValue.FALSE_POSITIVE.value

class EndResult(Enum):
    NOT_DONE = -1
    SUCCESS = 0
    FAILURE = 1

pieces = {
    'T': [(0, 0), (-1, 0), (1, 0), (0, -1)],
    'J': [(0, 0), (-1, 0), (0, -1), (0, -2)],
    'L': [(0, 0), (1, 0), (0, -1), (0, -2)],
    'Z': [(0, 0), (-1, 0), (0, -1), (1, -1)],
    'S': [(0, 0), (-1, -1), (0, -1), (1, 0)],
    'I': [(0, 0), (0, -1), (0, -2), (0, -3)],
    'O': [(0, 0), (0, -1), (-1, 0), (-1, -1)],
}
piece_names = ['T', 'J', 'L', 'Z', 'S', 'I', 'O']

# Returns a 4x4 grid representing the piece. 
# If a piece has equivalent orientations, those orientations will produce the same grid.
def get_shape_grid(shape):
    # Determine anchor location
    sum_x = max([coord[0] for coord in shape]) + min([coord[0] for coord in shape])
    sum_y = max([coord[1] for coord in shape]) + min([coord[1] for coord in shape])
    anchor = (1 if sum_x>=0 else 2, 1 if sum_y>=0 else 2)

    # Populate grid
    grid = np.zeros(shape=(4, 4))
    for coord in shape:
        grid[int(anchor[1] + coord[1])%4, int(anchor[0] + coord[0])%4] = 1
    return grid

def rotated(shape, cclk=False):
    if not cclk:
        return [(-j, i) for i, j in shape]
    else:
        return [(j, -i) for i, j in shape]


# Returns False iff it is possible for the shape to occupy that anchor location
def is_occupied(shape, anchor, board):
    for i, j in shape:
        x, y = anchor[0] + i, anchor[1] + j
        if x < 0 or y < 0 or x >= board.shape[0] or y >= board.shape[1] or (is_filled(board[x, y][0]) and not board[x,y][1]):
            return True
    return False


# Returns True iff the shape cannot fall any more
def has_dropped(shape, anchor, board):
    return is_occupied(shape, (anchor[0], anchor[1] + 1), board)

# Returns True iff the shapes (piece AND orientation) are the same
def shape_match(shape1, shape2):
    return np.array_equal(get_shape_grid(shape1), get_shape_grid(shape2))

# Returns True iff the pieces represented by the shapes are the same, regardless of orientation.
def piece_match(shape1, shape2):
    covered_all_orientations = False
    new_shape = np.copy(shape1)
    while not covered_all_orientations:
        new_shape = rotated(new_shape)
        if shape_match(new_shape, shape1):
            covered_all_orientations = True
        if shape_match(new_shape, shape2):
            return True
    return False

# Returns the name of the given piece
def get_piece_name(piece):
    for name in piece_names:
        if piece_match(piece, pieces[name]):
            return name
    return None

# Returns the index of this piece in the shapes list
def get_piece_index(piece):
    return piece_names.index(get_piece_name(piece))


##                            ##
## FUNCTIONS FOR GAME ACTIONS ##
##                            ##
def left(shape, anchor, board):
    new_anchor = (anchor[0] - 1, anchor[1])
    return (shape, anchor) if is_occupied(shape, new_anchor, board) else (shape, new_anchor)

def right(shape, anchor, board):
    new_anchor = (anchor[0] + 1, anchor[1])
    return (shape, anchor) if is_occupied(shape, new_anchor, board) else (shape, new_anchor)

def soft_drop(shape, anchor, board):
    new_anchor = (anchor[0], anchor[1] + 1)
    return (shape, anchor) if is_occupied(shape, new_anchor, board) else (shape, new_anchor)

def hard_drop(shape, anchor, board):
    while True:
        _, anchor_new = soft_drop(shape, anchor, board)
        if anchor_new == anchor:
            return (shape, anchor_new)
        anchor = anchor_new

def rotate_left(shape, anchor, board):
    new_shape = rotated(shape, cclk=False)
    return (shape, anchor) if is_occupied(new_shape, anchor, board) else (new_shape, anchor)

def rotate_right(shape, anchor, board):
    new_shape = rotated(shape, cclk=True)
    return (shape, anchor) if is_occupied(new_shape, anchor, board) else (new_shape, anchor)

def idle(shape, anchor, board):
    return (shape, anchor)


class TetrisAction(Enum):
    LEFT=left
    RIGHT=right
    HARD_DROP=hard_drop
    SOFT_DROP=soft_drop
    ROTATE_LEFT=rotate_left
    ROTATE_RIGHT=rotate_right
    IDLE=idle

def take_action(shape, anchor, board: np.ndarray, action: TetrisAction):
    new_vals = action(shape, anchor, board)
    clear_ghosts(board)
    apply_shape(*new_vals, board)
    return new_vals


def clear_ghosts(board: np.ndarray):
    is_ghost = board[:, :, 1]  # Extract the is_ghost values

    # Subtract 1 from the cell value of every ghost block and set it to non-ghost
    for index, value in np.ndenumerate(is_ghost):
        if value:
            board[index] = (board[index][0]-1, False, None)


def apply_shape(shape, anchor, board: np.ndarray, force_not_ghost=False):
    for i, j in shape:
        x, y = i + anchor[0], j + anchor[1]
        if x < board.shape[0] and x >= 0 and y < board.shape[1] and y >= 0:
            # Determine new values
            curr_value, curr_is_ghost, curr_piece_index = board[x, y]

            # If this cell is already filled, then there is no need to update its value
            new_val = curr_value + 1
            new_is_ghost = not has_dropped(shape, anchor, board) and not force_not_ghost
            new_piece_name = get_piece_name(shape)

            # Set cell
            board[x,y] = (new_val, new_is_ghost, new_piece_name)


def count_false_negatives(board: np.ndarray):
    return np.count_nonzero(board[:, :, 0] == CellValue.FALSE_NEGATIVE.value)

def count_false_positives(board: np.ndarray):
    return np.count_nonzero(board[:, :, 0] == CellValue.FALSE_POSITIVE.value)

def count_buried_false_negatives(board: np.ndarray):
    # For every column, work up from the bottom to determine how many false negatives are buried
    output = 0
    for x in range(board.shape[0]):
        count = 0
        for y in reversed(range(board.shape[1])):
            if board[x,y][0] == CellValue.FALSE_NEGATIVE.value:
                count+=1
            if is_filled(board[x,y][0]):
                output += count
                count = 0
    return output

def count_ghosts(board: np.ndarray):
    return np.count_nonzero(board[:, :, 1])

# A "straggler" is a false negative that cannot be filled without creating at least one false positive.
# This function uses DFS to determine the mod4 size of each island of false negatives, 
#   then returns a tuple containing the number of stragglers and the total number of islands.
# The number of islands can be used as the lower bound for the number of false positives required to fill all stragglers (one per island).
# Note that it is not sufficient to say that the stragglers of an island can be filled by a minimum of 4-(island size % 4) false positives, 
#   because it is possible that placing a single block could fill the stragglers of multiple islands (max 3).
def count_stragglers(board: np.ndarray):
    num_stragglers = 0
    num_islands = 0
    visited = np.full((board.shape[0], board.shape[1]), False)

    def dfs(x, y):
        currentSize = 0

        # Bounds check
        if (0 <= x and x < board.shape[0]) and (0 <= y and y < board.shape[1]) and not visited[x][y]:
            visited[x][y] = True

            # Value check
            if board[x][y][0] == CellValue.FALSE_NEGATIVE.value:
                currentSize += 1

                # Recursive calls (one for each neighbor)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    currentSize += dfs(x + dx, y + dy)
        return currentSize

    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if not visited[x][y] and board[x][y][0] == CellValue.FALSE_NEGATIVE.value:
                num_stragglers += dfs(x, y) % 4
                num_islands += 1

    return (num_stragglers, num_islands)


def board_from_grid(grid: np.ndarray):
    # Populate board with tuples of (CellValue, is_ghost, piece_name)
    board = np.empty((*grid.T.shape, 3), dtype='object')
    for index, value in np.ndenumerate(grid.T):
        board[index] = (CellValue.FALSE_NEGATIVE.value if value else CellValue.EMPTY.value, False, None)  
    return board

def get_random_piece(board: np.ndarray):
    # Choose piece
    piece = random.sample(pieces)
    return set_piece(board, piece)


def set_piece(board: np.ndarray, shape):
    piece = pieces[get_piece_name(shape)]

    # Determine the height of the anchor to get the whole shape on the screen
    height = abs(min(y for _, y in piece))

    # Place shape at the top of the board in the center
    anchor = (board.shape[0] // 2, height)

    # Apply the piece
    apply_shape(piece, anchor, board)

    # Return shape and anchor
    return (piece, anchor)


def print_board(board: np.ndarray):
    s = '\n+' + '-' * board.shape[0] + '+\n'
    s += '\n'.join(['|' + ''.join([str(j[0]) if not j[1] else 'G' for j in i]) + '|' for i in np.transpose(board, axes=(1, 0, 2))])
    s += '\n+' + '-' * board.shape[0] + '+'
    return s    





































class TetrisArtGym:
    def __init__(self, board: np.ndarray, allowable_false_positives: int, allowable_false_negatives: int, colors):
        # Populate board with tuples of (CellValue, is_ghost, color)
        self.board = np.empty(board.shape, dtype='object')
        self.width, self.height = board.shape
        for index, value in np.ndenumerate(board):
            self.board[index] = (value * CellValue.FALSE_NEGATIVE.value, False, None)

        self.allowable_false_positives = allowable_false_positives
        self.allowable_false_negatives = allowable_false_negatives
        self.colors = colors

        self.anchor = None
        self.shape = None

        self.new_piece()
    
    def new_piece(self, shape=None):
        # Choose shape
        self.shape = shape if shape else self._choose_shape()

        # Determine the height of the anchor to get the whole shape on the screen
        height = abs(min(y for _, y in self.shape))

        # Place shape at the top of the board in the center
        self.anchor = (self.width / 2, height)

    def step(self, action):
        # Take the action
        self.shape, self.anchor = self.value_action_map[action](self.shape, self.anchor, self.board)

        # Determine whether or not the piece dropped
        did_drop = has_dropped(self.shape, self.anchor, self.board)

        # Apply shape
        self.apply_shape()
        
        # Evaluate end conditions
        if did_drop:
            if count_false_positives(self.board) > self.allowable_false_positives:
                done = EndResult.FAILURE
            elif count_false_negatives(self.board) < self.allowable_false_negatives:
                done = EndResult.SUCCESS
            else: 
                done = EndResult.NOT_DONE

        state = (np.copy(self.board), self.shape.copy(), self.anchor) 
        return state, done
    
    def apply_shape(self):
        for i, j in self.shape:
            x, y = i + self.anchor[0], j + self.anchor[1]
            if x < self.width and x >= 0 and y < self.height and y >= 0:
                # Determine new values
                curr_value, curr_is_ghost, curr_color = self.board[x, y]
                new_val = curr_value if curr_is_ghost else curr_value + 1
                new_is_ghost = not has_dropped(self.shape, self.anchor, self.board)
                new_color = self.get_color(self.shape)

                # Set cell
                self.board[x,y] = (new_val, new_is_ghost, new_color)

    def get_color(self, shape):
        return self.colors[get_piece_name(shape)]



















class TetrisGym:
    def __init__(self, width, height, max_time=5000):
        self.width = width
        self.height = height
        self.board = np.zeros(shape=(width, height), dtype=np.float64)
        self.max_time = max_time

        # Mapping from action enum value to function
        self.value_action_map = {
            TetrisAction.LEFT: left,
            TetrisAction.RIGHT: right,
            TetrisAction.HARD_DROP: hard_drop,
            TetrisAction.SOFT_DROP: soft_drop,
            TetrisAction.ROTATE_LEFT: rotate_left,
            TetrisAction.ROTATE_RIGHT: rotate_right,
            TetrisAction.IDLE: idle,
            TetrisAction.SWAP_HOLD: swap_hold,
        }
        self.action_value_map = dict([(j, i) for i, j in self.value_action_map.items()])

        # for running the engine
        self.time = -1
        self.score = -1
        self.anchor = None
        self.shape = None
        self.n_deaths = 0

        # used for generating shapes
        self._shape_counts = [0] * len(pieces)

        # clear after initializing
        self.init()


    def _choose_shape(self):
        maxm = max(self._shape_counts)
        m = [5 + maxm - x for x in self._shape_counts]
        r = random.randint(1, sum(m))
        for i, n in enumerate(m):
            r -= n
            if r <= 0:
                self._shape_counts[i] += 1
                return pieces[piece_names[i]]


    def _new_piece(self, shape=None):
        # Choose shape
        self.shape = shape if shape else self._choose_shape()

        # Determine the height of the anchor to get the whole shape on the screen
        height = abs(min(y for _, y in self.shape))

        # Place shape at the top of the board in the center
        self.anchor = (self.width / 2, height)
        

    def _clear_lines(self):
        can_clear = [np.all(self.board[:, i]) for i in range(self.height)]
        new_board = np.zeros_like(self.board)
        j = self.height - 1
        for i in range(self.height - 1, -1, -1):
            if not can_clear[i]:
                new_board[:, j] = self.board[:, i]
                j -= 1
        self.score += sum(can_clear)
        self.board = new_board
        return sum(can_clear)

    def _has_dropped(self):
        return has_dropped(self.shape, self.anchor, self.board)

    def step(self, action):
        self.anchor = (int(self.anchor[0]), int(self.anchor[1]))
        self.shape, self.anchor, self.hold_piece = self.value_action_map[action](self.shape, self.anchor, self.board, self.hold_piece)
        
        # Drop each step
        # self.shape, self.anchor, self.hold_piece = soft_drop(self.shape, self.anchor, self.board, self.hold_piece)

        # Update time and reward
        self.time += 1
        reward = 0
        lines_cleared = 0
        done = self.time > self.max_time
        if self._has_dropped():
            self._set_piece(True)
            lines_cleared = self._clear_lines()
            reward = 10 ** (2*lines_cleared)
            if np.any(self.board[:, 0]):
                self.n_deaths += 1
                done = True
                reward = 0
            else:
                self._new_piece()

        state = (np.copy(self.board), self.shape.copy(), self.anchor, self.hold_piece) 
        self._set_piece(False)
        return state, (reward, lines_cleared), done

    def init(self, seed=None):
        self.time = 0
        self.score = 0
        self._new_piece()
        self.board = np.zeros_like(self.board)

        # Set random seed
        if seed:
            random.seed(seed)

        # Init hold piece
        self.hold_piece = self._choose_shape()

        # Return initial game state
        return (self.board, self.shape.copy(), self.anchor, self.hold_piece)

    def _set_piece(self, on=False):
        for i, j in self.shape:
            x, y = i + self.anchor[0], j + self.anchor[1]
            if x < self.width and x >= 0 and y < self.height and y >= 0:
                self.board[int(self.anchor[0] + i), int(self.anchor[1] + j)] = on

    def get_display_board(self):
        self._set_piece(True)
        display_board = np.copy(self.board)
        self._set_piece(False)
        return display_board

    def __repr__(self):
        self._set_piece(True)
        s = 'o' + '-' * self.width + 'o\n'
        s += '\n'.join(['|' + ''.join(['X' if j else ' ' for j in i]) + '|' for i in self.board.T])
        s += '\no' + '-' * self.width + 'o'
        s += '\n\nHold:'
        s += '\n+----+\n'
        s += '\n'.join(['|' + ''.join(['X' if j else ' ' for j in i]) + '|' for i in get_shape_grid(self.hold_piece)])
        s += '\n+----+\n'
        self._set_piece(False)
        return s
