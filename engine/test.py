import sys, json
import numpy as np
from tetris_env import board_from_grid, print_board, count_stragglers
from tetris_agent import TetrisAgent
from utils import log, send

# simple JSON echo script
for line in sys.stdin:
  in_msg = json.loads(line)

arr = np.asarray(in_msg["grid"])
false_positives = in_msg["false_positives"]
false_negatives = in_msg["false_negatives"]
log("Running...", false_positives, false_negatives)

board = board_from_grid(arr)
agent = TetrisAgent([-1, -1, -1], board.shape, 0, 0)
result, animation = agent.run_simulation(board)
data = {}
data["frames"] = animation
send(data)