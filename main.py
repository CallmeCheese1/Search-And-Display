import pygame
import sys
import time
import random
from environment import GraphEnvironment, NodeType, GraphTopology
from bfs_agent import BFS_SearchAgent
from dfs_agent import DFS_SearchAgent
from iddfs_agent import IDDFS_SearchAgent
from greedy_agent import Greedy_SearchAgent
from environment import GraphEnvironment, NodeType, GraphTopology
from bfs_agent import BFS_SearchAgent
from dfs_agent import DFS_SearchAgent
from iddfs_agent import IDDFS_SearchAgent
from greedy_agent import Greedy_SearchAgent
from astar_agent import AStar_SearchAgent

# Constants to configure how our UI's gonna look.
GRID_WINDOW_SIZE = 600
TREE_PANEL_WIDTH = 400
CONTROL_PANEL_WIDTH = 300
BOTTOM_PANEL_HEIGHT = 150
PADDING = 20
TOTAL_WINDOW_WIDTH = GRID_WINDOW_SIZE + TREE_PANEL_WIDTH + CONTROL_PANEL_WIDTH + PADDING
WINDOW_HEIGHT = GRID_WINDOW_SIZE + BOTTOM_PANEL_HEIGHT
GRID_SIZE = 10
CELL_SIZE = GRID_WINDOW_SIZE // GRID_SIZE

OBSTACLE_RATE = 0.20

# Defines the colors for each of our types of nodes
COLORS = {
    NodeType.EMPTY: (255, 255, 255), 
    NodeType.WALL: (50, 50, 50),     
    NodeType.START: (0, 255, 0),     
    NodeType.GOAL: (255, 0, 0),      
    NodeType.MARKED: (0, 0, 255),    
    NodeType.PATH: (255, 255, 0)     
}

# Modern UI Colors
UI_COLORS = {
    'background': (248, 250, 252),
    'button': (37, 99, 235),
    'button_hover': (59, 130, 246),
    'button_text': (255, 255, 255),
    'text': (30, 41, 59),
    'tree_background': (255, 255, 255),
    'tree_node': (219, 234, 254),
    'tree_current': (245, 158, 11),
    'tree_edge': (148, 163, 184),
    'path': (52, 211, 153),
    'panel_border': (226, 232, 240)
}

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
        
    def draw(self, screen, is_active=False):
        if is_active:
            pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=8)
            pygame.draw.rect(screen, UI_COLORS['button'], self.rect, 2, border_radius=8)
            text_surface = self.font.render(self.text, True, UI_COLORS['button'])
        else:
            color = UI_COLORS['button_hover'] if self.is_hovered else UI_COLORS['button']
            pygame.draw.rect(screen, color, self.rect, border_radius=8)
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
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, font, prefix_text="Speed"):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.font = font
        self.prefix_text = prefix_text
        self.dragging = False
        
        self.handle_radius = height // 2
        self.track_rect = pygame.Rect(x + self.handle_radius, y + height//4, 
                                    width - 2*self.handle_radius, height//2)
        self.update_handle_pos()
    
    def update_handle_pos(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_x = self.track_rect.x + ratio * self.track_rect.width
        self.handle_y = self.rect.centery
    
    def draw(self, screen):
        pygame.draw.rect(screen, (226, 232, 240), self.track_rect, border_radius=5)
        pygame.draw.circle(screen, UI_COLORS['button'], (int(self.handle_x), int(self.handle_y)), self.handle_radius)
        
        if self.prefix_text == "Speed":
            val_str = f"{self.val:.1f}x"
        elif self.prefix_text in ("N Nodes", "Branches"):
            val_str = f"{int(self.val)}"
        else:
            val_str = f"{self.val:.2f}"
            
        value_text = f"{self.prefix_text}: {val_str}"
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
        relative_x = max(0, min(self.track_rect.width, mouse_x - self.track_rect.x))
        ratio = relative_x / self.track_rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self.update_handle_pos()

def draw_grid(screen, grid_obj, agent_obj=None):
    if grid_obj is None:
        return
        
    for row in range(grid_obj.size):
        for col in range(grid_obj.size):
            node = grid_obj.get_node(row, col)
            if node is None: continue
            
            node_type = grid_obj.get_node_type(node)
            
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            
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
            
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (200, 200, 200), (x, y, CELL_SIZE, CELL_SIZE), 1)

def draw_web(screen, grid_obj, agent_obj=None):
    if grid_obj is None or not hasattr(grid_obj, 'node_positions'):
        return
        
    for u, v in grid_obj.graph.edges:
        if u not in grid_obj.node_positions or v not in grid_obj.node_positions: continue
        px, py = grid_obj.node_positions[u]
        qx, qy = grid_obj.node_positions[v]
        
        x1 = int(px * (GRID_WINDOW_SIZE - 40)) + 20
        y1 = int(py * (GRID_WINDOW_SIZE - 40)) + 20
        x2 = int(qx * (GRID_WINDOW_SIZE - 40)) + 20
        y2 = int(qy * (GRID_WINDOW_SIZE - 40)) + 20
        
        pygame.draw.line(screen, UI_COLORS['tree_edge'], (x1, y1), (x2, y2), 2)
        
    for node in grid_obj.graph.nodes:
        if node not in grid_obj.node_positions: continue
        px, py = grid_obj.node_positions[node]
        x = int(px * (GRID_WINDOW_SIZE - 40)) + 20
        y = int(py * (GRID_WINDOW_SIZE - 40)) + 20
        
        node_type = grid_obj.get_node_type(node)
        
        if agent_obj and getattr(agent_obj, 'is_finished', False) and agent_obj.path and node in agent_obj.path:
            color = COLORS[NodeType.PATH] if node_type not in (NodeType.START, NodeType.GOAL) else COLORS[node_type]
        elif agent_obj and getattr(agent_obj, 'current_node', None) == node:
            color = UI_COLORS['path']
        elif agent_obj and node in getattr(agent_obj, 'visited', set()):
            color = COLORS[NodeType.MARKED] if node_type not in (NodeType.START, NodeType.GOAL) else COLORS[node_type]
        else:
            color = COLORS.get(node_type, UI_COLORS['tree_node'])
            
        text = pygame.font.SysFont('segoeui, arial', 10, bold=True).render(str(node), True, UI_COLORS['text'])
        text_rect = text.get_rect(center=(x, y))
        
        if isinstance(node, str) and not node.isdigit():
            width = text_rect.width + 12
            height = text_rect.height + 8
            rect = pygame.Rect(0, 0, width, height)
            rect.center = (x, y)
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, UI_COLORS['text'], rect, 1, border_radius=6)
            screen.blit(text, text_rect)
        else:
            pygame.draw.circle(screen, color, (x, y), 12)
            pygame.draw.circle(screen, UI_COLORS['text'], (x, y), 12, 1)
            screen.blit(text, text_rect)

