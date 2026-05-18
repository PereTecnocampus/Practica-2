from aima.search import GraphProblem, astar_search
from board import Board, PieceType

class BoardGraphProblem(GraphProblem):
    def __init__(self, initial, goal, graph):
        super().__init__(initial, goal, graph)
    
    def h(self, node):
        """h function is manhattan distance from a node's state to goal."""
        node_pos = node.state
        return abs(node_pos[0] - self.goal[0]) + abs(node_pos[1] - self.goal[1])


if __name__ == "__main__":
    board = Board()
    board.populate()
    graph = board.to_graph()

    coin = tuple(board.coins[PieceType.GOLD][0])
    spawn_pos = tuple(board.get_valid_spawn_pos())

    problem = BoardGraphProblem(
        spawn_pos,
        coin,
        graph
    )

    final_node = astar_search(problem)
    print(board.board)
    print(spawn_pos)
    print(coin)
    print(graph.get(tuple(spawn_pos)))
    print(final_node)
    print(final_node.solution())