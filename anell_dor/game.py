from board import Board
from searcher import find_best_route
import numpy as np

class Game:
    def __init__(self):
        self.board = None
        self.player_pos = np.array([0, 0])

    def _init_board(self):
        self.board = Board()

        result = None

        while result == None:
            self.board.populate()

            raw_spawn = self.board.get_valid_spawn_pos()
            spawn_pos = (int(raw_spawn[0]), int(raw_spawn[1]))
            
            result = find_best_route(self.board, spawn_pos)

        total_cost, full_path, sequence = result

    def start(self):
        self._init_board()