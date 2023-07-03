import numpy as np
import random
from tetris_env import TetrisAction, EndResult, set_piece, get_shape_grid, is_occupied, has_dropped, rotated, piece_match, count_stragglers, count_false_positives, count_false_negatives, count_buried_false_negatives, pieces, apply_shape, print_board, take_action
from utils import log

features = [count_false_positives, count_false_negatives, count_buried_false_negatives]
weights = [-1, -1]

def get_features(_board):
    # Copy the board
    board = np.copy(_board)

    # Given a board, return the values of each feature of that board
    return [feature(board) for feature in features]


# Returns the optimal (ordered) sequence of actions to achieve the desired placement starting from the current state.
def generate_action_sequence(placement, board, shape, anchor):
    sequence = []
    placement_shape, placement_anchor = placement
    placement_shape_grid = get_shape_grid(placement_shape)
    
    # If the orientation of the shape does not match, then rotate
    while not np.array_equal(get_shape_grid(shape), placement_shape_grid):
        # Determine which way to rotate
        if np.array_equal(get_shape_grid(rotated(shape, False)), placement_shape_grid):
            sequence.append(TetrisAction.ROTATE_LEFT)
            shape = rotated(shape, False)
        else:
            sequence.append(TetrisAction.ROTATE_RIGHT)
            shape = rotated(shape, True)
    
    # If the anchor column does not match, then move
    col_diff = anchor[0] - placement_anchor[0]
    while col_diff != 0:
        if col_diff > 0:
            sequence.append(TetrisAction.LEFT)
            col_diff-=1
        else:
            sequence.append(TetrisAction.RIGHT)
            col_diff+=1
    
    # Do the drop (using soft drops)
    while not has_dropped(shape, anchor, board):
        anchor = (placement_anchor[0], anchor[1]+1)
        sequence.append(TetrisAction.SOFT_DROP)

    return sequence