def draw_tree_visualization(screen, font, agent):
    tree_x = GRID_WINDOW_SIZE
    tree_panel = pygame.Rect(tree_x, 0, TREE_PANEL_WIDTH, GRID_WINDOW_SIZE)
    pygame.draw.rect(screen, UI_COLORS['tree_background'], tree_panel)
    pygame.draw.rect(screen, UI_COLORS['panel_border'], tree_panel, 2)
    
    if not agent or not hasattr(agent, 'current_node') or not agent.current_node:
        title_text = font.render("Search Tree", True, UI_COLORS['text'])
        screen.blit(title_text, (tree_x + 10, 10))
        screen.blit(font.render("No active search.", True, UI_COLORS['text']), (tree_x + 10, 50))
        return

    if getattr(agent, 'is_finished', False):
        if not hasattr(agent, 'path') or not agent.path:
            title_text = font.render("Result: No Path Found", True, UI_COLORS['text'])
            screen.blit(title_text, (tree_x + 10, 10))
            return
            
        title_text = font.render("Result: Final Path", True, UI_COLORS['text'])
        screen.blit(title_text, (tree_x + 10, 10))
        
        node_radius = 15
        padding = 45 
        nodes_per_row = (TREE_PANEL_WIDTH - 20) // padding
        
        positions = []
        for i, node in enumerate(agent.path):
            row = i // nodes_per_row
            col = i % nodes_per_row
            
            x = tree_x + 30 + (col * padding)
            y = 70 + (row * padding)
            positions.append((x, y, node))
            
        for i in range(len(positions) - 1):
            x1, y1, _ = positions[i]
            x2, y2, _ = positions[i+1]
            pygame.draw.line(screen, UI_COLORS['path'], (x1, y1), (x2, y2), 4)
            
        for x, y, node in positions:
            color = UI_COLORS['tree_current'] if node in (agent.path[0], agent.path[-1]) else UI_COLORS['path']
            rect = pygame.Rect(x - 25, y - 15, 50, 30)
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, UI_COLORS['text'], rect, 1, border_radius=6)
            
            node_str = f"({node[0]},{node[1]})" if isinstance(node, tuple) else str(node)
            text = pygame.font.SysFont('segoeui, arial', 12, bold=True).render(node_str, True, UI_COLORS['text'])
            screen.blit(text, text.get_rect(center=rect.center))
            
        return

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
    if hasattr(agent, 'tree'):
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

    node_width = 50
    node_height = 30
    
    absolute_depth = 0
    trace = agent.view_root
    while hasattr(agent, 'parents') and agent.parents.get(trace):
        trace = agent.parents.get(trace)
        absolute_depth += 1

    node_positions = {}
    tier_height = GRID_WINDOW_SIZE // 6

    for level, nodes in levels.items():
        y = tier_height * (level + 1)
        depth_label = pygame.font.SysFont('segoeui, arial', 14, bold=True).render(f"Depth {absolute_depth + level}", True, (150, 150, 180))
        screen.blit(depth_label, (tree_x + 10, y - 10))
        
        spacing = (TREE_PANEL_WIDTH - 70) // (len(nodes) + 1)
        for i, node in enumerate(nodes):
            x = tree_x + 60 + (spacing * (i + 1))
            node_positions[node] = (x, y)

    curr_path_set = set()
    tr = current
    while hasattr(agent, 'parents') and tr:
        curr_path_set.add(tr)
        tr = agent.parents.get(tr)

    for level in range(4):
        for parent_node in levels.get(level, []):
            if parent_node in node_positions:
                px, py = node_positions[parent_node]
                for child_node in children_map.get(parent_node, []):
                    if child_node in node_positions:
                        cx, cy = node_positions[child_node]
                        is_path = parent_node in curr_path_set and child_node in curr_path_set
                        color = UI_COLORS['tree_current'] if is_path else UI_COLORS['tree_edge']
                        thickness = 3 if is_path else 1
                        pygame.draw.line(screen, color, (px, py), (cx, cy), thickness)

    for level, nodes in levels.items():
        for node in nodes:
            x, y = node_positions[node]
            if node == current:
                color = UI_COLORS['tree_current']
            elif hasattr(agent, 'visited') and node in agent.visited:
                color = (220, 220, 220)
            else:
                color = UI_COLORS['tree_node']
                
            rect = pygame.Rect(x - node_width//2, y - node_height//2, node_width, node_height)
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, UI_COLORS['text'], rect, 1, border_radius=6)
            
            node_str = f"({node[0]},{node[1]})" if isinstance(node, tuple) else str(node)
            text = pygame.font.SysFont('segoeui, arial', 12, bold=True).render(node_str, True, UI_COLORS['text'])
            screen.blit(text, text.get_rect(center=rect.center))


