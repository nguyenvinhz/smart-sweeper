WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
FPS = 60
TITLE = "SMART SWEEPER - AI"

SIDEBAR_W = 280
BOTTOM_PANEL_H = 180
TOOLBAR_H = 60
GRID_PADDING = 20
CELL_MARGIN = 0
MAX_CELL_SIZE = 40
MIN_CELL_SIZE = 15

class C:
    BG_BOARD = (30, 41, 59)
    BG_SIDEBAR = (38, 50, 56)
    BG_TOOLBAR = (30, 41, 59)
    
    TEXT_WHITE = (255, 255, 255)
    TEXT_MUTED = (156, 163, 175)
    
    BTN_BLUE = (59, 130, 246)
    BTN_GRAY = (75, 85, 99)
    
    INPUT_BG = (255, 255, 255)
    INPUT_TEXT = (15, 23, 42)
    
    CARD_BG = (38, 50, 56)
    CARD_BORDER_ORANGE = (249, 115, 22)
    CARD_BORDER_BLUE = (59, 130, 246)
    CARD_BORDER_GREEN = (16, 185, 129)
    
    TABLE_HEADER = (55, 65, 81)
    TABLE_ROW_ALT = (45, 55, 72)
    
    CELL_HIDDEN_CENTER = (203, 213, 225)
    CELL_HIDDEN_TOP = (248, 250, 252)
    CELL_HIDDEN_BOT = (100, 116, 139)
    CELL_REVEALED = (226, 232, 240)
    CELL_REVEALED_BORDER = (148, 163, 184)
    
    MINE_BG = (239, 68, 68)
    FLAG_COLOR = (220, 38, 38)
    
    PROGRESS_TRACK = (55, 65, 81)
    PROGRESS_FILL = (59, 130, 246)

NUMBER_COLORS = {
    1: (37, 99, 235),
    2: (22, 163, 74),
    3: (220, 38, 38),
    4: (79, 70, 229),
    5: (147, 51, 234),
    6: (13, 148, 136),
    7: (0, 0, 0),
    8: (64, 64, 64)
}

CATEGORIES = [
    {'name': '1. UNINFORMED'},
    {'name': '2. INFORMED'},
    {'name': '3. LOCAL SEARCH'},
    {'name': '4. NONDETERMINISTIC'},
    {'name': '5. CSP'},
    {'name': '6. ADVERSARIAL'},
]

ALGORITHM_LIST = [
    ("BFS",                 0, "bfs"),
    ("DFS",                 0, "dfs"),
    ("A* Search",           1, "astar"),
    ("Greedy Best-First",   1, "greedy"),
    ("Hill Climbing",       2, "hill_climbing"),
    ("Simulated Annealing", 2, "simulated_annealing"),
    ("AND-OR Search",       3, "and_or"),
    ("Belief State",        3, "belief_state"),
    ("AC-3",                4, "ac3"),
    ("Backtracking",        4, "backtracking"),
    ("Alpha-Beta Pruning",  5, "alpha_beta"),
    ("Minimax",             5, "minimax"),
]

STATE_SETUP = 0
STATE_RUNNING = 1
STATE_PAUSED = 2
STATE_FINISHED = 3
STATE_COMPARING = 4
STATE_COMPARE_RUNNING = 5
