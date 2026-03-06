from collections import deque
from environment import NodeType, Grid, Node

class BFS_SearchAgent:

    def __init__(self, grid, start_node):
        self.grid = grid

        self.frontier = deque([start_node])
        self.visited = set()

        self.is_finished = False
        self.path = []
    
    def step(self):
        """Move forward one step, based on the BFS algorithm."""

        #If we're finished, or we don't even have a frontier anymore, and this function gets called, mark that we're finished. 
        if self.is_finished or not self.frontier:
            self.is_finished = True
            return
        
        #Just like normal
        current_node = self.frontier.popleft()

        if current_node in self.visited:
            return #we're at a duplicate! so we go back.
        
        self.visited.add(current_node)

        if current_node.type == NodeType.EMPTY:
            current_node.type = NodeType.MARKED
        
        if current_node.type == NodeType.GOAL:
            self.is_finished = True
            self.path = self.reconstruct_path(current_node)
            return
    
        for neighbor in self.grid.get_neighbors(current_node):
            if neighbor not in self.visited:
                neighbor.parent = current_node
                self.frontier.append(neighbor)
                
    def _reconstruct_path(self, goal_node):
        """Helper to walk the parents backwards once finished."""
        path = []
        curr = goal_node
        while curr is not None:
            path.insert(0, curr)
            curr = curr.parent
        return path