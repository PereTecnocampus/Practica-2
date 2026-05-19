from aima.search import GraphProblem, astar_search
from board import Board, PieceType
import itertools

class BoardGraphProblem(GraphProblem):
    def __init__(self, initial, goal, graph):
        super().__init__(initial, goal, graph)
    
    def h(self, node):
        """h function is manhattan distance from a node's state to goal."""
        node_pos = node.state
        return abs(node_pos[0] - self.goal[0]) + abs(node_pos[1] - self.goal[1])

def get_path(start, goal, graph, cache={}):
    """Finds shortest path from start to goal using A* search. Saves results in cache to avoid calculations that have already been performed."""
    if (start, goal) in cache:
        return cache[(start, goal)]
    
    problem = BoardGraphProblem(start, goal, graph)
    result = astar_search(problem)

    if result is None:
        """No path found."""
        cache[(start, goal)] = ([], float('inf'), [])
    else:
        path=result.solution()
        cost=result.path_cost
        cache[(start, goal)] = (cost, path)
    
    return cache[(start, goal)]

def find_best_route(board: Board, spawn_pos):
    """Finds the shortest path respecting the hierarchy of coins (bronze -> silver -> gold)."""
    
    bronze_coins = [(int(c[0]), int(c[1])) for c in board.coins[PieceType.BRONZE]]
    silver_coins = [(int(c[0]), int(c[1])) for c in board.coins[PieceType.SILVER]]
    gold_coin = (int(board.coins[PieceType.GOLD][0][0]), int(board.coins[PieceType.GOLD][0][1]))

    cache = {}
    best_cost = float('inf')
    best_full_path = []
    best_sequence = []

    """Generate all possible combinations to grab all coins of every type respecting the hierarchy."""
    bronze_perms = list(itertools.permutations(bronze_coins))
    silver_perms = list(itertools.permutations(silver_coins))

    """Iterate through all possible combinations and calculate the total cost of the path.
       If the path is valid and has a lower cost than the best cost found so far, update the best cost and path."""
    
    graphs = {
        PieceType.BRONZE: board.to_graph(PieceType.BRONZE),
        PieceType.SILVER: board.to_graph(PieceType.SILVER),
        PieceType.GOLD: board.to_graph(PieceType.GOLD)
    }

    for bronze_seq in bronze_perms:
        for silver_seq in silver_perms:

            sequence = [spawn_pos] + list(bronze_seq) + list(silver_seq) + [gold_coin]
            bronze_len = len(list(bronze_seq))
            silver_len = len(list(silver_seq))
            
            current_cost = 0
            current_full_path = []
            valid = True
            
            for i in range(len(sequence) - 1):
                next_idx = i + 1
                start_node = sequence[i]
                end_node = sequence[next_idx]

                target_type = PieceType.GOLD
                if next_idx <= bronze_len:
                    target_type = PieceType.BRONZE
                elif next_idx <= silver_len:
                    target_type = PieceType.SILVER

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

if __name__ == "__main__":
    board = Board()
    
    result = None

    while result == None:
        board.populate()

        raw_spawn = board.get_valid_spawn_pos()
        spawn_pos = (int(raw_spawn[0]), int(raw_spawn[1]))
        
        result = find_best_route(board, spawn_pos)

    total_cost, full_path, sequence = result

    print("ESTAT DEL TAULER (0=Buit, 1=Paret, 2=Bronze, 3=Plata, 4=Or):")
    print(board.board)
    print(f"\nPosició Inicial (Jugador): {spawn_pos}")

    print(f"\nCOST MÍNIM TOTAL: {total_cost} passos.")
    print(f"ORDRE D'OBJECTIUS: {sequence}")
    print(f"RUTA COMPLETA DE MOVIMENTS: {full_path}")