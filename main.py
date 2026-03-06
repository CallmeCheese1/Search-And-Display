import pygame
from environment import Grid, NodeType

#NOTE: The project goal is that we'll have, on the right side, a grid that, given we spawn a particular type of Agent, we'll animate the agent picking and checking particular nodes as blue, and then once it finds the goal, we mark all the nodes in the path as yellow. But then, on the left side, a node tree will track and create cells and edges of every node as the agent checks them.

# 1. Configuration
WINDOW_SIZE = 600
GRID_SIZE = 10
CELL_SIZE = WINDOW_SIZE // GRID_SIZE

# Define some colors (RGB tuples)
COLORS = {
    NodeType.EMPTY: (255, 255, 255), # White
    NodeType.WALL: (50, 50, 50),     # Dark Gray
    NodeType.START: (0, 255, 0),     # Green
    NodeType.GOAL: (255, 0, 0),      # Red
    NodeType.MARKED: (0, 0, 255),    # Blue
    NodeType.PATH: (255, 255, 0)     # Yellow
}

def draw_grid(screen, grid_obj):
    """Iterate through the Grid object and draw rectangles."""
    for row in range(grid_obj.size):
        for col in range(grid_obj.size):
            node = grid_obj.get_node(row, col)
            
            # The math to find the pixel location
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            
            # The Pygame drawing function
            # pygame.draw.rect(surface, color, (x, y, width, height))
            pygame.draw.rect(screen, COLORS[node.type], (x, y, CELL_SIZE, CELL_SIZE))
            
            # Optional: Draw a grid line outline around each cell
            pygame.draw.rect(screen, (200, 200, 200), (x, y, CELL_SIZE, CELL_SIZE), 1)

def main():
    # 2. Setup Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Pathfinding Visualizer")
    
    # Initialize your environment
    my_grid = Grid(GRID_SIZE)
    
    # 3. The Game Loop
    running = True
    while running:
        # Event Handling (so it doesn't freeze)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Draw the background
        screen.fill((0, 0, 0))
        
        # Draw our specific grid
        draw_grid(screen, my_grid)
        
        # Tell Pygame to push the new drawing to the monitor
        pygame.display.flip()

    # Quit cleanly when the loop breaks
    pygame.quit()

if __name__ == "__main__":
    main()