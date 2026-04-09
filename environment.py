from enum import Enum
import random
import networkx as nx

class GraphTopology(Enum):
    GRID = 0
    TREE = 1
    CSV = 2

class NodeType(Enum):
    EMPTY = 0
    WALL = 1
    START = 2
    GOAL = 3
    MARKED = 4
    PATH = 5

#Ever since Part A of the project, yes, this file is STILL all the graph logic! Utilizes networkx to keep track of the grid or node space for pathfinding. If this environment is created in Grid mode, it's a grid. If it's created in tree mode, it's a tree. If we activate it in CSV mode, it parses and loads from the CSV IN THE SAME DIRECTORY and makes it into a tree.
class GraphEnvironment:
    """Represents the graph space for pathfinding using NetworkX."""
    
    def __init__(self, size=None, seed=None, obstacle_rate=0.25, topology=GraphTopology.GRID, branching_factor=2):
        self.topology = topology
        self.size = size if size is not None else 10
        self.seed = seed
        self.node_positions = {}
        if seed is not None:
            random.seed(seed)
            try:
                import numpy as np
                np.random.seed(seed)
            except ImportError:
                pass
        
        self.start_node = None
        self.goal_node = None
        
        if self.topology == GraphTopology.GRID:
            self.graph = nx.grid_2d_graph(self.size, self.size)
            for n in self.graph.nodes:
                self.graph.nodes[n]['type'] = NodeType.EMPTY
            self._place_start_and_goal()
            self._generate_walls(obstacle_rate)
            
        elif self.topology == GraphTopology.TREE:
            self.graph = nx.barabasi_albert_graph(int(self.size), min(int(branching_factor), int(self.size)-1), seed=seed)
            
            pos = nx.spring_layout(self.graph, seed=seed)
            if pos:
                min_x = min([p[0] for p in pos.values()])
                max_x = max([p[0] for p in pos.values()])
                min_y = min([p[1] for p in pos.values()])
                max_y = max([p[1] for p in pos.values()])
                
                range_x = max_x - min_x if max_x > min_x else 1.0
                range_y = max_y - min_y if max_y > min_y else 1.0
                
                for n, p in pos.items():
                    nx_val = 0.05 + 0.9 * ((p[0] - min_x) / range_x)
                    ny_val = 0.05 + 0.9 * ((p[1] - min_y) / range_y)
                    self.node_positions[n] = (float(nx_val), float(ny_val))
            
            for n in self.graph.nodes:
                self.graph.nodes[n]['type'] = NodeType.EMPTY
            
            # Assign random weights to edges
            for u, v in self.graph.edges:
                self.graph[u][v]['weight'] = random.randint(1, 10)
            
            self._place_start_and_goal()
            
        elif self.topology == GraphTopology.CSV:
            self.graph = nx.Graph()
            
            try:
                import os
                if os.path.exists('coordinates.csv'):
                    with open('coordinates.csv', 'r') as f:
                        for line in f:
                            parts = line.strip().split(',')
                            if len(parts) >= 3:
                                name = parts[0].strip()
                                lat = float(parts[1].strip())
                                lon = float(parts[2].strip())
                                self.graph.add_node(name)
                                self.node_positions[name] = (lon, lat)
                                
                if os.path.exists('Adjacencies.txt'):
                    with open('Adjacencies.txt', 'r') as f:
                        for line in f:
                            parts = line.split()
                            if len(parts) > 1:
                                source = parts[0]
                                for dest in parts[1:]:
                                    self.graph.add_edge(source, dest)
                
                # Assign distance-based weights to CSV edges
                import math
                for u, v in self.graph.edges:
                    if u in self.node_positions and v in self.node_positions:
                        p1 = self.node_positions[u]
                        p2 = self.node_positions[v]
                        dist = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
                        self.graph[u][v]['weight'] = max(1, round(dist * 50))
            except Exception as e:
                print(f"Error parsing CSV/TXT files: {e}")
                
            if self.node_positions:
                min_x = min([p[0] for p in self.node_positions.values()])
                max_x = max([p[0] for p in self.node_positions.values()])
                min_y = min([p[1] for p in self.node_positions.values()])
                max_y = max([p[1] for p in self.node_positions.values()])
                
                range_x = max_x - min_x if max_x > min_x else 1.0
                range_y = max_y - min_y if max_y > min_y else 1.0
                
                # Normalize and invert Y for Pygame coordinate space (0=top)
                for n, p in self.node_positions.items():
                    nx_val = 0.05 + 0.9 * ((p[0] - min_x) / range_x)
                    ny_val = 0.05 + 0.9 * (1.0 - ((p[1] - min_y) / range_y))
                    self.node_positions[n] = (float(nx_val), float(ny_val))
                    
                # Collision resolution for overlapping city plates
                import math
                for _ in range(100):
                    moved = False
                    for n1 in self.graph.nodes:
                        for n2 in self.graph.nodes:
                            if n1 < n2 and n1 in self.node_positions and n2 in self.node_positions:
                                p1 = self.node_positions[n1]
                                p2 = self.node_positions[n2]
                                dist = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
                                min_dist = 0.075 # Threshold padding based on string render width roughly
                                if dist < min_dist:
                                    if dist == 0:
                                        dx, dy = 0.01, 0.01
                                        dist = 0.014
                                    else:
                                        dx = p1[0] - p2[0]
                                        dy = p1[1] - p2[1]
                                    push = (min_dist - dist) / 2
                                    # Dampen x and y pushing slightly
                                    self.node_positions[n1] = (p1[0] + (dx/dist)*push, p1[1] + (dy/dist)*push)
                                    self.node_positions[n2] = (p2[0] - (dx/dist)*push, p2[1] - (dy/dist)*push)
                                    moved = True
                    if not moved:
                        break
            for n in self.graph.nodes:
                if 'type' not in self.graph.nodes[n]:
                    self.graph.nodes[n]['type'] = NodeType.EMPTY
                    
            if len(self.graph.nodes) >= 2:
                self._place_start_and_goal()
        
    def _place_start_and_goal(self):
        nodes = list(self.graph.nodes)
        positions = random.sample(nodes, 2)
        
        self.start_node = positions[0]
        self.goal_node = positions[1]
        
        self.graph.nodes[self.start_node]['type'] = NodeType.START
        self.graph.nodes[self.goal_node]['type'] = NodeType.GOAL

    def _generate_walls(self, obstacle_rate):
        # We find empty nodes for walls
        nodes = [n for n in self.graph.nodes if self.graph.nodes[n]['type'] == NodeType.EMPTY]
        num_walls = int(len(nodes) * obstacle_rate)
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