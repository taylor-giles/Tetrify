import sys, json
import numpy as np
from tetris_env import board_from_grid, print_board, count_stragglers
from tetris_agent import TetrisAgent
from utils import log, send
import time

# simple JSON echo script
for line in sys.stdin:
  in_msg = json.loads(line)

arr = np.asarray(in_msg["grid"])
false_positives = in_msg["false_positives"]
false_negatives = in_msg["false_negatives"]
enforce_gravity = in_msg["enforce_gravity"]
log("Running...")

start_time = time.perf_counter()
board = board_from_grid(arr)
agent = TetrisAgent([-1, -1, -1], board.shape, false_positives, false_negatives, enforce_gravity)
result, animation = agent.run_simulation(board)
data = {}
data["frames"] = animation
log(time.perf_counter() - start_time)
send(data)