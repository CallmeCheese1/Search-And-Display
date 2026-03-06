from collections import deque
from environment import NodeType, Grid, Node
from binary_tree import VisualizationTree

class BFS_SearchAgent:
    """A search agent that relies on Breadth-First Search, given the grid and the start node. Call step() for me to move through BFS step by step, marking Nodes along the way. Once is_finished becomes true, either my .path will have a path, or it'll be an empty list, if I couldn't find a path."""

    def __init__(self, grid, start_node):
        self.grid = grid

        self.frontier = deque([start_node])
        self.visited = set()
        self.tree = VisualizationTree(start_node)

        self.is_finished = False
        self.path = []
    
    def step(self):
        """Move forward one step, based on the BFS algorithm. Won't run if is_finished is set to true, and at that point, either I'll have a finished path in .path, or I'll have an empty path if there's no hope."""

        #If we're finished, or we don't even have a frontier anymore, and this function gets called, mark that we're finished. 
        if self.is_finished or not self.frontier:
            self.is_finished = True
            return
        
        #Just like normal, we take our first node by looking at the firs tone in the queue.
        current_node = self.frontier.popleft()

        #Are we at a duplicate? Return! Where to? Dunno!
        if current_node in self.visited:
            return
        
        self.visited.add(current_node)

        #Mark that we're touching these nodes, but if it's our goal, create the path that we found from start to finish!
        if current_node.type == NodeType.EMPTY:
            current_node.type = NodeType.MARKED
        
        if current_node.type == NodeType.GOAL:
            self.is_finished = True
            self.path = self._reconstruct_path(current_node)
            print(self.tree)
            return

        #At the end of the day, if we're still here, go ahead and queue up the rest of the nearby neighbors. Check it's not in visited, and then add it to the END of our queue.
        for neighbor in self.grid.get_neighbors(current_node):
            if neighbor not in self.visited:

                neighbor.parent = current_node

                self.tree.add_edge(current_node, neighbor)

                self.frontier.append(neighbor)
                
    def _reconstruct_path(self, goal_node):
        """Helper to walk the parents backwards once finished."""
        path = []
        curr = goal_node
        while curr is not None:
            path.insert(0, curr)
            curr = curr.parent
        return path