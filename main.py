import pygame
import sys
from environment import GraphEnvironment, NodeType
from bfs_agent import BFS_SearchAgent
from dfs_agent import DFS_SearchAgent

#SO. Let's be honest here. In the spirit of time constraints, a lot of this main function is written with AI assistance, because, once I got the main window created initially, I turned to Claude to further develop the UI into looking how it does. Once I started getting into the weeds of visualizing the tree (as horrible as that went), I went between both Claude AND Gemini. So this was a three person effort. One person and two halves. One person and two bots. Just depends on your interpretation.

# Constants to configure how our UI's gonna look.
GRID_WINDOW_SIZE = 600
TREE_PANEL_WIDTH = 400
CONTROL_PANEL_WIDTH = 300
PADDING = 20
TOTAL_WINDOW_WIDTH = GRID_WINDOW_SIZE + TREE_PANEL_WIDTH + CONTROL_PANEL_WIDTH + PADDING
WINDOW_HEIGHT = GRID_WINDOW_SIZE
GRID_SIZE = 10
CELL_SIZE = GRID_WINDOW_SIZE // GRID_SIZE

# Defines the colors for each of our types of nodes, used later on throughout the code.
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
    'text': (50, 50, 50),
    'tree_background': (250, 250, 250),
    'tree_node': (200, 200, 255),
    'tree_current': (255, 100, 100),
    'tree_edge': (100, 100, 100),
    'path': (255, 255, 0)
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

#Uses our colors described above to draw out our grid with the right colors.
def draw_grid(screen, grid_obj, agent_obj=None):
    """Iterate through the Grid object and draw rectangles on the left side."""
    if grid_obj is None:
        return
        
    for row in range(grid_obj.size):
        for col in range(grid_obj.size):
            node = grid_obj.get_node(row, col)
            if node is None: continue
            
            node_type = grid_obj.get_node_type(node)
            
            # The math to find the pixel location (positioned starting at top-left corner)
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            
            # Extract agent drawing logic from environment markers
            if agent_obj and getattr(agent_obj, 'is_finished', False) and agent_obj.path and node in agent_obj.path:
                if node_type not in (NodeType.START, NodeType.GOAL): color = COLORS[NodeType.PATH]
                else: color = COLORS[node_type]
            elif agent_obj and getattr(agent_obj, 'current_node', None) == node:
                color = UI_COLORS['path']
            elif agent_obj and node in getattr(agent_obj, 'visited', set()):
                if node_type not in (NodeType.START, NodeType.GOAL): color = COLORS[NodeType.MARKED]
                else: color = COLORS[node_type]
            else:
                color = COLORS.get(node_type, (255, 255, 255))
            
            # The Pygame drawing function
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            
            # Optional: Draw a grid line outline around each cell
            pygame.draw.rect(screen, (200, 200, 200), (x, y, CELL_SIZE, CELL_SIZE), 1)

#So, funny backstory behind this one. I straight up vibe coded through getting a visualization of the tree, and going through the weeds with Claude got SO bad that, as can be seen in the past commits, there were two behemoth functions that kept getting piled on to make the tree visualization as we needed.

