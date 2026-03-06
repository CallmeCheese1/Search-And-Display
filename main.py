import pygame
import sys
from environment import Grid, NodeType
from bfs_agent import BFS_SearchAgent
from dfs_agent import DFS_SearchAgent

#NOTE: The project goal is that we'll have, on the left side, a grid that, given we spawn a particular type of Agent, we'll animate the agent picking and checking particular nodes as blue, and then once it finds the goal, we mark all the nodes in the path as yellow. But then, on the right side, we'll have controls to manage the search process.

# 1. Configuration
GRID_WINDOW_SIZE = 600
TREE_PANEL_WIDTH = 400
CONTROL_PANEL_WIDTH = 300
PADDING = 20
TOTAL_WINDOW_WIDTH = GRID_WINDOW_SIZE + TREE_PANEL_WIDTH + CONTROL_PANEL_WIDTH + PADDING
WINDOW_HEIGHT = GRID_WINDOW_SIZE
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
    'text': (50, 50, 50),
    'tree_background': (250, 250, 250),
    'tree_node': (200, 200, 255),
    'tree_current': (255, 100, 100),
    'tree_edge': (100, 100, 100)
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
            
            # The math to find the pixel location (positioned starting at top-left corner)
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            
            # The Pygame drawing function
            # pygame.draw.rect(surface, color, (x, y, width, height))
            pygame.draw.rect(screen, COLORS[node.type], (x, y, CELL_SIZE, CELL_SIZE))
            
            # Optional: Draw a grid line outline around each cell
            pygame.draw.rect(screen, (200, 200, 200), (x, y, CELL_SIZE, CELL_SIZE), 1)

def get_active_node_context(agent, layers=2):
    """Get the active node and surrounding context (siblings at each level)."""
    if not agent:
        return [], [], None
    
    # Determine the active node (currently being processed)
    active_node = None
    
    # The active node should be the next node to be processed from the frontier
    if hasattr(agent, 'frontier') and agent.frontier and len(agent.frontier) > 0:
        # For BFS: next node is at front (index 0)
        # For DFS: next node is at back (index -1) 
        if isinstance(agent, BFS_SearchAgent):
            active_node = agent.frontier[0]  # Next to be processed (popleft)
        elif isinstance(agent, DFS_SearchAgent):
            active_node = agent.frontier[-1]  # Next to be processed (pop)
        else:
            active_node = agent.frontier[0]  # Default to first
    
    # If no frontier, try to get the most recently visited node
    if not active_node and hasattr(agent, 'visited') and agent.visited:
        # Convert set to list and get last item (though set order isn't guaranteed)
        visited_list = list(agent.visited)
        if visited_list:
            active_node = visited_list[-1]
    
    # Final fallback to root if nothing else works
    if not active_node and hasattr(agent, 'tree') and agent.tree and agent.tree.root:
        active_node = agent.tree.root
    
    if not active_node:
        return [], [], None
    
    # Make sure we have tree edges to work with
    if not hasattr(agent, 'tree') or not agent.tree or not agent.tree.edges:
        # If we only have the root, still show it
        if active_node:
            return [active_node], [], active_node
        return [], [], None
    
    # Build complete tree structure and assign absolute levels from root
    parent_to_children = {}
    child_to_parent = {}
    all_nodes = {agent.tree.root}
    
    for parent, child in agent.tree.edges:
        if parent not in parent_to_children:
            parent_to_children[parent] = []
        parent_to_children[parent].append(child)
        child_to_parent[child] = parent
        all_nodes.add(parent)
        all_nodes.add(child)
    
    # Assign absolute levels from root using BFS
    absolute_levels = {agent.tree.root: 0}
    queue = [(agent.tree.root, 0)]
    
    while queue:
        node, level = queue.pop(0)
        if node in parent_to_children:
            for child in parent_to_children[node]:
                if child not in absolute_levels:
                    absolute_levels[child] = level + 1
                    queue.append((child, level + 1))
    
    # Find the active node's level
    active_level = absolute_levels.get(active_node, 0)
    
    # Collect all nodes within the level range (show all siblings at each level)
    nodes_to_show = set()
    edges_to_show = []
    
    min_level = max(0, active_level - layers)  # Don't go below root level
    max_level = active_level + layers
    
    # Add all nodes at levels within range
    for node, level in absolute_levels.items():
        if min_level <= level <= max_level:
            nodes_to_show.add(node)
    
    # Add all edges between nodes that we're showing
    for parent, child in agent.tree.edges:
        if parent in nodes_to_show and child in nodes_to_show:
            edges_to_show.append((parent, child))
    
    return list(nodes_to_show), edges_to_show, active_node