def get_frontier_nodes(agent):
    if not agent or not hasattr(agent, 'frontier'):
        return []
    
    raw_list = list(agent.frontier)
    agent_name = getattr(agent.__class__, '__name__', '')
    
    if agent_name in ('AStar_SearchAgent', 'Greedy_SearchAgent'):
        try:
            raw_list = sorted(raw_list)
        except TypeError:
            pass
    elif agent_name in ('DFS_SearchAgent', 'IDDFS_SearchAgent'):
        raw_list = raw_list[::-1]
    
    nodes = []
    for item in raw_list:
        if isinstance(item, tuple):
            if len(item) == 2 and isinstance(item[0], int): 
                nodes.append((item, "")) 
            elif len(item) == 2 and isinstance(item[0], tuple): 
                nodes.append((item[0], f"D:{item[1]}")) 
            elif len(item) == 3: 
                nodes.append((item[2], f"Cost:{int(item[0])}")) 
            else: 
                nodes.append((item, ""))
        else:
            nodes.append((item, ""))
    return nodes

def draw_bottom_panel(screen, font, agent):
    bottom_rect = pygame.Rect(0, GRID_WINDOW_SIZE, TOTAL_WINDOW_WIDTH, BOTTOM_PANEL_HEIGHT)
    pygame.draw.rect(screen, UI_COLORS['tree_background'], bottom_rect)
    pygame.draw.rect(screen, UI_COLORS['panel_border'], bottom_rect, 2)
    
    title = font.render("Open-List / Priority Queue Frontier", True, UI_COLORS['text'])
    screen.blit(title, (20, GRID_WINDOW_SIZE + 10))
    
    if not agent or not hasattr(agent, 'frontier') or not agent.frontier:
        screen.blit(font.render("No frontier active.", True, UI_COLORS['tree_edge']), (20, GRID_WINDOW_SIZE + 50))
        return
        
    nodes = get_frontier_nodes(agent)
    
    max_visible = 10
    visible_nodes = nodes[:max_visible]
    visible_nodes.reverse()
    
    x_offset = 20
    y_offset = GRID_WINDOW_SIZE + 50
    node_width = 80
    node_height = 50
    
    if len(nodes) > max_visible:
        screen.blit(font.render("...", True, UI_COLORS['text']), (x_offset, y_offset + 10))
        x_offset += 40
        
    for i, item in enumerate(visible_nodes):
        node, meta = item
            
        rect = pygame.Rect(x_offset, y_offset, node_width, node_height)
        
        bg_color = UI_COLORS['button'] if i == len(visible_nodes) - 1 else UI_COLORS['tree_node']
        text_color = (255, 255, 255) if i == len(visible_nodes) - 1 else UI_COLORS['text']
        
        pygame.draw.rect(screen, bg_color, rect, border_radius=6)
        pygame.draw.rect(screen, UI_COLORS['text'], rect, 1, border_radius=6)
        
        node_str = f"({node[0]},{node[1]})" if isinstance(node, tuple) else str(node)
        node_text = pygame.font.SysFont('segoeui, arial', 14, bold=True).render(node_str, True, text_color)
        
        if meta:
            screen.blit(node_text, node_text.get_rect(centerx=rect.centerx, centery=rect.centery - 8))
            meta_text = pygame.font.SysFont('segoeui, arial', 12, bold=True).render(meta, True, (220, 220, 220) if i == len(visible_nodes) - 1 else (100, 100, 100))
            screen.blit(meta_text, meta_text.get_rect(centerx=rect.centerx, centery=rect.centery + 10))
        else:
            screen.blit(node_text, node_text.get_rect(centerx=rect.centerx, centery=rect.centery))
        
        x_offset += node_width + 10

