import sys, json
import numpy as np
from tetris_env import board_from_grid, print_board, count_stragglers
from tetris_agent import TetrisAgent
from utils import log, send

# simple JSON echo script
for line in sys.stdin:
  arr = np.asarray(json.loads(line))

log("Running...")

board = board_from_grid(arr)
agent = TetrisAgent([-1, -1, -1], board.shape, 0, 0)
result, animation = agent.run_simulation(board)
data = {}
data["frames"] = animation
send(data)