#When I turned to Gemini, who I was previously only using for a conceptual back and forth, Gemini essentially looked at the two behemoth functions and said "hell no", giving the singular function that we have now. Interesting to watch one AI call another AI's work so trash.
def draw_tree_visualization(screen, font, agent):
    """Draws a 5-tier tree, overriding to a wrapped path view when finished."""
    tree_x = GRID_WINDOW_SIZE
    tree_panel = pygame.Rect(tree_x, 0, TREE_PANEL_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, UI_COLORS['tree_background'], tree_panel)
    pygame.draw.rect(screen, UI_COLORS['text'], tree_panel, 2)
    
    if not agent or not hasattr(agent, 'current_node') or not agent.current_node:
        title_text = font.render("Search Tree", True, UI_COLORS['text'])
        screen.blit(title_text, (tree_x + 10, 10))
        screen.blit(font.render("No active search.", True, UI_COLORS['text']), (tree_x + 10, 50))
        return

    # ==========================================
    # THE PATH WRAPPER (Runs only when finished)
    # ==========================================
    if getattr(agent, 'is_finished', False):
        if not hasattr(agent, 'path') or not agent.path:
            title_text = font.render("Result: No Path Found", True, UI_COLORS['text'])
            screen.blit(title_text, (tree_x + 10, 10))
            return
            
        title_text = font.render("Result: Final Path Sequence", True, UI_COLORS['text'])
        screen.blit(title_text, (tree_x + 10, 10))
        
        node_radius = 15
        padding = 45 # Space between nodes
        nodes_per_row = (TREE_PANEL_WIDTH - 20) // padding
        
        # 1. Calculate all positions for the snake wrap
        positions = []
        for i, node in enumerate(agent.path):
            row = i // nodes_per_row
            col = i % nodes_per_row
            
            x = tree_x + 30 + (col * padding)
            y = 70 + (row * padding)
            positions.append((x, y, node))
            
        # 2. Draw connecting lines
        for i in range(len(positions) - 1):
            x1, y1, _ = positions[i]
            x2, y2, _ = positions[i+1]
            pygame.draw.line(screen, UI_COLORS['path'], (x1, y1), (x2, y2), 4)
            
        # 3. Draw the nodes on top
        for x, y, node in positions:
            color = UI_COLORS['tree_current'] if node in (agent.path[0], agent.path[-1]) else UI_COLORS['path']
            pygame.draw.circle(screen, color, (x, y), node_radius)
            pygame.draw.circle(screen, UI_COLORS['text'], (x, y), node_radius, 2)
            
            text = font.render(f"{node[0]},{node[1]}", True, UI_COLORS['text'])
            text = pygame.transform.scale(text, (int(text.get_width() * 0.6), int(text.get_height() * 0.6)))
            screen.blit(text, text.get_rect(center=(x, y)))
            
        return # Bail out so we don't draw the 5-tier tree!

    # ==========================================
    # THE 5-TIER PAGING TREE (Runs while searching)
    # ==========================================
    title_text = font.render("5-Tier Search Tree", True, UI_COLORS['text'])
    screen.blit(title_text, (tree_x + 10, 10))

    current = agent.current_node

    if not hasattr(agent, 'view_root') or not agent.view_root:
        agent.view_root = current

    temp = current
    depth = 0
    found_root = False
    
    while temp and depth < 5:
        if temp == agent.view_root:
            found_root = True
            break
        temp = agent.parents.get(temp)
        depth += 1

    if not found_root:
        new_root = current
        up_steps = 0
        while agent.parents.get(new_root) and up_steps < 4:
            new_root = agent.parents.get(new_root)
            up_steps += 1
        agent.view_root = new_root

    children_map = {}
    for p, c in agent.tree.edges:
        if p not in children_map:
            children_map[p] = []
        children_map[p].append(c)

    levels = {0: [agent.view_root]}
    for d in range(4): 
        next_level = []
        for node in levels.get(d, []):
            next_level.extend(children_map.get(node, []))
        if next_level:
            levels[d + 1] = next_level
        else:
            break

    node_positions = {}
    tier_height = WINDOW_HEIGHT // 6
    node_radius = 15

    for level, nodes in levels.items():
        y = tier_height * (level + 1)
        spacing = TREE_PANEL_WIDTH // (len(nodes) + 1)
        for i, node in enumerate(nodes):
            x = tree_x + (spacing * (i + 1))
            node_positions[node] = (x, y)

    def draw_node(node, x, y, color):
        pygame.draw.circle(screen, color, (x, y), node_radius)
        pygame.draw.circle(screen, UI_COLORS['text'], (x, y), node_radius, 1)
        text = font.render(f"{node[0]},{node[1]}", True, UI_COLORS['text'])
        text = pygame.transform.scale(text, (int(text.get_width() * 0.7), int(text.get_height() * 0.7)))
        screen.blit(text, text.get_rect(center=(x, y)))

    for level in range(4):
        for parent_node in levels.get(level, []):
            if parent_node in node_positions:
                px, py = node_positions[parent_node]
                for child_node in children_map.get(parent_node, []):
                    if child_node in node_positions:
                        cx, cy = node_positions[child_node]
                        pygame.draw.line(screen, UI_COLORS['tree_edge'], (px, py), (cx, cy), 2)

    for level, nodes in levels.items():
        for node in nodes:
            x, y = node_positions[node]
            if node == current:
                color = UI_COLORS['tree_current']
            elif node in agent.visited:
                color = (150, 150, 150)
            else:
                color = UI_COLORS['tree_node']
                
            draw_node(node, x, y, color)

def draw_control_panel(screen, font, grid_status, agent_status, search_status, algorithm_type):
    """Draw the control panel on the right side."""
    panel_x = GRID_WINDOW_SIZE + TREE_PANEL_WIDTH
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

#The heart of the entire project. Sets up Pygame, creates our proper variables and agents, and runs each step by step. 
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
    my_grid = GraphEnvironment(GRID_SIZE)  # Start with a grid ready to go
    current_agent = None
    algorithm_type = "None"
    search_running = False
    search_completed = False
    last_step_time = 0
    
    # Create the algorithm buttons
    bfs_button = Button(
        GRID_WINDOW_SIZE + TREE_PANEL_WIDTH + 30, 200, 200, 50,
        "Create BFS Agent", button_font
    )
    
    dfs_button = Button(
        GRID_WINDOW_SIZE + TREE_PANEL_WIDTH + 30, 270, 200, 50,
        "Create DFS Agent", button_font
    )
    
    reset_button = Button(
        GRID_WINDOW_SIZE + TREE_PANEL_WIDTH + 30, 340, 200, 50,
        "Reset", button_font
    )
    
    # Create speed slider (0.1x to 5.0x speed, default 1.0x)
    speed_slider = Slider(
        GRID_WINDOW_SIZE + TREE_PANEL_WIDTH + 30, 420, 200, 30,
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
            
            if reset_button.handle_event(event):
                # Create new grid and reset everything
                my_grid = GraphEnvironment(GRID_SIZE)
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
        draw_grid(screen, my_grid, current_agent)
        
        # Draw the tree visualization (middle)
        draw_tree_visualization(screen, button_font, current_agent)
        
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