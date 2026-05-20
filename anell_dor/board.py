import numpy as np
from enum import Enum
import random
from aima.search import UndirectedGraph

WIDTH = 12
HEIGHT = 12
COST = 1

class PieceType(Enum):
    EMPTY = 0
    WALL = 1
    BRONZE = 2
    SILVER = 3
    GOLD = 4

class Board():
    def __init__(self):
        self.board = np.zeros((WIDTH, HEIGHT), dtype=int)
        self.coins = {
            PieceType.BRONZE: [],
            PieceType.SILVER: [],
            PieceType.GOLD: []
        }

    def _can_place_wall(self, pos, length, direction):
        for i in range(length):
            target = pos + i * direction
            if target[0] >= WIDTH or target[1] >= HEIGHT or target[0] < 0 or target[1] < 0:
                return False
            if self.board[target[1], target[0]] != PieceType.EMPTY.value:
                return False
        return True

    def _populate_walls(self):
        wall_lengths = [5, 4, 3, 3, 3]
        for length in wall_lengths:
            can_place = False
            while not can_place:
                pos = np.array([random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)])
                dir = np.array([0, 0])
                while np.all(dir == 0):
                    dir = np.array([random.randint(-1, 1), random.randint(-1, 1)])
                can_place = self._can_place_wall(pos, length, dir)
            
            for i in range(length):
                target = pos + i * dir
                self.board[target[1], target[0]] = PieceType.WALL.value

    def _populate_coins(self):
        coins = [6, 3, 1]
        coin_types = [PieceType.BRONZE, PieceType.SILVER, PieceType.GOLD]

        for i, coin_type in enumerate(coin_types):
            for j in range(coins[i]):
                while True:
                    pos = np.array([random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)])
                    if self.board[pos[1], pos[0]] == PieceType.EMPTY.value:
                        self.board[pos[1], pos[0]] = coin_type.value
                        self.coins[coin_type].append(pos)
                        break

    def populate(self):
        self._populate_walls()
        self._populate_coins()

    def get_valid_spawn_pos(self):
        pos = None
        while True:
            pos = np.array([random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)])
            if self.board[pos[1], pos[0]] == PieceType.EMPTY.value:
                break
        return pos

    def remove_coin(self, pos, coin_type):
        self.board[pos[1], pos[0]] = PieceType.EMPTY.value
        new_coins = []
        for c in self.coins[coin_type]:
            if not (c[0] == pos[0] and c[1] == pos[1]):
                new_coins.append(c)
        self.coins[coin_type] = new_coins

    def to_graph(self, current_coin: PieceType):
        graph_dict = {}
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.board[y, x] == PieceType.WALL.value:
                    continue

                graph_dict[(x, y)] = {}
                for j in range(y - 1, y + 2):
                    for i in range(x - 1, x + 2):
                        if x == i and y == j: continue
                        if i < 0 or i >= WIDTH: continue
                        if j < 0 or j >= HEIGHT: continue
                        if abs(i - x) == 1 and abs(j - y) == 1: continue
                        if self.board[j, i] == PieceType.WALL.value: continue

                        graph_dict[(x, y)][(i, j)] = COST
        
        graph = UndirectedGraph(graph_dict)
        return graph

