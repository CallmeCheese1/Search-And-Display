from environment import NodeType

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
