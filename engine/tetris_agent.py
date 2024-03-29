import numpy as np
import random
from tetris_env import TetrisAction, SimulationResult, set_piece, get_shape_grid, is_occupied, has_dropped, rotated, count_stragglers, count_wells, count_towers, count_false_positives, count_false_negatives, count_buried_false_negatives, pieces, apply_shape, take_action
from utils import log
from collections.abc import Callable

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
    while anchor[1] < placement_anchor[1] and not has_dropped(shape, anchor, board):
        anchor = (placement_anchor[0], anchor[1]+1)
        sequence.append(TetrisAction.SOFT_DROP)

    return sequence


class TetrisAgent:
    def __init__(self, board_shape, allowable_false_positives: int, allowable_false_negatives: int, enforce_gravity=True, reduce_Is=True):
        self.board_width = board_shape[0]
        self.board_height = board_shape[1]
        self.current_state = (None, None, None, None)
        self.allowable_false_positives = allowable_false_positives
        self.allowable_false_negatives = allowable_false_negatives
        self.enforce_gravity = enforce_gravity

        # List of features to be used to evaluate state values
        self.features: list = [count_false_positives, count_false_negatives, count_buried_false_negatives]
        if reduce_Is:
            self.features = [*self.features, count_wells, count_towers]
        
        # Parameters (each feature is weighted equally negatively)
        # NOTE - If any ML were to be introduced to this project, optimizing these weights would be a good starting point
        self.parameters = [-1 for _ in self.features]

    def get_features(self, _board):
        # Copy the board
        board = np.copy(_board)

        # Given a board, return the values of each feature of that board
        return [feature(board) for feature in self.features]


    def state_value(self, board):
        # Given a board and a list of feature weights (parameters), return the summed "goodness" value of the board
        return sum([feature*weight for feature, weight in zip(self.get_features(board), self.parameters)])
    
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
                    if self.enforce_gravity:
                        # Gravity is enforced, so hard dropping is acceptable
                        shape, (x,y) = take_action(shape, (x, start_height-1), board, TetrisAction.HARD_DROP)
                    
                        # Successfully hallucinated the dropping of the piece. Evaluate the value of this new board
                        board_val = self.state_value(board)

                        # Add this position and its score to output array iff its placement would not cause failure
                        if not self.did_fail(board):
                            placements.append((board_val, shape, (x,y)))
                    else:
                        # Add a placement for every possible height of this piece (gravity not enforced)
                        y = start_height-1
                        while not has_dropped(shape, (x,y), board):
                            y += 1
                            apply_shape(shape, (x,y), board, True)

                            # Successfully hallucinated the dropping of the piece. Evaluate the value of this new board
                            board_val = self.state_value(board)

                            # Add this position and its score to output array iff its placement would not cause failure
                            if not self.did_fail(board):
                                placements.append((board_val, shape, (x,y)))

                            # Reset board (must be done here, BEFORE while condition is checked)
                            board = np.copy(_board)
            # Rotate the shape
            shape = rotated(shape)
        # log(len(placements))
        return placements
    
    def did_fail(self, board):
        num_stragglers, num_needed_false_positives = count_stragglers(board)
        num_false_positives = count_false_positives(board)
        return num_false_positives > self.allowable_false_positives or (num_false_positives + num_needed_false_positives > self.allowable_false_positives and num_stragglers > self.allowable_false_negatives)

    def run_simulation(self, orig_board: np.ndarray, _board: np.ndarray, on_success: Callable[[tuple], None], prev_sequence=[], depth=0):
        # Randomly order the pieces
        piece_order = random.sample(list(pieces.values()), len(list(pieces.values())))

        result = SimulationResult.NOT_DONE
        sequence = []
        placements = []
        board = np.copy(_board)

        # Evaluate end condition
        result = SimulationResult.FAILURE if self.did_fail(board) else SimulationResult.NOT_DONE if count_false_negatives(board) > self.allowable_false_negatives else SimulationResult.SUCCESS

        if result == SimulationResult.NOT_DONE:
            # Step 1: Determine the scores for all possible placements for all pieces
            for piece in piece_order:
                # Determine all possible placements and their scores
                placements.extend(self.get_scored_placements(board, piece))

            # If there are no placements, return failure
            if len(placements) == 0:
                return SimulationResult.FAILURE, []
            
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
            #max_score = max(placements, key=lambda x: x[0])[0]

            # Step 3: Try placements in order of best -> least score
            for score, shape, anchor in sorted_placements:
                # Reset the board and sequence (undo anything done in past iterations of this loop)
                board = np.copy(_board)
                sequence = []

                # Build placement object
                placement = (shape, anchor)
                sequence.append(placement)

                # Put the shape onto the board (make the placement)
                apply_shape(*placement, board, not self.enforce_gravity)

                # Re-evaluate end condition
                result = SimulationResult.FAILURE if count_false_positives(board) > self.allowable_false_positives else SimulationResult.NOT_DONE if count_false_negatives(board) > self.allowable_false_negatives else SimulationResult.SUCCESS

                if result == SimulationResult.NOT_DONE:
                    # Step 3a: Recursive call to find the rest of the sequence
                    result, rest_of_sequence = self.run_simulation(orig_board, board, on_success, [*prev_sequence, *sequence], depth+1)
                    sequence.extend(rest_of_sequence)

                # On success, trigger on_success function
                if result == SimulationResult.SUCCESS:
                    on_success(self.build_animation_from_placements(np.copy(orig_board), [*prev_sequence, *sequence]))
                    result = SimulationResult.FAILURE
        return result, sequence


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
            apply_shape(shape, anchor, board, True)
        return frames
    
    # def run_simulation(self, board):
    #     result, placements = self.find_placements(board)
    #     if result == SimulationResult.SUCCESS:
    #         return SimulationResult.SUCCESS, self.build_animation_from_placements(board, placements)
    #     else:
    #         return SimulationResult.FAILURE, []

