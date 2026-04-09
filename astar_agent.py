import heapq
from environment import NodeType
from binary_tree import VisualizationTree

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def euclidean_distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5

class AStar_SearchAgent:
    """A* Search implementation combining path cost (g) and a Greedy Best-First heuristic estimate (h) via Priority Queue."""
    
    def __init__(self, grid, start_node, use_euclidean=False):
        self.grid = grid
        self.goal_node = grid.goal_node
        self.use_euclidean = use_euclidean
        self.counter = 0
        
        self.g_scores = {start_node: 0}
        h = self._get_heuristic(start_node)
        
        # frontier elements: (f_score, tie_breaker, node)
        self.frontier = [(h, self.counter, start_node)]
        self.visited = set()
        
        self.tree = VisualizationTree(start_node)
        self.is_finished = False
        self.path = []
        self.parents = {start_node: None}
        self.current_node = start_node
        self.view_root = start_node
        self.max_memory_nodes = 0
    
    #Our primary heuristic: returns the distance between us and the particular node we're looking for. Usually, it's gonna be between us and the goal.
    def _get_heuristic(self, node):
        if getattr(self.grid, 'topology', None) and self.grid.topology.name in ('TREE', 'CSV'):
            p1 = self.grid.node_positions[node]
            p2 = self.grid.node_positions[self.goal_node]
        else:
            p1, p2 = node, self.goal_node
            
        if self.use_euclidean:
            return euclidean_distance(p1, p2)
        return manhattan_distance(p1, p2)

    #Similar to the implementation of bfs and dfs agents, we run through A* one step at a time. Pygame calls this function multiple times per loop to run the algorithm.
    def step(self):
        if self.is_finished or not self.frontier:
            self.is_finished = True
            return
        
        self.max_memory_nodes = max(self.max_memory_nodes, len(self.frontier) + len(self.visited))
            
        f, _, current_node = heapq.heappop(self.frontier)
        self.current_node = current_node
        
        if current_node in self.visited:
            return
            
        self.visited.add(current_node)
        
        if self.grid.get_node_type(current_node) == NodeType.GOAL:
            self.is_finished = True
            self.path = self._reconstruct_path(current_node)
            return

        for neighbor in self.grid.get_neighbors(current_node):
            # Use edge weight if available (weighted graphs), otherwise default to 1
            edge_weight = self.grid.graph[current_node][neighbor].get('weight', 1)
            tentative_g = self.g_scores[current_node] + edge_weight
            
            # If we found a strictly better path or haven't tracked this neighbor's g_score
            if tentative_g < self.g_scores.get(neighbor, float('inf')):
                self.parents[neighbor] = current_node
                self.g_scores[neighbor] = tentative_g
                h_cost = self._get_heuristic(neighbor)
                f_cost = tentative_g + h_cost
                
                self.counter += 1
                heapq.heappush(self.frontier, (f_cost, self.counter, neighbor))
                
                # Only log purely new explorations to the visualization tree to avoid duplication noise
                if neighbor not in self.visited: 
                    self.tree.add_edge(current_node, neighbor)
                    

    #Walk back through the path that we've traveled when told!
    def _reconstruct_path(self, goal_node):
        path = []
        curr = goal_node
        while curr is not None:
            path.insert(0, curr)
            curr = self.parents.get(curr)
        return path
