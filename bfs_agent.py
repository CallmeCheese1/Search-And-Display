from collections import deque
from environment import NodeType
from binary_tree import VisualizationTree

class BFS_SearchAgent:
    def __init__(self, grid, start_node):
        self.grid = grid
        self.frontier = deque([start_node])
        self.visited = set()
        self.tree = VisualizationTree(start_node)
        self.is_finished = False
        self.path = []
        self.parents = {start_node: None}
        self.current_node = start_node
        self.view_root = start_node
        self.max_memory_nodes = 0
    
    def step(self):
        if self.is_finished or not self.frontier:
            self.is_finished = True
            return
        
        self.max_memory_nodes = max(self.max_memory_nodes, len(self.frontier) + len(self.visited))
        
        current_node = self.frontier.popleft()
        self.current_node = current_node

        if current_node in self.visited:
            return
            
        self.visited.add(current_node)
        
        if self.grid.get_node_type(current_node) == NodeType.GOAL:
            self.is_finished = True
            self.path = self._reconstruct_path(current_node)
            return

        for neighbor in self.grid.get_neighbors(current_node):
            if neighbor not in self.visited and neighbor not in self.parents:
                self.parents[neighbor] = current_node
                self.tree.add_edge(current_node, neighbor)
                self.frontier.append(neighbor)
                
    def _reconstruct_path(self, goal_node):
        path = []
        curr = goal_node
        while curr is not None:
            path.insert(0, curr)
            curr = self.parents.get(curr)
        return path