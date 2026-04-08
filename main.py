import pygame
import sys
import time
import random
from environment import GraphEnvironment, NodeType, GraphTopology
from bfs_agent import BFS_SearchAgent
from dfs_agent import DFS_SearchAgent
from iddfs_agent import IDDFS_SearchAgent
from greedy_agent import Greedy_SearchAgent
from astar_agent import AStar_SearchAgent

from constants import (
    GRID_WINDOW_SIZE, TREE_PANEL_WIDTH, CONTROL_PANEL_WIDTH, BOTTOM_PANEL_HEIGHT, PADDING,
    TOTAL_WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, CELL_SIZE, OBSTACLE_RATE, COLORS, UI_COLORS
)
from ui_components import Button, Slider
from renderer import draw_grid, draw_web, draw_tree_visualization, draw_bottom_panel, draw_popup

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