import sys, json
import numpy as np
from tetris_env import board_from_grid, print_board, count_stragglers
from tetris_agent import TetrisAgent
from utils import log, send

# Read JSON input
for line in sys.stdin:
  in_msg = json.loads(line)

# Parse JSON input
arr = np.asarray(in_msg["grid"])
false_positives = in_msg["false_positives"]
false_negatives = in_msg["false_negatives"]
enforce_gravity = in_msg["enforce_gravity"]
reduce_Is = in_msg["reduce_Is"]
log("Running...")

def send_frames(animation):
  data = {}
  data["frames"] = animation
  send(data)

# Build agent and run simulation
sys.setrecursionlimit(2000)
board = board_from_grid(arr)
agent = TetrisAgent(board.shape, false_positives, false_negatives, enforce_gravity, reduce_Is)
result, animation = agent.run_simulation(board, board, on_success=send_frames)