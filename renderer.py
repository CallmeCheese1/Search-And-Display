import pygame
from environment import NodeType
from constants import (
    TOTAL_WINDOW_WIDTH, GRID_WINDOW_SIZE, BOTTOM_PANEL_HEIGHT, TREE_PANEL_WIDTH,
    CELL_SIZE, UI_COLORS, COLORS
)

#Super long, and honestly, I no longer feel like writing these comments. As the name might imply, this file handles the rendering. Consider it the graphics card of our application.

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
        
        # Render edge weight label at midpoint (only for weighted graphs, i.e. Tree topology)
        weight = grid_obj.graph[u][v].get('weight', None)
        if weight is not None:
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2
            weight_font = pygame.font.SysFont('segoeui, arial', 11, bold=True)
            weight_text = weight_font.render(str(weight), True, (200, 60, 60))
            weight_rect = weight_text.get_rect(center=(mid_x, mid_y))
            # Small background pill for readability
            bg_rect = weight_rect.inflate(6, 2)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=3)
            screen.blit(weight_text, weight_rect)
        
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
    
    popup = pygame.Rect(100, 150, 400, 340)
    pygame.draw.rect(screen, UI_COLORS['background'], popup, border_radius=10)
    pygame.draw.rect(screen, UI_COLORS['panel_border'], popup, 2, border_radius=10)
    
    title = pygame.font.SysFont('segoeui, arial', 28, bold=True).render("Search Completed!", True, UI_COLORS['button'])
    screen.blit(title, title.get_rect(center=(300, 180)))
    
    metrics = [
        f"Time Elapsed: {elapsed_time:.3f} s",
        f"Nodes Expanded: {len(getattr(agent, 'visited', []))}",
        f"Path Length: {len(getattr(agent, 'path', [])) if getattr(agent, 'path', []) else 'No Path'}",
        f"Peak Memory: {getattr(agent, 'max_memory_nodes', 0)} nodes"
    ]
    
    y = 240
    for m in metrics:
        text = font.render(m, True, UI_COLORS['text'])
        screen.blit(text, text.get_rect(center=(300, y)))
        y += 40

def draw_benchmark_results(screen, font, aggregated_data, chart_surface):
    start_y = 160
    start_x = 40
    
    # Two-line headers: (line1, line2)
    headers = [
        ("Algorithm", ""),
        ("Mean", "Time (s)"),
        ("Std", "Time"),
        ("Mean", "Expanded"),
        ("Std", "Expanded"),
        ("Peak", "Memory")
    ]
    col_widths = [110, 130, 100, 120, 120, 110]
    
    header_font = pygame.font.SysFont('segoeui, arial, helvetica', 18, bold=True)
    curr_x = start_x
    for i, (line1, line2) in enumerate(headers):
        text1 = header_font.render(line1, True, UI_COLORS['button'])
        screen.blit(text1, (curr_x, start_y))
        if line2:
            text2 = header_font.render(line2, True, UI_COLORS['button'])
            screen.blit(text2, (curr_x, start_y + 20))
        curr_x += col_widths[i]
        
    pygame.draw.line(screen, UI_COLORS['panel_border'], (start_x, start_y + 45), (start_x + 680, start_y + 45), 2)
    
    y = start_y + 55
    if aggregated_data:
        for alg, data in aggregated_data.items():
            row = [
                alg,
                f"{data['mean_time']:.5f}",
                f"{data['std_time']:.5f}",
                f"{data['mean_expanded']:.1f}",
                f"{data['std_expanded']:.1f}",
                f"{data.get('mean_memory', 0):.0f}"
            ]
            curr_x = start_x
            for i, val in enumerate(row):
                text = font.render(val, True, UI_COLORS['text'])
                screen.blit(text, (curr_x, y))
                curr_x += col_widths[i]
            y += 35
            
    if chart_surface:
        screen.blit(chart_surface, (start_x + 750, start_y))
