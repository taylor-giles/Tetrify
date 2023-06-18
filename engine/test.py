import sys, json
import numpy as np
from tetris_env import board_from_grid, print_board
from tetris_agent import TetrisAgent

# simple JSON echo script
for line in sys.stdin:
  arr = np.asarray(json.loads(line))

print("Running...", flush=True)

board = board_from_grid(arr)
agent = TetrisAgent([-1, -1, -1], board.shape, 0, 0)
result, animation = agent.run_simulation(board)
data = {}
data["frames"] = animation
print(json.dumps(data), flush=True)