from collections import deque
from environment import NodeType
from binary_tree import VisualizationTree

#Oh, this class. Uses Iterative Deepening Depth-First Search, so it limits itself to checking at each depth before it checks deeper. As that implies, that requires a lot of calculations. As THAT implies, in the initial implementations, it kept crashing the program twice due to errors with how we handled programming the depth limits and node checking. But it's all good now!
#...hopefully.

class IDDFS_SearchAgent:
    """Iterative Deepening Depth-First Search implementation."""
    
    def __init__(self, grid, start_node):
        self.grid = grid
        self.start_node = start_node
        self.depth_limit = 0
        
        self.tree = VisualizationTree(start_node)
        self.is_finished = False
        self.path = []
        self.current_node = start_node
        self.view_root = start_node
        self.max_depth_reached_in_iteration = 0
        
        self.global_min_depths = {start_node: 0}
        self.visited = set()
        
        self._initialize_iteration()

    def _initialize_iteration(self):
        """Reset internal structures for a new deeper iteration limit."""
        # stack stores: (node, depth)
        self.frontier = [(self.start_node, 0)]
        self.visited_depths = {self.start_node: 0} 
        self.parents = {self.start_node: None}
        self.max_depth_reached_in_iteration = 0

    def step(self):
        steps_taken = 0
        # Compute up to 50 redundant internal steps to fast-forward execution visually
        while steps_taken < 50:
            if self.is_finished:
                return
            if not self.frontier:
                if self.max_depth_reached_in_iteration < self.depth_limit:
                    self.is_finished = True
                    self.path = []
                    return
                self.depth_limit += 1
                self._initialize_iteration()
                return
                
            current_node, current_depth = self.frontier.pop()
            
            if current_depth > self.max_depth_reached_in_iteration:
                self.max_depth_reached_in_iteration = current_depth
                
            self.current_node = current_node
            
            self.visited.add(current_node)
            
            if self.grid.get_node_type(current_node) == NodeType.GOAL:
                self.is_finished = True
                self.path = self._reconstruct_path(current_node)
                return

            if current_depth < self.depth_limit:
                for neighbor in self.grid.get_neighbors(current_node):
                    next_depth = current_depth + 1
                    
                    # Global pruning: if we've reached this node in ANY iteration at a strictly better depth,
                    # this path is a suboptimal cycle. Prune!
                    if next_depth > self.global_min_depths.get(neighbor, float('inf')):
                        continue
                        
                    if next_depth < self.global_min_depths.get(neighbor, float('inf')):
                        self.global_min_depths[neighbor] = next_depth
                    
                    # Expand if unexplored in this iteration OR if we found a strictly shorter path to it.
                    if neighbor not in self.visited_depths or next_depth < self.visited_depths[neighbor]:
                        self.visited_depths[neighbor] = next_depth
                        self.parents[neighbor] = current_node
                        self.tree.add_edge(current_node, neighbor)
                        self.frontier.append((neighbor, next_depth))

            # Only yield to Pygame rendering if we've reached the very outer edge of our search limit
            if current_depth == self.depth_limit:
                break
                
            steps_taken += 1

    def _reconstruct_path(self, goal_node):
        path = []
        curr = goal_node
        while curr is not None:
            path.insert(0, curr)
            curr = self.parents.get(curr)
        return path
