from board import Board
from searcher import find_best_route
import numpy as np

class Game:
    def __init__(self):
        self.board = None
        self.player_pos = np.array([0, 0])
        self.initial_best_route = None
        self.best_route = None

    def _update_best_route(self):
        self.best_route = find_best_route(self.board, tuple(self.player_pos))

    def _init_board(self):
        self.board = Board()

        result = None

        while result == None:
            self.board.populate()

            raw_spawn = self.board.get_valid_spawn_pos()
            spawn_pos = (int(raw_spawn[0]), int(raw_spawn[1]))
            self.player_pos = np.array(spawn_pos)
            
            result = find_best_route(self.board, spawn_pos)

        total_cost, full_path, sequence = result
        self.best_route = (total_cost, full_path, sequence)
        self.initial_best_route = self.best_route

    def get_piece(self, x, y):
        return self.board.board[y, x]

    def start(self):
        self._init_board()

    def move_player(self, direction: np.ndarray):
        self.player_pos += direction
        self._update_best_route()