def calculate_active_tree_positions(nodes, edges, active_node, tree_panel_bounds):
    """Calculate positions for active node tree showing siblings at each level."""
    if not nodes or not active_node:
        return {}
    
    tree_x, tree_y, tree_width, tree_height = tree_panel_bounds
    
    # Handle case with only one node (just show it centered)
    if len(nodes) == 1:
        center_x = tree_x + tree_width // 2
        center_y = tree_y + tree_height // 2
        return {nodes[0]: (center_x, center_y)}
    
    # Build parent-child relationships
    parent_to_children = {}
    child_to_parent = {}
    
    for parent, child in edges:
        if parent not in parent_to_children:
            parent_to_children[parent] = []
        parent_to_children[parent].append(child)
        child_to_parent[child] = parent
    
    # Find root node (appears as parent but never as child, or is in nodes but not a child)
    root_node = None
    for node in nodes:
        if node not in child_to_parent:
            root_node = node
            break
    
    # If we can't find a clear root, use the active node as reference
    if not root_node:
        root_node = active_node
    
    # Assign absolute levels from root using BFS
    levels = {root_node: 0}
    queue = [(root_node, 0)]
    
    while queue:
        node, level = queue.pop(0)
        if node in parent_to_children:
            for child in parent_to_children[node]:
                if child not in levels and child in nodes:  # Only process nodes we're showing
                    levels[child] = level + 1
                    queue.append((child, level + 1))
    
    # Ensure active_node has a level (in case tree structure is incomplete)
    if active_node not in levels:
        levels[active_node] = 0  # Default to level 0
    
    # Find active node's level for centering
    active_level = levels.get(active_node, 0)
    
    # Group nodes by level
    level_groups = {}
    for node, level in levels.items():
        if node in nodes:  # Only include nodes we're showing
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(node)
    
    # If somehow no nodes got levels, just put them all at level 0
    if not level_groups:
        level_groups[0] = list(nodes)
    
    # Calculate positions
    positions = {}
    node_radius = 20  # Smaller nodes to fit more
    level_height = 80  # Tighter vertical spacing
    
    # Center the active node's level vertically in the panel
    center_y = tree_y + tree_height // 2
    
    for level, level_nodes in level_groups.items():
        # Calculate relative position from active level
        level_offset = level - active_level
        y = center_y + (level_offset * level_height)
        
        # Skip if outside panel bounds
        if y < tree_y + 60 or y > tree_y + tree_height - 60:
            continue
            
        num_nodes = len(level_nodes)
        if num_nodes == 1:
            x = tree_x + tree_width // 2
            positions[level_nodes[0]] = (x, y)
        else:
            # Distribute nodes across the width
            available_width = tree_width - 80  # Leave margins
            if num_nodes > 1:
                spacing = available_width / (num_nodes - 1)
                start_x = tree_x + 40
            else:
                spacing = 0
                start_x = tree_x + tree_width // 2
            
            for i, node in enumerate(level_nodes):
                x = start_x + (i * spacing)
                positions[node] = (x, y)
    
    return positions

def draw_tree_visualization(screen, font, agent):
    """Draw the tree visualization panel focused on active node."""
    tree_x = GRID_WINDOW_SIZE
    tree_panel = pygame.Rect(tree_x, 0, TREE_PANEL_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(screen, UI_COLORS['tree_background'], tree_panel)
    pygame.draw.rect(screen, UI_COLORS['text'], tree_panel, 2)
    
    # Title
    title_text = font.render("Search Tree (Siblings View)", True, UI_COLORS['text'])
    screen.blit(title_text, (tree_x + 10, 10))
    
    if not agent:
        no_agent_text = font.render("No agent active", True, UI_COLORS['text'])
        screen.blit(no_agent_text, (tree_x + 10, 50))
        return
    
    if not agent.tree.edges:
        no_tree_text = font.render("No exploration yet", True, UI_COLORS['text'])
        screen.blit(no_tree_text, (tree_x + 10, 50))
        return
    
    # Get active node context
    nodes, edges, active_node = get_active_node_context(agent, layers=2)
    
    if not nodes:
        return
    
    # Calculate focused tree positions
    tree_bounds = (tree_x, 0, TREE_PANEL_WIDTH, WINDOW_HEIGHT)
    node_positions = calculate_active_tree_positions(nodes, edges, active_node, tree_bounds)
    
    # Draw edges first
    for parent, child in edges:
        if parent in node_positions and child in node_positions:
            start_pos = node_positions[parent]
            end_pos = node_positions[child]
            pygame.draw.line(screen, UI_COLORS['tree_edge'], start_pos, end_pos, 3)
    
    # Draw nodes
    node_radius = 20  # Match the positioning function
    for node in nodes:
        if node in node_positions:
            x, y = node_positions[node]
            
            # Choose color based on node status
            if node == active_node:
                color = UI_COLORS['tree_current']  # Red for active
            elif node == agent.tree.root:
                color = (100, 255, 100)  # Green for root
            else:
                color = UI_COLORS['tree_node']  # Blue for others
            
            # Draw node circle
            pygame.draw.circle(screen, color, (int(x), int(y)), node_radius)
            pygame.draw.circle(screen, UI_COLORS['text'], (int(x), int(y)), node_radius, 2)
            
            # Draw coordinates text (smaller font for more nodes)
            coord_text = f"({node.row},{node.column})"
            text_surface = font.render(coord_text, True, UI_COLORS['text'])
            text_rect = text_surface.get_rect(center=(int(x), int(y)))
            screen.blit(text_surface, text_rect)
    
    # Draw legend
    legend_y = WINDOW_HEIGHT - 80
    legend_items = [
        ("Active Node", UI_COLORS['tree_current']),
        ("Root Node", (100, 255, 100)),
        ("Other Nodes", UI_COLORS['tree_node'])
    ]
    
    for i, (label, color) in enumerate(legend_items):
        legend_x = tree_x + 10
        legend_item_y = legend_y + i * 20
        
        pygame.draw.circle(screen, color, (legend_x + 10, legend_item_y + 7), 8)
        pygame.draw.circle(screen, UI_COLORS['text'], (legend_x + 10, legend_item_y + 7), 8, 1)
        
        label_surface = font.render(label, True, UI_COLORS['text'])
        screen.blit(label_surface, (legend_x + 25, legend_item_y))

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