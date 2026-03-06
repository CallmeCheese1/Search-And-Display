import pygame
import sys
from environment import Grid, NodeType
from bfs_agent import BFS_SearchAgent
from dfs_agent import DFS_SearchAgent

#NOTE: The project goal is that we'll have, on the left side, a grid that, given we spawn a particular type of Agent, we'll animate the agent picking and checking particular nodes as blue, and then once it finds the goal, we mark all the nodes in the path as yellow. But then, on the right side, we'll have controls to manage the search process.

# 1. Configuration
GRID_WINDOW_SIZE = 600
CONTROL_PANEL_WIDTH = 300
PADDING = 20
TOTAL_WINDOW_WIDTH = GRID_WINDOW_SIZE + CONTROL_PANEL_WIDTH + (PADDING * 2)
WINDOW_HEIGHT = GRID_WINDOW_SIZE + (PADDING * 2)
GRID_SIZE = 10
CELL_SIZE = GRID_WINDOW_SIZE // GRID_SIZE

# Define some colors (RGB tuples)
COLORS = {
    NodeType.EMPTY: (255, 255, 255), # White
    NodeType.WALL: (50, 50, 50),     # Dark Gray
    NodeType.START: (0, 255, 0),     # Green
    NodeType.GOAL: (255, 0, 0),      # Red
    NodeType.MARKED: (0, 0, 255),    # Blue
    NodeType.PATH: (255, 255, 0)     # Yellow
}

