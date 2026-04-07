from enum import Enum
import random
import networkx as nx

class NodeType(Enum):
    EMPTY = 0
    WALL = 1
    START = 2
    GOAL = 3
    MARKED = 4
    PATH = 5

class GraphEnvironment:
    """Represents the graph space for pathfinding using NetworkX."""
    
    def __init__(self, size=10, seed=None):
        self.size = size
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # Grid graph for Phase 1
        self.graph = nx.grid_2d_graph(size, size)
        self.start_node = None
        self.goal_node = None
        
        # Initialize default types
        for n in self.graph.nodes:
            self.graph.nodes[n]['type'] = NodeType.EMPTY
            
        self._place_start_and_goal()
        self._generate_walls()
        
    def _place_start_and_goal(self):
        nodes = list(self.graph.nodes)
        positions = random.sample(nodes, 2)
        
        self.start_node = positions[0]
        self.goal_node = positions[1]
        
        self.graph.nodes[self.start_node]['type'] = NodeType.START
        self.graph.nodes[self.goal_node]['type'] = NodeType.GOAL

    def _generate_walls(self):
        # We find empty nodes for walls
        nodes = [n for n in self.graph.nodes if self.graph.nodes[n]['type'] == NodeType.EMPTY]
        num_walls = int(len(nodes) * 0.25)
        wall_nodes = random.sample(nodes, num_walls)
        
        for n in wall_nodes:
            self.graph.nodes[n]['type'] = NodeType.WALL

    def get_node(self, row, column):
        if (row, column) in self.graph:
            return (row, column)
        return None

    def get_node_type(self, node):
        if node and node in self.graph:
            return self.graph.nodes[node]['type']
        return None

    def get_neighbors(self, node):
        neighbors = []
        if node in self.graph:
            for n in self.graph.neighbors(node):
                if self.graph.nodes[n]['type'] != NodeType.WALL:
                    neighbors.append(n)
        return neighbors

if __name__ == "__main__":
    print("=== Phase 1 Decoupling Test ===")
    env = GraphEnvironment(10)
    print(f"Nodes in graph: {env.graph.number_of_nodes()}")
    print(f"Start: {env.start_node}, Goal: {env.goal_node}")
    print(f"Neighbors around Start: {env.get_neighbors(env.start_node)}")