class TetrisAgent:
    def __init__(self, parameters, board_shape, allowable_false_positives: int, allowable_false_negatives: int):
        self.board_width = board_shape[0]
        self.board_height = board_shape[1]
        self.parameters = parameters
        self.current_state = (None, None, None, None)
        self.allowable_false_positives = allowable_false_positives
        self.allowable_false_negatives = allowable_false_negatives

    def state_value(self, board):
        # Given a board and a list of feature weights (parameters), return the summed "goodness" value of the board
        return sum([feature*weight for feature, weight in zip(get_features(board), self.parameters)])
    
    # Returns a list of all possible placements for the given shape on the given board.
    # Placements are given as a tuple (score, shape, anchor) where those values are the position for the piece and the corresponding score for that position, as decided by this agent
    def get_scored_placements(self, _board, shape):
        placements = []

        # For each orientation of the piece...
        prev_orientations = [] # Keep track of previous orientations to check for duplicates
        for ori in range(4): # Max 4 orientations per shape
            # Check if this orientation has already been seen
            if np.any([np.array_equal(get_shape_grid(shape), prev_shape_grid) for prev_shape_grid in prev_orientations]):
                # This orientation has been seen before (therefore all unique orientations have been seen), so do not continue checking new orientations.
                break
            prev_orientations.append(get_shape_grid(shape))
            
            # For each possible anchor column...
            for x in range(self.board_width):
                board = np.copy(_board)

                # Check if this is a valid placement
                start_height = abs(min(_y for _, _y in shape))
                if not is_occupied(shape, (x, start_height), board):
                    # This is valid placement. Simulate dropping the piece
                    shape, (x,y) = take_action(shape, (x, start_height-1), board, TetrisAction.HARD_DROP)
                    
                    # Successfully hallucinated the dropping of the piece. Evaluate the value of this new board
                    board_val = self.state_value(board)

                    # Add this position and its score to output array
                    placements.append((board_val, shape, (x,y)))
            
            # Rotate the shape
            shape = rotated(shape)
        return placements


    # Takes the actions in order as specified by the input queue. 
    # Returns a tuple containing the list of rewards from the actions in this sequence and a boolean indicating whether or not the game ended during this sequence.
    def take_action_sequence(self, sequence, env):
        done = EndResult.NOT_DONE
        for action in sequence:
            if done == EndResult.NOT_DONE:
                self.current_state, done = env.step(action)
                board, shape, anchor = self.current_state

                # End this sequence early if the piece dropped earlier than expected
                if has_dropped(shape, (int(anchor[0]), int(anchor[1])), board):
                    break
        return done
    
    def did_fail(self, board):
        num_stragglers, num_needed_false_positives = count_stragglers(board)
        num_false_positives = count_false_positives(board)
        return num_false_positives > self.allowable_false_positives or (num_false_positives + num_needed_false_positives > self.allowable_false_positives and num_stragglers > self.allowable_false_negatives)

    def find_placements(self, _board, depth=0):
        # Randomly order the pieces
        piece_order = random.sample(list(pieces.values()), len(list(pieces.values())))

        result = EndResult.NOT_DONE
        sequence = []
        placements = []
        board = np.copy(_board)
        end_board = np.copy(_board)

        # Evaluate end condition
        result = EndResult.FAILURE if self.did_fail(board) else EndResult.NOT_DONE if count_false_negatives(board) > self.allowable_false_negatives else EndResult.SUCCESS

        if result == EndResult.NOT_DONE:
            # Step 1: Determine the scores for all possible placements for all pieces
            for piece in piece_order:
                # Determine all possible placements and their scores
                placements.extend(self.get_scored_placements(board, piece))

            # Step 2: Order the placements by score, but randomize the order of placements with the same score
            placements = sorted(placements, key=lambda x: x[0], reverse=True)
            sorted_placements = []
            current_score = placements[0][0]
            current_group = []
            for placement in placements:
                if placement[0] == current_score:
                    current_group.append(placement)
                else:
                    sorted_placements.extend(random.sample(current_group, len(current_group)))
                    current_group = [placement]
                    current_score = placement[0]
            sorted_placements.extend(current_group)

            # Print the maximum score
            max_score = max(placements, key=lambda x: x[0])[0]

            # Step 3: Try placements in order of best -> least score
            for score, shape, anchor in sorted_placements:
                # Reset the board and sequence (undo anything done in past iterations of this loop)
                board = np.copy(_board)
                sequence = []

                # Build placement object
                placement = (shape, anchor)
                sequence.append(placement)
                # print("placement", score, shape, anchor)

                # Put the shape onto the board (make the placement)
                apply_shape(*placement, board)
                end_board = np.copy(board)

                # print(print_board(board))

                # Re-evaluate end condition
                result = EndResult.FAILURE if count_false_positives(board) > self.allowable_false_positives else EndResult.NOT_DONE if count_false_negatives(board) > self.allowable_false_negatives else EndResult.SUCCESS

                if result == EndResult.NOT_DONE:
                    # Step 3a: Recursive call to find the rest of the sequence
                    result, rest_of_sequence, end_board = self.find_placements(np.copy(board), depth+1)
                    sequence.extend(rest_of_sequence)

                # On success, stop looking (on failure, try next placement)
                if result == EndResult.SUCCESS:
                    break
        return result, sequence, end_board


    def build_animation_from_placements(self, _board, placements):
        frames = []
        board = np.copy(_board)
        for placement in placements:
            # Set the piece
            shape, anchor = set_piece(board, placement[0])   
            # curr_cell_val = board[anchor[0], anchor[1], :]
            # board[placement[1][0], placement[1][1]] = (curr_cell_val[0], curr_cell_val[1], "P")
            frames.append(board[:, :, 2].T.tolist())

            # Find the action sequence
            sequence = generate_action_sequence(placement, board, shape, anchor)

            # Take the actions in the sequence
            for action in sequence:
                shape, anchor = take_action(shape, anchor, board, action)
                frames.append(board[:, :, 2].T.tolist())
        return frames
    
    def run_simulation(self, board):
        result, placements, end_board = self.find_placements(board)
        if result == EndResult.SUCCESS:
            return EndResult.SUCCESS, self.build_animation_from_placements(board, placements)
        else:
            return EndResult.FAILURE, []