# UI Colors
UI_COLORS = {
    'background': (240, 240, 240),
    'button': (100, 150, 200),
    'button_hover': (120, 170, 220),
    'button_text': (255, 255, 255),
    'text': (50, 50, 50)
}

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
        
    def draw(self, screen):
        color = UI_COLORS['button_hover'] if self.is_hovered else UI_COLORS['button']
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, UI_COLORS['text'], self.rect, 2)
        
        text_surface = self.font.render(self.text, True, UI_COLORS['button_text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.font = font
        self.dragging = False
        
        # Calculate handle position
        self.handle_radius = height // 2
        self.track_rect = pygame.Rect(x + self.handle_radius, y + height//4, 
                                    width - 2*self.handle_radius, height//2)
        self.update_handle_pos()
    
    def update_handle_pos(self):
        # Calculate handle x position based on current value
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_x = self.track_rect.x + ratio * self.track_rect.width
        self.handle_y = self.rect.centery
    
    def draw(self, screen):
        # Draw track
        pygame.draw.rect(screen, (150, 150, 150), self.track_rect)
        pygame.draw.rect(screen, UI_COLORS['text'], self.track_rect, 1)
        
        # Draw handle
        pygame.draw.circle(screen, UI_COLORS['button'], (int(self.handle_x), int(self.handle_y)), self.handle_radius)
        pygame.draw.circle(screen, UI_COLORS['text'], (int(self.handle_x), int(self.handle_y)), self.handle_radius, 2)
        
        # Draw value text
        value_text = f"Speed: {self.val:.1f}x"
        text_surface = self.font.render(value_text, True, UI_COLORS['text'])
        screen.blit(text_surface, (self.rect.x, self.rect.y - 25))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_rect = pygame.Rect(self.handle_x - self.handle_radius, 
                                    self.handle_y - self.handle_radius,
                                    2 * self.handle_radius, 2 * self.handle_radius)
            if handle_rect.collidepoint(event.pos) or self.track_rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value_from_mouse(event.pos[0])
            return True
        return False
    
    def update_value_from_mouse(self, mouse_x):
        # Clamp mouse position to track bounds
        relative_x = max(0, min(self.track_rect.width, mouse_x - self.track_rect.x))
        ratio = relative_x / self.track_rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self.update_handle_pos()

def draw_grid(screen, grid_obj):
    """Iterate through the Grid object and draw rectangles on the left side."""
    if grid_obj is None:
        return
        
    for row in range(grid_obj.size):
        for col in range(grid_obj.size):
            node = grid_obj.get_node(row, col)
            
            # The math to find the pixel location (positioned on the left side with padding)
            x = col * CELL_SIZE + PADDING
            y = row * CELL_SIZE + PADDING
            
            # The Pygame drawing function
            # pygame.draw.rect(surface, color, (x, y, width, height))
            pygame.draw.rect(screen, COLORS[node.type], (x, y, CELL_SIZE, CELL_SIZE))
            
            # Optional: Draw a grid line outline around each cell
            pygame.draw.rect(screen, (200, 200, 200), (x, y, CELL_SIZE, CELL_SIZE), 1)

def draw_control_panel(screen, font, grid_status, agent_status, search_status, algorithm_type):
    """Draw the control panel on the right side."""
    panel_x = GRID_WINDOW_SIZE + PADDING
    panel_rect = pygame.Rect(panel_x, 0, CONTROL_PANEL_WIDTH + PADDING, WINDOW_HEIGHT)
    pygame.draw.rect(screen, UI_COLORS['background'], panel_rect)
    
    # Draw a separator line
    pygame.draw.line(screen, UI_COLORS['text'], (panel_x, 0), (panel_x, WINDOW_HEIGHT), 2)
    
    # Title
    title_text = font.render("Search Visualizer", True, UI_COLORS['text'])
    screen.blit(title_text, (panel_x + PADDING, PADDING + 10))
    
    # Status information
    y_offset = PADDING + 60
    status_texts = [
        "Grid: " + grid_status,
        "Agent: " + agent_status,
        "Algorithm: " + algorithm_type,
        "Search: " + search_status
    ]
    
    for text in status_texts:
        status_surface = font.render(text, True, UI_COLORS['text'])
        screen.blit(status_surface, (panel_x + PADDING, y_offset))
        y_offset += 30

def main():
    # 2. Setup Pygame
    pygame.init()
    screen = pygame.display.set_mode((TOTAL_WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pathfinding Visualizer")
    clock = pygame.time.Clock()
    
    # Initialize font
    font = pygame.font.Font(None, 24)
    button_font = pygame.font.Font(None, 20)
    
    # Initialize state variables
    my_grid = Grid(GRID_SIZE)  # Start with a grid ready to go
    current_agent = None
    algorithm_type = "None"
    search_running = False
    search_completed = False
    last_step_time = 0
    
    # Create the algorithm buttons
    bfs_button = Button(
        GRID_WINDOW_SIZE + PADDING + 30, 200, 200, 50,
        "Create BFS Agent", button_font
    )
    
    dfs_button = Button(
        GRID_WINDOW_SIZE + PADDING + 30, 270, 200, 50,
        "Create DFS Agent", button_font
    )
    
    reset_button = Button(
        GRID_WINDOW_SIZE + PADDING + 30, 340, 200, 50,
        "Reset", button_font
    )
    
    # Create speed slider (0.1x to 5.0x speed, default 1.0x)
    speed_slider = Slider(
        GRID_WINDOW_SIZE + PADDING + 30, 420, 200, 30,
        0.1, 5.0, 1.0, button_font
    )
    
    # 3. The Game Loop
    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle button clicks
            if bfs_button.handle_event(event):
                if not search_running and my_grid is not None:
                    # Create new BFS agent on existing grid
                    current_agent = BFS_SearchAgent(my_grid, my_grid.start_node)
                    algorithm_type = "BFS"
                    # Start the search
                    search_running = True
                    search_completed = False
                    bfs_button.text = "Searching..."
                    dfs_button.text = "Create DFS Agent"
                    # Clear any previous markings
                    my_grid.clear_marks()
            
            if dfs_button.handle_event(event):
                if not search_running and my_grid is not None:
                    # Create new DFS agent on existing grid
                    current_agent = DFS_SearchAgent(my_grid, my_grid.start_node)
                    algorithm_type = "DFS"
                    # Start the search
                    search_running = True
                    search_completed = False
                    dfs_button.text = "Searching..."
                    bfs_button.text = "Create BFS Agent"
                    # Clear any previous markings
                    my_grid.clear_marks()
            
            if reset_button.handle_event(event):
                # Create new grid and reset everything
                my_grid = Grid(GRID_SIZE)
                current_agent = None
                algorithm_type = "None"
                search_running = False
                search_completed = False
                bfs_button.text = "Create BFS Agent"
                dfs_button.text = "Create DFS Agent"
            
            # Handle slider events
            speed_slider.handle_event(event)
        
        # Update search process (with timing control)
        current_time = pygame.time.get_ticks()
        step_delay = int(1000 / (speed_slider.val * 20))  # Convert speed to milliseconds delay
        
        if search_running and current_agent and not current_agent.is_finished:
            if current_time - last_step_time > step_delay:
                current_agent.step()
                last_step_time = current_time
        elif search_running and current_agent and current_agent.is_finished:
            if len(current_agent.path):
                my_grid.mark_path(current_agent.path)
            search_running = False
            search_completed = True
            bfs_button.text = "Create BFS Agent"
            dfs_button.text = "Create DFS Agent"
        
        # Determine status strings
        grid_status = "Created" if my_grid else "Not Created"
        agent_status = "Created" if current_agent else "Not Created"
        if search_running:
            search_status = "Running"
        elif search_completed:
            search_status = "Completed"
        else:
            search_status = "Not Started"
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw the grid (left side)
        draw_grid(screen, my_grid)
        
        # Draw the control panel (right side)
        draw_control_panel(screen, font, grid_status, agent_status, search_status, algorithm_type)
        
        # Draw buttons and slider
        bfs_button.draw(screen)
        dfs_button.draw(screen)
        reset_button.draw(screen)
        speed_slider.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)  # 60 FPS, but search will still be controlled by the step timing

    # Quit cleanly when the loop breaks
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()