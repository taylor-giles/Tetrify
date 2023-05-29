import numpy as np

# Import the gym
import sys
sys.path.append('./tetris-gym')
from tetris_env import TetrisAction, EndResult, get_shape_grid, is_occupied, has_dropped, rotated, piece_match, count_false_positives, count_false_negatives
import curses

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

features = [count_false_positives, count_false_negatives]
feature_names = ["False Positives", "False Negatives"]
weights = [-1, -1]

def get_features(_board):
    # Copy the board
    board = np.copy(_board)

    # Given a board, return the values of each feature of that board
    return [feature(board) for feature in features]


# Returns the optimal (ordered) sequence of actions to achieve the desired placement starting from the current state.
def generate_action_sequence(placement, current_state):
    sequence = []
    placement_shape, placement_anchor_col = placement
    board, shape, anchor = current_state
    placement_shape_grid = get_shape_grid(placement_shape)
    
    # If the orientation of the shape does not match, then rotate
    while not np.array_equal(get_shape_grid(shape), placement_shape_grid):
        # Determine which way to rotate
        if np.array_equal(get_shape_grid(rotated(shape, True)), placement_shape_grid):
            sequence.append(TetrisAction.ROTATE_RIGHT)
            shape = rotated(shape, True)
        else:
            sequence.append(TetrisAction.ROTATE_LEFT)
            shape = rotated(shape, False)
    
    # If the anchor column does not match, then move
    col_diff = anchor[0] - placement_anchor_col
    while col_diff != 0:
        if col_diff > 0:
            sequence.append(TetrisAction.LEFT)
            col_diff-=1
        else:
            sequence.append(TetrisAction.RIGHT)
            col_diff+=1
    
    # Do the drop
    sequence.append(TetrisAction.HARD_DROP)
    return sequence


class TetrisAgent:
    def __init__(self, parameters):
        self.parameters = [-1 for _ in features]
        self.current_state = (None, None, None, None)

    def state_value(self, board):
        # Given a board and a list of feature weights (parameters), return the summed "goodness" value of the board
        return sum([feature*weight for feature, weight in zip(get_features(board), self.parameters)])
    
    # Returns a tuple (shape, anchor_col) where those values are the optimal way to play this piece as decided by this agent
    def get_goal_placement(self, _board, shape):
        curr_max_val = None
        curr_best_placement = (None, None, None)

        # For each orientation of the piece...
        prev_orientations = [] # Keep track of previous orientations to check for duplicates
        for ori in range(4): # Max 4 orientations per shape
            # Rotate the shape
            shape = rotated(shape)

            # Check if this orientation has already been seen
            if np.any([np.array_equal(get_shape_grid(shape), prev_shape_grid) for prev_shape_grid in prev_orientations]):
                # This orientation has been seen before (therefore all unique orientations have been seen), so do not continue checking new orientations.
                break
            prev_orientations.append(get_shape_grid(shape))
            
            # For each possible anchor column...
            for x in range(BOARD_WIDTH):
                board = np.copy(_board)

                # Check if this is a valid placement
                start_height = abs(min(_y for _, _y in shape))
                if not is_occupied(shape, (x, start_height), board):
                    # This is valid placement. Simulate dropping the piece
                    y = start_height-1
                    while not has_dropped(shape, (x, y), board):
                        y += 1
                    
                    # Draw the shape into the board
                    for cell in shape:
                        # print(x, cell[0])
                        board[x + cell[0], y + cell[1]] = 2

                    # Successfully hallucinated the dropping of the piece. Evaluate the value of this new board
                    board_val = self.state_value(board)
                    
                    if curr_max_val == None:
                        curr_max_val = board_val
                    
                    if board_val >= curr_max_val:
                        curr_best_placement = (shape, x)
        return curr_best_placement


    # Takes the actions in order as specified by the input queue. 
    # Returns a tuple containing the list of rewards from the actions in this sequence and a boolean indicating whether or not the game ended during this sequence.
    def take_action_sequence(self, sequence, env, placement):
        done = EndResult.NOT_DONE
        for action in sequence:
            if done == EndResult.NOT_DONE:
                self.current_state, done = env.step(action)
                board, shape, anchor = self.current_state

                # End this sequence early if the piece dropped earlier than expected
                if has_dropped(shape, (int(anchor[0]), int(anchor[1])), board):
                    break
        return done
    

    def play(self, env):
        while done != EndResult.SUCCESS:
            done = EndResult.NOT_DONE
            self.current_state = env.init()
            self.action_sequence = []
            while done == EndResult.NOT_DONE:
                board, shape, anchor = self.current_state

                # Determine the best placement and take the action sequence for it
                placement = self.get_goal_placement(board, shape)
                sequence = generate_action_sequence(placement, self.current_state)
                done = self.take_action_sequence(sequence, env, placement)
        return self.rewards