def draw_popup(screen, font, agent, elapsed_time):
    if not agent or not getattr(agent, 'is_finished', False): return
    
    overlay = pygame.Surface((GRID_WINDOW_SIZE, GRID_WINDOW_SIZE))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    popup = pygame.Rect(100, 150, 400, 300)
    pygame.draw.rect(screen, UI_COLORS['background'], popup, border_radius=10)
    pygame.draw.rect(screen, UI_COLORS['panel_border'], popup, 2, border_radius=10)
    
    title = pygame.font.SysFont('segoeui, arial', 28, bold=True).render("Search Completed!", True, UI_COLORS['button'])
    screen.blit(title, title.get_rect(center=(300, 180)))
    
    metrics = [
        f"Time Elapsed: {elapsed_time:.3f} s",
        f"Nodes Expanded: {len(getattr(agent, 'visited', []))}",
        f"Path Length: {len(getattr(agent, 'path', [])) if getattr(agent, 'path', []) else 'No Path'}"
    ]
    
    y = 240
    for m in metrics:
        text = font.render(m, True, UI_COLORS['text'])
        screen.blit(text, text.get_rect(center=(300, y)))
        y += 40

def main():
    pygame.init()
    screen = pygame.display.set_mode((TOTAL_WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pathfinding Visualizer")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont('segoeui, arial, helvetica', 24)
    button_font = pygame.font.SysFont('segoeui, arial, helvetica', 18, bold=True)
    playback_font = pygame.font.SysFont('segoeui, arial, helvetica', 16, bold=True)
    
    my_grid = GraphEnvironment(GRID_SIZE)
    current_agent = None
    algorithm_type = "None"
    
    search_running = False
    is_paused = False
    search_completed = False
    popup_dismissed = False
    close_popup_btn = Button(260, 360, 80, 30, "Close", button_font)
    
    last_step_time = 0
    use_euclidean = False
    
    search_start_time = 0
    accumulated_time = 0
    elapsed_time = 0
    
    panel_x_btn = GRID_WINDOW_SIZE + TREE_PANEL_WIDTH + 30
    
    # 1. Configuration Sidebar
    mode_button = Button(panel_x_btn, 20, 200, 35, "Mode: Visualizer", button_font)
    randomize_btn = Button(panel_x_btn, 65, 200, 30, "Randomize Graph", button_font)
    
    topology_modes = ["Grid", "Tree", "CSV"]
    topology_index = 0
    topology_button = Button(panel_x_btn, 105, 200, 30, f"Topology: {topology_modes[topology_index]}", button_font)
    
    # Grid specific configs
    obstacle_slider = Slider(panel_x_btn, 185, 200, 30, 0.0, 0.6, 0.20, button_font, "Obstacles")
    
    # Tree specific configs
    current_seed = random.randint(0, 99999)
    # Replaced seed button with render label dynamically positioned
    nodes_slider = Slider(panel_x_btn, 225, 200, 30, 5.0, 50.0, 20.0, button_font, "N Nodes")
    branch_slider = Slider(panel_x_btn, 275, 200, 30, 1.0, 5.0, 2.0, button_font, "Branches")
    random_start_btn = Button(panel_x_btn, 155, 95, 30, "Rand Start", button_font)
    random_goal_btn = Button(panel_x_btn + 105, 155, 95, 30, "Rand Goal", button_font)
    
    # 2. Algorithm Buttons
    y_start = 320
    bfs_button = Button(panel_x_btn, y_start, 95, 30, "BFS", button_font)
    dfs_button = Button(panel_x_btn + 105, y_start, 95, 30, "DFS", button_font)
    iddfs_button = Button(panel_x_btn, y_start + 35, 95, 30, "IDDFS", button_font)
    greedy_button = Button(panel_x_btn + 105, y_start + 35, 95, 30, "Greedy", button_font)
    astar_button = Button(panel_x_btn, y_start + 70, 200, 30, "A*", button_font)
    
    heuristic_button = Button(panel_x_btn, y_start + 105, 200, 30, "Heuristic: Manhat", button_font)
    
    # 3. Playback Controls
    y_pl = y_start + 150
    play_button = Button(panel_x_btn, y_pl, 60, 30, "Play", playback_font)
    pause_button = Button(panel_x_btn + 70, y_pl, 60, 30, "Pause", playback_font)
    step_button = Button(panel_x_btn + 140, y_pl, 60, 30, "Step", playback_font)

    speed_slider = Slider(panel_x_btn, y_pl + 55, 200, 30, 0.1, 5.0, 1.0, button_font, "Speed")
    reset_button = Button(panel_x_btn, y_pl + 100, 200, 30, "Reset", button_font)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if mode_button.handle_event(event):
                # Phase 4 feature block
                pass
                
            if topology_button.handle_event(event) and not search_running:
                topology_index = (topology_index + 1) % len(topology_modes)
                topology_button.text = f"Topology: {topology_modes[topology_index]}"
                
                if topology_modes[topology_index] == "Grid":
                    my_grid = GraphEnvironment(GRID_SIZE, seed=current_seed, obstacle_rate=obstacle_slider.val)
                elif topology_modes[topology_index] == "Tree":
                    my_grid = GraphEnvironment(size=int(nodes_slider.val), seed=current_seed, topology=GraphTopology.TREE, branching_factor=int(branch_slider.val))
                elif topology_modes[topology_index] == "CSV":
                    my_grid = GraphEnvironment(topology=GraphTopology.CSV)
                current_agent = None
                
            if topology_modes[topology_index] == "Tree" and not search_running:
                pass # removed logic because we stripped seed button interactable
                    
            if topology_modes[topology_index] == "CSV":
                if random_start_btn.handle_event(event) and not search_running:
                    if my_grid and len(my_grid.graph.nodes) >= 2:
                        my_grid.graph.nodes[my_grid.start_node]['type'] = NodeType.EMPTY
                        choices = [n for n in my_grid.graph.nodes if n != my_grid.goal_node]
                        my_grid.start_node = random.choice(choices)
                        my_grid.graph.nodes[my_grid.start_node]['type'] = NodeType.START
                        current_agent = None
                        search_completed = False

                if random_goal_btn.handle_event(event) and not search_running:
                    if my_grid and len(my_grid.graph.nodes) >= 2:
                        my_grid.graph.nodes[my_grid.goal_node]['type'] = NodeType.EMPTY
                        choices = [n for n in my_grid.graph.nodes if n != my_grid.start_node]
                        my_grid.goal_node = random.choice(choices)
                        my_grid.graph.nodes[my_grid.goal_node]['type'] = NodeType.GOAL
                        current_agent = None
                        search_completed = False
                
            if topology_modes[topology_index] != "CSV" and randomize_btn.handle_event(event) and not search_running:
                current_seed = random.randint(0, 99999)
                seed_button.text = f"Seed: {current_seed}"
                
                if topology_modes[topology_index] == "Grid":
                    my_grid = GraphEnvironment(GRID_SIZE, seed=current_seed, obstacle_rate=obstacle_slider.val)
                elif topology_modes[topology_index] == "Tree":
                    my_grid = GraphEnvironment(size=int(nodes_slider.val), seed=current_seed, topology=GraphTopology.TREE, branching_factor=int(branch_slider.val))
                    
                current_agent = None
                algorithm_type = "None"
                elapsed_time = 0
                accumulated_time = 0
                search_completed = False

            def init_agent():
                nonlocal search_running, is_paused, search_completed, accumulated_time, search_start_time, popup_dismissed
                search_running = False
                is_paused = False
                search_completed = False
                popup_dismissed = False
                accumulated_time = 0
                search_start_time = time.time()
                
            if bfs_button.handle_event(event) and not search_running and my_grid is not None:
                current_agent = BFS_SearchAgent(my_grid, my_grid.start_node)
                algorithm_type = "BFS"
                init_agent()
                
            if dfs_button.handle_event(event) and not search_running and my_grid is not None:
                current_agent = DFS_SearchAgent(my_grid, my_grid.start_node)
                algorithm_type = "DFS"
                init_agent()
                
            if iddfs_button.handle_event(event) and not search_running and my_grid is not None:
                current_agent = IDDFS_SearchAgent(my_grid, my_grid.start_node)
                algorithm_type = "ID-DFS"
                init_agent()
                
            if greedy_button.handle_event(event) and not search_running and my_grid is not None:
                current_agent = Greedy_SearchAgent(my_grid, my_grid.start_node, use_euclidean)
                algorithm_type = "Greedy"
                init_agent()
                
            if astar_button.handle_event(event) and not search_running and my_grid is not None:
                current_agent = AStar_SearchAgent(my_grid, my_grid.start_node, use_euclidean)
                algorithm_type = "A*"
                init_agent()
                
            if heuristic_button.handle_event(event) and not search_running:
                use_euclidean = not use_euclidean
                heuristic_button.text = "Heuristic: Euclidean" if use_euclidean else "Heuristic: Manhat"
            
            if search_completed and not popup_dismissed:
                if close_popup_btn.handle_event(event):
                    popup_dismissed = True

            # Playback Handles
            if play_button.handle_event(event) and current_agent is not None and not search_completed:
                if not search_running:
                    search_running = True
                    is_paused = False
                    search_start_time = time.time()
                elif is_paused:
                    is_paused = False
                    search_start_time = time.time()
                
            if pause_button.handle_event(event) and search_running:
                if not is_paused:
                    accumulated_time += time.time() - search_start_time
                is_paused = True
                
            if step_button.handle_event(event) and search_running and is_paused and current_agent and not current_agent.is_finished:
                current_agent.step()
                if current_agent.is_finished:
                    search_running = False
                    search_completed = True
            
            if reset_button.handle_event(event):
                if topology_modes[topology_index] == "Grid":
                    my_grid = GraphEnvironment(GRID_SIZE, seed=current_seed, obstacle_rate=obstacle_slider.val)
                elif topology_modes[topology_index] == "Tree":
                    my_grid = GraphEnvironment(size=int(nodes_slider.val), seed=current_seed, topology=GraphTopology.TREE, branching_factor=int(branch_slider.val))
                elif topology_modes[topology_index] == "CSV":
                    my_grid = GraphEnvironment(topology=GraphTopology.CSV)
                current_agent = None
                algorithm_type = "None"
                search_running = False
                is_paused = False
                search_completed = False
                accumulated_time = 0
            if topology_modes[topology_index] == "Grid" and not search_running:
                obstacle_slider.handle_event(event)
            elif topology_modes[topology_index] == "Tree" and not search_running:
                nodes_slider.handle_event(event)
                branch_slider.handle_event(event)
                
            speed_slider.handle_event(event)

        # Update Timing 
        if search_running and not is_paused and current_agent:
            current_time = pygame.time.get_ticks()
            step_delay = int(1000 / (speed_slider.val * 20))
            
            if not current_agent.is_finished:
                if current_time - last_step_time > step_delay:
                    current_agent.step()
                    last_step_time = current_time
                    elapsed_time = accumulated_time + (time.time() - search_start_time)
            else:
                elapsed_time = accumulated_time + (time.time() - search_start_time)
                search_running = False
                search_completed = True

        screen.fill(UI_COLORS['background'])

        # Draw Environment
        if topology_modes[topology_index] == "Grid":
            draw_grid(screen, my_grid, current_agent)
        elif topology_modes[topology_index] in ("Tree", "CSV"):
            draw_web(screen, my_grid, current_agent)
            
        # Draw Tree UI
        draw_tree_visualization(screen, font, current_agent)
        draw_bottom_panel(screen, font, current_agent)
        
        # Draw Side Control Panel
        panel_x = GRID_WINDOW_SIZE + TREE_PANEL_WIDTH
        panel_rect = pygame.Rect(panel_x, 0, CONTROL_PANEL_WIDTH + PADDING, WINDOW_HEIGHT)
        pygame.draw.rect(screen, UI_COLORS['background'], panel_rect)
        pygame.draw.line(screen, UI_COLORS['panel_border'], (panel_x, 0), (panel_x, WINDOW_HEIGHT), 2)
        
        y_status = y_pl + 145
        status_surface = font.render(f"Alg: {algorithm_type}", True, UI_COLORS['text'])
        screen.blit(status_surface, (panel_x + PADDING, y_status))
        
        if search_completed:
            state_str = "Completed"
        elif current_agent is not None and not search_running and not is_paused:
            state_str = "Ready"
        elif search_running:
            state_str = "Running"
        elif is_paused:
            state_str = "Paused"
        else:
            state_str = "Waiting"
            
        state_surface = font.render(f"State: {state_str}", True, UI_COLORS['text'])
        screen.blit(state_surface, (panel_x + PADDING, y_status + 30))

        mode_button.draw(screen)
        
        if topology_modes[topology_index] != "CSV":
            randomize_btn.draw(screen)
            
        topology_button.draw(screen)
        
        if topology_modes[topology_index] == "Grid":
            bg_rect = pygame.Rect(panel_x_btn - 10, 145, 220, 80)
            pygame.draw.rect(screen, (241, 245, 249), bg_rect, border_radius=8)
            pygame.draw.rect(screen, UI_COLORS['panel_border'], bg_rect, 2, border_radius=8)
            obstacle_slider.draw(screen)
            
        elif topology_modes[topology_index] == "Tree":
            bg_rect = pygame.Rect(panel_x_btn - 10, 145, 220, 170)
            pygame.draw.rect(screen, (241, 245, 249), bg_rect, border_radius=8)
            pygame.draw.rect(screen, UI_COLORS['panel_border'], bg_rect, 2, border_radius=8)
            screen.blit(button_font.render(f"Seed: {current_seed}", True, UI_COLORS['text']), (panel_x_btn, 160))
            nodes_slider.draw(screen)
            branch_slider.draw(screen)
            
        elif topology_modes[topology_index] == "CSV":
            bg_rect = pygame.Rect(panel_x_btn - 10, 145, 220, 50)
            pygame.draw.rect(screen, (241, 245, 249), bg_rect, border_radius=8)
            pygame.draw.rect(screen, UI_COLORS['panel_border'], bg_rect, 2, border_radius=8)
            random_start_btn.draw(screen)
            random_goal_btn.draw(screen)
            
        bfs_button.draw(screen, True if algorithm_type == "BFS" else False)
        dfs_button.draw(screen, True if algorithm_type == "DFS" else False)
        iddfs_button.draw(screen, True if algorithm_type == "ID-DFS" else False)
        greedy_button.draw(screen, True if algorithm_type == "Greedy" else False)
        astar_button.draw(screen, True if algorithm_type == "A*" else False)
        heuristic_button.draw(screen)
        
        play_button.draw(screen)
        pause_button.draw(screen)
        step_button.draw(screen)
        speed_slider.draw(screen)
        reset_button.draw(screen)
        
        # Popups
        if current_agent and getattr(current_agent, 'is_finished', False) and not popup_dismissed:
            draw_popup(screen, font, current_agent, elapsed_time)
            close_popup_btn.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()