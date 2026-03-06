from enum import Enum
import random

#As the name of the file implies, this houses all the code for the environment itself, defining Nodes that can be either empty, a Wall, a Start position, or a Goal, and defining the entire grid as a whole. Most of this code was also generated using a Claude Sonnet 4 Agent through Github Copilot, so commenting back through this is gonna be...interesting.

#NOTE: ALL COORDINATES start from the top left and start at 0.

#Nodes can either be an empty space, a Wall, a Start position, or a Goal.
class NodeType(Enum):
    """Enum for different node types in the grid. A node can either be an empty space, a WALL, a START position, or a GOAL."""
    #Wow, look at me learning what docstrings actually are. Thanks, Claude.

    EMPTY = 0
    WALL = 1
    START = 2
    GOAL = 3
    MARKED = 4
    PATH = 5

#Fundamental building blocks of the entire project. Nodes are created with the row, column, and the type, defaulting to empty. Comes with string representation, equality, and hashing.
class Node:
    """Represents a single node in the grid."""
    
    def __init__(self, row, column, node_type=NodeType.EMPTY):
        """
        Create a node with the row, column, and node type (default: NoteType.EMPTY)
        """

        self.row = row
        self.column = column
        self.type = node_type
        self.parent = None
    
    #What happens if we try to print a node?
    def __repr__(self):
        return f"Node({self.row}, {self.column}, {self.type.name})"
    
    #What happens if we check if one node equals another?
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.row == other.row and self.column == other.column
    
    #What happens when we run hash(Node)?
    def __hash__(self):
        return hash((self.row, self.column))


