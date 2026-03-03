##Houses the main code for the environment itself, defining classes for Nodes and for the entire GridSpace. 

from enum import Enum
import random


class NodeType(Enum):
    """Enum for different node types in the grid."""
    EMPTY = 0
    WALL = 1
    START = 2
    GOAL = 3


class Node:
    """Represents a single node in the grid."""
    
    def __init__(self, row, column, node_type=NodeType.EMPTY):
        """
        Initialize a node.
        
        Args:
            row: Row coordinate of the node
            column: Column coordinate of the node
            node_type: Type of the node (default: NodeType.EMPTY)
        """
        self.row = row
        self.column = column
        self.type = node_type
    
    def __repr__(self):
        return f"Node({self.row}, {self.column}, {self.type.name})"
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.row == other.row and self.column == other.column
    
    def __hash__(self):
        return hash((self.row, self.column))


class Grid:
    """Represents the NxN grid space for pathfinding."""
    
    def __init__(self, size):
        """
        Initialize the grid.
        
        Args:
            size: Size of the NxN grid
        """
        self.size = size
        self.grid = []
        self.start_node = None
        self.goal_node = None
        self._create_grid()
    
    def _create_grid(self):
        """Create the grid with nodes, start, goal, and walls."""
        # Initialize grid with empty nodes
        self.grid = [[Node(row, col) for col in range(self.size)] 
                     for row in range(self.size)]
        
        # Place start and goal nodes
        self._place_start_and_goal()
        
        # Generate walls (25% of remaining nodes)
        self._generate_walls()
    
    def _place_start_and_goal(self):
        """Randomly place start and goal nodes in the grid."""
        # Get random positions for start and goal
        positions = random.sample(range(self.size * self.size), 2)
        
        start_row = positions[0] // self.size
        start_col = positions[0] % self.size
        goal_row = positions[1] // self.size
        goal_col = positions[1] % self.size
        
        # Set start node
        self.grid[start_row][start_col].type = NodeType.START
        self.start_node = self.grid[start_row][start_col]
        
        # Set goal node
        self.grid[goal_row][goal_col].type = NodeType.GOAL
        self.goal_node = self.grid[goal_row][goal_col]
    
    def _generate_walls(self):
        """Generate walls in 25% of the remaining nodes."""
        # Get all nodes that are not start or goal
        available_nodes = []
        for row in range(self.size):
            for col in range(self.size):
                node = self.grid[row][col]
                if node.type == NodeType.EMPTY:
                    available_nodes.append(node)
        
        # Calculate 25% of remaining nodes
        num_walls = int(len(available_nodes) * 0.25)
        
        # Randomly select nodes to be walls
        wall_nodes = random.sample(available_nodes, num_walls)
        for node in wall_nodes:
            node.type = NodeType.WALL
    
    def get_node(self, row, column):
        """
        Get a specific node from the grid.
        
        Args:
            row: Row coordinate
            column: Column coordinate
            
        Returns:
            Node at the specified position or None if out of bounds
        """
        if 0 <= row < self.size and 0 <= column < self.size:
            return self.grid[row][column]
        return None
    
    def get_neighbors(self, node):
        """
        Get valid 4-cardinal adjacent nodes that are NOT walls.
        
        Args:
            node: The node to find neighbors for
            
        Returns:
            List of valid neighbor nodes
        """
        neighbors = []
        # Four cardinal directions: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for d_row, d_col in directions:
            new_row = node.row + d_row
            new_col = node.column + d_col
            
            # Check if within bounds
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                neighbor = self.grid[new_row][new_col]
                # Only include if not a wall
                if neighbor.type != NodeType.WALL:
                    neighbors.append(neighbor)
        
        return neighbors
    
    def print_grid(self):
        """Print a text-based representation of the grid."""
        print(f"\nGrid ({self.size}x{self.size}):")
        print("S = Start, G = Goal, # = Wall, . = Empty\n")
        
        for row in range(self.size):
            line = ""
            for col in range(self.size):
                node = self.grid[row][col]
                if node.type == NodeType.START:
                    line += "S "
                elif node.type == NodeType.GOAL:
                    line += "G "
                elif node.type == NodeType.WALL:
                    line += "# "
                else:
                    line += ". "
            print(line)
        print()


if __name__ == "__main__":
    # Create a grid and print it for verification
    print("=== Phase 1: Grid Environment ===")
    
    # Test with a 10x10 grid
    grid = Grid(10)
    grid.print_grid()
    
    # Display start and goal positions
    print(f"Start Node: ({grid.start_node.row}, {grid.start_node.column})")
    print(f"Goal Node: ({grid.goal_node.row}, {grid.goal_node.column})")
    
    # Test get_neighbors method
    print(f"\nNeighbors of Start Node:")
    neighbors = grid.get_neighbors(grid.start_node)
    for neighbor in neighbors:
        print(f"  - ({neighbor.row}, {neighbor.column}) [{neighbor.type.name}]")
    
    # Count node types
    wall_count = 0
    empty_count = 0
    for row in range(grid.size):
        for col in range(grid.size):
            node = grid.grid[row][col]
            if node.type == NodeType.WALL:
                wall_count += 1
            elif node.type == NodeType.EMPTY:
                empty_count += 1
    
    total_nodes = grid.size * grid.size
    wall_percentage = (wall_count / (total_nodes - 2)) * 100  # Exclude start and goal
    
    print(f"\nGrid Statistics:")
    print(f"  Total Nodes: {total_nodes}")
    print(f"  Empty Nodes: {empty_count}")
    print(f"  Wall Nodes: {wall_count}")
    print(f"  Wall Percentage (of remaining): {wall_percentage:.1f}%")