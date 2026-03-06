from environment import Grid, NodeType, Node
from collections import deque

#Will hold the algorithmic code for both Depth-First Search and Breadth-First Search Algorithms.

def bfs(grid: Grid, start: Node):
    """Given a grid, use a Breadth-First Search algorithm to return a list of nodes pathing from the start to the goal, or return None if no path exists."""

    #no recursion this time! hooray. am i rite

    #Define a frontier, a deque which holds what we are/will currently look at, and visited, both of which will just start with the starting node
    frontier = deque([start])
    visited = set()

    #Then, for as long as we have a frontier...
    #Take the current Node, popped from the left of frontier
    #if it's the goal, hooray! reconstruct the path and return that path

    while frontier:
        current_node = frontier.popleft()

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node.type is NodeType.GOAL:
            path = []
            while current_node is not None:
                path.insert(0, current_node)
                current_node = current_node.parent
            return path

        
        neighbors = grid.get_neighbors(current_node)
        
        if neighbors:
            for neighbor in neighbors:
                if neighbor not in visited:
                    neighbor.parent = current_node
                    frontier.append(neighbor)

    return None

def dfs(grid: Grid, visited: set[Node], start: Node):
    """Given a grid, use a Depth-First Search algorithm to return a list of nodes pathing from the start to the goal, or return None if no path exists."""

    #first, check if the starting node is a Goal node. If so, we've found the goal, and we pass it back up in a list on its own
    if start.type is NodeType.GOAL:
        return [start]
    else:
        visited.add(start)

    #get all of the node's neighbors, if no neighbors, return None. That means we're at a dead end here.
    neighbors = grid.get_neighbors(start)
    if not neighbors:
        return None
    
    else:
        for neighbor_node in neighbors:

            #First, don't double dip.
            if neighbor_node not in visited:

                #{ast double dipping? Good. Recursively call US on each of our neighbor nodes.
                result = dfs(grid, visited, neighbor_node)

                #Thanks to the above code so far, if our neighbor node has found a path, it'll be returning the path, so we add ourselves to that path and pass it up the chain. 
                if result:
                    result.insert(0, start)
                    return result

        return None

#Fun fact for future reflection: The first time, after I created the DFS algorithm, it technically worked, but it just returned a long list of the coordinates that was hard to follow. So I prompted Claude with environment.py and search.py to create a way to mark noddes in a path, and it created exactly what I needed. The power of the sun in the palm of my hand.

'''
if __name__ == "__main__":
    # Create a test grid
    print("=== DFS Test ===")
    grid = Grid(8)  # Smaller grid for easier visualization
    grid.print_grid()
    
    # Run DFS from start to goal
    visited = set()
    path = dfs(grid, visited, grid.start_node)
    
    if path:
        print(f"Path found! Length: {len(path)}")
        print("Path coordinates:")
        for i, node in enumerate(path):
            print(f"  {i+1}. ({node.row}, {node.column}) [{node.type.name}]")
        
        # Mark the path and show it visually
        grid.mark_path(path)
        print("\nGrid with path marked:")
        grid.print_grid()
        
    else:
        print("No path found!")
    
    print(f"\nLength of final path: {len(visited)}"
'''

if __name__ == "__main__":
    # Create a test grid
    print("=== Path Search Algorithm Comparison ===")
    grid = Grid(8)  # Smaller grid for easier visualization
    print("Starting Grid:")
    grid.print_grid()
    
    # Test DFS
    print("=== DFS Results ===")
    visited_dfs = set()
    dfs_path = dfs(grid, visited_dfs, grid.start_node)
    
    if dfs_path:
        print(f"DFS Path found! Length: {len(dfs_path)}")
        grid.mark_path(dfs_path)
        print("Grid with DFS path marked:")
        grid.print_grid()
        grid.clear_marks()  # Clear for next test
    else:
        print("DFS: No path found!")
    
    # Test BFS
    print("=== BFS Results ===")
    bfs_path = bfs(grid, grid.start_node)
    
    if bfs_path:
        print(f"BFS Path found! Length: {len(bfs_path)}")
        grid.mark_path(bfs_path)
        print("Grid with BFS path marked:")
        grid.print_grid()
    else:
        print("BFS: No path found!")

