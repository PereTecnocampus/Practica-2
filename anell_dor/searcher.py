from aima.search import GraphProblem, astar_search
from board import Board, PieceType
import itertools

class BoardGraphProblem(GraphProblem):
    def __init__(self, initial, goal, graph):
        super().__init__(initial, goal, graph)
    
    def h(self, node):
        node_pos = node.state
        return abs(node_pos[0] - self.goal[0]) + abs(node_pos[1] - self.goal[1])

def get_path(start, goal, graph, cache={}):
    if (start, goal) in cache:
        return cache[(start, goal)]
    
    problem = BoardGraphProblem(start, goal, graph)
    result = astar_search(problem)

    if result is None:
        cache[(start, goal)] = ([], float('inf'), [])
    else:
        path = result.solution()
        cost = result.path_cost
        cache[(start, goal)] = (cost, path)
    
    return cache[(start, goal)]

def find_best_route(board: Board, spawn_pos):
    bronze_coins = [(int(c[0]), int(c[1])) for c in board.coins[PieceType.BRONZE]]
    silver_coins = [(int(c[0]), int(c[1])) for c in board.coins[PieceType.SILVER]]
    
    gold_coin_list = board.coins[PieceType.GOLD]
    if not gold_coin_list:
        return 0, [], [] 
    gold_coin = (int(gold_coin_list[0][0]), int(gold_coin_list[0][1]))

    cache = {}
    best_cost = float('inf')
    best_full_path = []
    best_sequence = []

    bronze_perms = list(itertools.permutations(bronze_coins))
    silver_perms = list(itertools.permutations(silver_coins))
    if not bronze_perms: bronze_perms = [()]
    if not silver_perms: silver_perms = [()]

    graphs = {
        PieceType.BRONZE: board.to_graph(PieceType.BRONZE),
        PieceType.SILVER: board.to_graph(PieceType.SILVER),
        PieceType.GOLD: board.to_graph(PieceType.GOLD)
    }

    for bronze_seq in bronze_perms:
        for silver_seq in silver_perms:
            sequence = [spawn_pos] + list(bronze_seq) + list(silver_seq) + [gold_coin]
            
            current_cost = 0
            current_full_path = [spawn_pos] 
            valid = True
            
            for i in range(len(sequence) - 1):
                next_idx = i + 1
                start_node = sequence[i]
                end_node = sequence[next_idx]

                if next_idx <= len(bronze_coins):
                    target_type = PieceType.BRONZE
                elif next_idx <= len(bronze_coins) + len(silver_coins):
                    target_type = PieceType.SILVER
                else:
                    target_type = PieceType.GOLD

                graph = graphs[target_type]
                result = get_path(start_node, end_node, graph, cache=cache)
                
                if result == ([], float('inf'), []):
                    return None

                cost, path = result

                if cost == float('inf'):
                    valid = False
                    break
                    
                current_cost += cost
                current_full_path.extend(path)
                
                if current_cost >= best_cost:
                    valid = False
                    break
            
            if valid and current_cost < best_cost:
                best_cost = current_cost
                best_full_path = current_full_path
                best_sequence = sequence
                
    return best_cost, best_full_path, best_sequence