#Where all the magic happens. Creates an NxN grid space for our agent to work its magic, with a specified percentage of walls, start and end goals, and functions to find neighbors or get particular nodes.
class Grid:
    """Represents the NxN grid space for pathfinding."""
    
    def __init__(self, size):
        """
        Initialize the grid with the n size.
        """

        self.size = size
        self.grid = []
        self.start_node = None
        self.goal_node = None
        self._create_grid()
    
    def _create_grid(self):
        """Run on init, creates the grid with nodes, start, goal, and walls."""

        # Initializes grid with empty nodes, using list comprehension syntax. So technically, yes, this could be done with a double for loop, but this achieves the same.
        self.grid = [[Node(row, col) for col in range(self.size)] 
                     for row in range(self.size)]
        
        #Run partner functions to place our start and end goals, and generate walls. 
        self._place_start_and_goal()
        self._generate_walls()
    
    def _place_start_and_goal(self):
        """Randomly place start and goal nodes in the grid."""
        
        # Creates random positions for the start goal by pulling two random numbers corresponding to locations in our nxn grid. For example, in a 3x3, we'd select a random number from 0 to 3x3=9, say, 2 and 7.
        positions = random.sample(range(self.size * self.size), 2)
        
        # Uses integer division and modulo to map the random positional numbers from above into...actual coordinates. Coincidentally, using integer division on a positional number gives us the row, while using modulus gives us the column. 
        start_row = positions[0] // self.size
        start_col = positions[0] % self.size
        
        #So we do it on the first number for the start, and then again on the second number for the goal. 
        goal_row = positions[1] // self.size
        goal_col = positions[1] % self.size
        
        #Set our start and goal nodes to be the coordinates we've calculated.
        self.grid[start_row][start_col].type = NodeType.START
        self.start_node = self.grid[start_row][start_col]

        self.grid[goal_row][goal_col].type = NodeType.GOAL
        self.goal_node = self.grid[goal_row][goal_col]
    
    def _generate_walls(self):
        """Turn 25% of our remaining nodes into walls randomly."""
        
        #Iterates through the enitre 2D array of the grid, and finds every node that's EMPTY -- everything that's NOT a Start or Goal. 
        available_nodes = []
        for row in range(self.size):
            for col in range(self.size):
                node = self.grid[row][col]
                if node.type == NodeType.EMPTY:
                    available_nodes.append(node)
        
        # Calculate the number of walls we need to convert by calculating what 25% of our available nodes is. 
        num_walls = int(len(available_nodes) * 0.25)
        
        # Based on that last line, select num_walls random walls and make them walls. Then boom!
        wall_nodes = random.sample(available_nodes, num_walls)
        for node in wall_nodes:
            node.type = NodeType.WALL
    
    def get_node(self, row, column):
        """
        Get a specific node from the grid with row and column, returning the Node object or None if it doesn't exist. 
        """
        if 0 <= row < self.size and 0 <= column < self.size:
            return self.grid[row][column]
        return None
    
    def get_neighbors(self, node):
        """
        Find the valid nodes in every cardinal direction that's NOT a wall, for the specified Node. Returns a list of valid neighbors, or an empty list if no valid neighbors.
        """

        neighbors = []
        # Define the holy cardinal directions that have guided civilization: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for direction_row, direction_col in directions:
            new_row = node.row + direction_row
            new_col = node.column + direction_col
            
            # Check if within bounds
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                neighbor = self.grid[new_row][new_col]
                # If our neighbor isn't a wall, include it and say hi neighbor
                if neighbor.type != NodeType.WALL:
                    neighbors.append(neighbor)
        
        return neighbors
    
    def mark_path(self, path):
        """Mark nodes in the given path (except start and goal) for visualization."""
        for node in path:
            # Don't overwrite start and goal nodes
            if node.type == NodeType.EMPTY or node.type == NodeType.MARKED:
                node.type = NodeType.PATH
    
    def clear_marks(self):
        """Clear all marked and pathed nodes back to empty, without actually resetting the whole grid or any positions."""
        for row in range(self.size):
            for col in range(self.size):

                node = self.grid[row][col]

                if node.type == NodeType.MARKED or node.type == NodeType.PATH:
                    node.type = NodeType.EMPTY

                if node.type != NodeType.START and node.type != NodeType.GOAL:
                    node.parent = None
    
    #Here's a funny AI moment. At some point, I told Claude that we need to be able to run either agent without clearing and restarting the grid every time. As we'd expect, as humans, we'd probably want to use the above clear_marks() function to...clear the grid. But it doesn't have the condition to clear NodeType.PATH nodes. I ASSUMED that Claude would use the above clear_marks() function, and add that new function.
    # ...clearly, my assumption was wrong, 'cause it just made a whole new function. I'm gonna leave this commented out for the sake of reflection, and just because it's funny. 
    # def _reset_markings(self):
    #     """Reset all MARKED and PATH nodes back to EMPTY for algorithm comparison."""
    #     for row in range(self.size):
    #         for col in range(self.size):
    #             node = self.grid[row][col]
    #             if node.type == NodeType.MARKED or node.type == NodeType.PATH:
    #                 node.type = NodeType.EMPTY
    #             # Also reset parent pointers for clean algorithm runs
    #             if node.type != NodeType.START and node.type != NodeType.GOAL:
    #                 node.parent = None
    
    def print_grid(self):
        """Do you really need to be told what a PRINT_GRID function does?"""
        print(f"\nGrid ({self.size}x{self.size}):")
        print("S = Start, G = Goal, # = Wall, . = Empty, X = Path")

        print()
        
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
                elif node.type == NodeType.MARKED:
                    line += "* "
                elif node.type == NodeType.PATH:
                    line += "X "
                else:
                    line += ". "
            print(line)
        
        print()

#In case this one is the file you're running, let's make a grid and print it out.
if __name__ == "__main__":
    # Create a grid and print it for verification
    print("=== Phase 1: Grid Environment ===")
    grid = Grid(10)
    grid.print_grid()
    
    # Dox the start and goal nodes
    print(f"Start Node: ({grid.start_node.row}, {grid.start_node.column})")
    print(f"Goal Node: ({grid.goal_node.row}, {grid.goal_node.column})")
    
    # Test out the get_neighbors method
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
    
    #you can tell this line's coming from Claude cause I sure don't know how that last format worked, ancient arcane magic
    print(f"  Wall Percentage (of remaining): {wall_percentage:.1f}%")