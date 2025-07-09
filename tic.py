import pygame
import sys
import random
import time

pygame.init()
pygame.mixer.init()

# --- Initialize Pygame Clock ---
clock = pygame.time.Clock() # Add this line to define the clock object

# --- Constants and Configurations ---
# Screen dimensions
SCREEN_INFO = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN_INFO.current_w, SCREEN_INFO.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Ultimate Tic Tac Toe")

# Game board dimensions
GRID_SIZE = 3 # For Ultimate Tic Tac Toe, the main board is 3x3 of mini-boards
BOARD_WIDTH, BOARD_HEIGHT = 600, 600
CELL_SIZE = BOARD_WIDTH // (GRID_SIZE * GRID_SIZE) # Size of the smallest cell

# Offsets to center the game board on the screen
OFFSET_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
OFFSET_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 100, 255)
GREEN = (0, 200, 0)
RED = (255, 50, 50)
DARK_GRAY = (50, 50, 50)

# Line widths for drawing
THIN_LINE_WIDTH = 1
MEDIUM_LINE_WIDTH = 3
THICK_LINE_WIDTH = 5
BOARD_HIGHLIGHT_WIDTH = 4 # Width for highlighting the current playable board

# Fonts
FONT = pygame.font.SysFont(None, 40)
BIG_FONT = pygame.font.SysFont(None, 80)
WINNER_FONT = pygame.font.SysFont(None, 100) # For displaying game winner

# --- Assets Loading ---
# Load and scale the icon
logo = pygame.image.load('assets/images/logo.png')
logo = pygame.transform.scale(logo, (50, 50))
pygame.display.set_icon(logo)

# Sound Variables
click_sound = pygame.mixer.Sound("assets/sound/click.mp3")
win_sound = pygame.mixer.Sound("assets/sound/win.mp3")
# Music tracks
MUSIC_TRACKS = {
    "Abstract Glitch": pygame.mixer.Sound("assets/sound/experimental-abstract-tech-glitch-179496.mp3"),
    "Samurai": pygame.mixer.Sound("assets/sound/samurai-127302.mp3"),
    "Coding Night": pygame.mixer.Sound("assets/sound/coding-night-112186.mp3"),
    "Synthetic Deceit": pygame.mixer.Sound("assets/sound/synthetic-deception-loopable-epic-cyberpunk-crime-music-157454.mp3")
}

# Image assets for buttons
ai_button_img = pygame.image.load("assets/images/ai-mode.png")
multi_button_img = pygame.image.load("assets/images/multiplayer.png")
restart_button_img = pygame.image.load("assets/images/restart.png")
quit_button_img = pygame.image.load("assets/images/quit.png")
info_btn_img = pygame.image.load("assets/images/info.png")
back_button_img = pygame.image.load("assets/images/back.png")

# Background image for the game board
board_bg = pygame.image.load("assets/images/back3.jpg")
board_bg = pygame.transform.scale(board_bg, (BOARD_WIDTH + 60, BOARD_HEIGHT + 60)) # Scaled slightly larger than board

# --- Global Game State Variables ---
dropdown_open = False
selected_track_name = "Abstract Glitch"
current_music = None # Holds the currently playing music Sound object

# Loading Screen Tips
LOADING_TIPS = [
    "Tip: Focus the center, control the grid.",
    "Hint: Corners aren't just edges — they’re strategy.",
    "Tip: Outthink, don’t just outplay.",
    "Hint: Use small wins to control the big board.",
    "Tip: The last move can set the next trap.",
    "Tip: Winning one board isn't enough. Think ahead.",
    "Did you know? The AI thinks 6 moves deep.", # This might be an exaggeration or goal
    "Strategy: Send your opponent to weak boards.",
    "The AI adapts — break patterns to stay unpredictable.",
    "Rule: You must play in the board matching the cell you last picked.",
    "Pro Tip: Force a draw on a board to open up options.",
    "Watch closely — your move decides theirs.",
    "Rule: 3 local wins = global domination.",
    "Hint: Each move shapes the future. Plan wisely."
]

# --- Game Utility Functions ---
def draw_grid():
    """Draws the main 3x3 grid and the inner 3x3 grids for Ultimate Tic Tac Toe."""
    # Draw thick lines for the main 3x3 grid
    for i in range(1, GRID_SIZE):
        # Horizontal lines
        pygame.draw.line(screen, BLACK,
                         (OFFSET_X, OFFSET_Y + i * BOARD_HEIGHT // GRID_SIZE),
                         (OFFSET_X + BOARD_WIDTH, OFFSET_Y + i * BOARD_HEIGHT // GRID_SIZE),
                         THICK_LINE_WIDTH)
        # Vertical lines
        pygame.draw.line(screen, BLACK,
                         (OFFSET_X + i * BOARD_WIDTH // GRID_SIZE, OFFSET_Y),
                         (OFFSET_X + i * BOARD_WIDTH // GRID_SIZE, OFFSET_Y + BOARD_HEIGHT),
                         THICK_LINE_WIDTH)

    # Draw thin lines for the inner 3x3 cells within each mini-board
    for i in range(1, GRID_SIZE * GRID_SIZE):
        # Horizontal lines for cells
        pygame.draw.line(screen, GRAY,
                         (OFFSET_X, OFFSET_Y + i * CELL_SIZE),
                         (OFFSET_X + BOARD_WIDTH, OFFSET_Y + i * CELL_SIZE),
                         THIN_LINE_WIDTH)
        # Vertical lines for cells
        pygame.draw.line(screen, GRAY,
                         (OFFSET_X + i * CELL_SIZE, OFFSET_Y),
                         (OFFSET_X + i * CELL_SIZE, OFFSET_Y + BOARD_HEIGHT),
                         THIN_LINE_WIDTH)

def get_board_and_cell(pos):
    """
    Converts screen coordinates to (board_index, cell_index).
    Returns (None, None) if the position is outside the game board.
    """
    x, y = pos
    x -= OFFSET_X
    y -= OFFSET_Y
    if not (0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT):
        return None, None # Outside board area

    board_x = x // (CELL_SIZE * GRID_SIZE)
    board_y = y // (CELL_SIZE * GRID_SIZE)
    cell_x = (x % (CELL_SIZE * GRID_SIZE)) // CELL_SIZE
    cell_y = (y % (CELL_SIZE * GRID_SIZE)) // CELL_SIZE

    board_index = board_x + board_y * GRID_SIZE
    cell_index = cell_x + cell_y * GRID_SIZE
    return board_index, cell_index

def draw_moves(moves, boards_won, current_board):
    """
    Draws X's and O's on the board, highlights the current playable board,
    and draws indicators for won mini-boards.
    """
    for board_idx in range(9):
        for cell_idx in range(9):
            val = moves[board_idx][cell_idx]
            if val:
                # Calculate pixel position for the center of the cell
                # board_x, board_y are 0, 1, or 2 for the main 3x3 grid
                bx, by = board_idx % GRID_SIZE, board_idx // GRID_SIZE
                # cell_x, cell_y are 0, 1, or 2 for the 3x3 cells within a mini-board
                cx, cy = cell_idx % GRID_SIZE, cell_idx // GRID_SIZE

                # Global x, y position on the entire 9x9 grid
                global_cell_x = (bx * GRID_SIZE) + cx
                global_cell_y = (by * GRID_SIZE) + cy

                px = OFFSET_X + global_cell_x * CELL_SIZE + CELL_SIZE // 2
                py = OFFSET_Y + global_cell_y * CELL_SIZE + CELL_SIZE // 2

                # Render X or O
                text = FONT.render(val, True, RED if val == "X" else BLUE)
                text_rect = text.get_rect(center=(px, py))
                screen.blit(text, text_rect)

    # Highlight the current playable board
    if current_board is not None and boards_won[current_board] == "":
        bx, by = current_board % GRID_SIZE, current_board // GRID_SIZE
        rect = pygame.Rect(OFFSET_X + bx * GRID_SIZE * CELL_SIZE,
                           OFFSET_Y + by * GRID_SIZE * CELL_SIZE,
                           GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
        pygame.draw.rect(screen, BLUE, rect, BOARD_HIGHLIGHT_WIDTH)

    # Draw indicator for won mini-boards
    for i in range(9):
        if boards_won[i]:
            bx, by = i % GRID_SIZE, i // GRID_SIZE
            center = (OFFSET_X + bx * GRID_SIZE * CELL_SIZE + CELL_SIZE * 1.5,
                      OFFSET_Y + by * GRID_SIZE * CELL_SIZE + CELL_SIZE * 1.5)
            # Use GREEN for 'X' wins, RED for 'O' wins (consistent with symbol colors)
            color = RED if boards_won[i] == "X" else BLUE
            pygame.draw.circle(screen, color, center, CELL_SIZE, THICK_LINE_WIDTH) # Outline circle
            # Optionally, draw a larger transparent circle or a faded X/O
            s = pygame.Surface((CELL_SIZE * 3, CELL_SIZE * 3), pygame.SRCALPHA) # per-pixel alpha
            s.fill((0,0,0,0)) # transparent
            text_surf = WINNER_FONT.render(boards_won[i], True, (color[0], color[1], color[2], 100)) # Semi-transparent
            text_rect = text_surf.get_rect(center=(CELL_SIZE * 1.5, CELL_SIZE * 1.5))
            s.blit(text_surf, text_rect)
            screen.blit(s, (OFFSET_X + bx * 3 * CELL_SIZE, OFFSET_Y + by * 3 * CELL_SIZE))


def draw_hover(moves, boards_won, current_board, hover_cell, turn):
    """
    Draws a green outline on the cell currently hovered by the mouse,
    if that cell is a valid move.
    `hover_cell` is a tuple (global_cell_x, global_cell_y).
    """
    global_x, global_y = hover_cell
    # Calculate the board_index and cell_index from global coordinates
    board_x = global_x // GRID_SIZE
    board_y = global_y // GRID_SIZE
    board_index = board_x + board_y * GRID_SIZE

    cell_x = global_x % GRID_SIZE
    cell_y = global_y % GRID_SIZE
    cell_index = cell_x + cell_y * GRID_SIZE

    # Check if the move is valid:
    # 1. The board is the current_board (or any board if current_board is None)
    # 2. The cell is empty
    # 3. The mini-board is not already won
    is_valid_hover = (current_board is None or current_board == board_index) and \
                     moves[board_index][cell_index] == "" and \
                     boards_won[board_index] == ""

    if is_valid_hover:
        rect = pygame.Rect(OFFSET_X + global_x * CELL_SIZE,
                           OFFSET_Y + global_y * CELL_SIZE,
                           CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, GREEN, rect, MEDIUM_LINE_WIDTH) # Solid green outline

def check_win(board):
    """
    Checks if a player has won a single 3x3 board.
    Returns 'X', 'O', or '' (empty string) for no winner.
    """
    lines = [
        [0,1,2], [3,4,5], [6,7,8], # Horizontal
        [0,3,6], [1,4,7], [2,5,8], # Vertical
        [0,4,8], [2,4,6]           # Diagonal
    ]
    for a,b,c in lines:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return ""

def game_winner(boards_won):
    """
    Checks if a player has won the overall Ultimate Tic Tac Toe game.
    Returns 'X', 'O', or '' for no winner.
    """
    return check_win(boards_won)

def is_board_full(board_moves):
    """Checks if a given mini-board is full (all cells occupied)."""
    return all(cell != "" for cell in board_moves)

def get_empty_cells(board_moves):
    """Returns a list of indices of empty cells in a given mini-board."""
    return [cell_idx for cell_idx, mark in enumerate(board_moves) if mark == ""]

# --- AI Logic (Minimax-like heuristic) ---
# This AI prioritizes immediate wins/blocks and strategic board control.
def ai_move(moves, boards_won, current_board, difficulty="hard"):
    """
    Determines the best move for the AI ('O') using a heuristic-based approach.
    Prioritizes winning, blocking, and strategic board control.
    """
    ai_mark = "O"
    player_mark = "X"

    # Determine valid boards the AI can play in
    valid_boards_to_play_in = []
    if current_board is None: # AI can play anywhere
        valid_boards_to_play_in = [i for i in range(9) if boards_won[i] == "" and not is_board_full(moves[i])]
    elif boards_won[current_board] == "" and not is_board_full(moves[current_board]):
        valid_boards_to_play_in = [current_board]
    else: # Current board is won or full, AI can play anywhere
        valid_boards_to_play_in = [i for i in range(9) if boards_won[i] == "" and not is_board_full(moves[i])]

    if not valid_boards_to_play_in:
        return None, None # No valid moves left (game over or error)

    best_score = -float('inf')
    best_moves = [] # List to store (board_idx, cell_idx) tuples for moves with the same best_score

    for board_idx in valid_boards_to_play_in:
        for cell_idx in get_empty_cells(moves[board_idx]):
            score = 0 # Initialize score for this specific move

            # --- Simulate the move to evaluate its impact ---
            temp_moves = [list(row) for row in moves] # Deep copy of moves
            temp_boards_won = list(boards_won) # Copy of boards_won

            temp_moves[board_idx][cell_idx] = ai_mark

            # Check if this move wins the local board
            local_win_state = check_win(temp_moves[board_idx])
            if local_win_state == ai_mark:
                temp_boards_won[board_idx] = ai_mark
                # Check if this local win results in a global win
                if game_winner(temp_boards_won) == ai_mark:
                    score += 1000 # AI wins the game! Very high priority
                else:
                    score += 100 # AI wins a local board
            elif is_board_full(temp_moves[board_idx]) and local_win_state == "": # Local board becomes a tie
                score += 5 # Neutral, avoids losing control of the board

            # --- Evaluate where the player will be sent ---
            next_board_for_player = cell_idx # Player will be sent to the board corresponding to the cell AI just picked

            # Scenario 1: Player is sent to an already won or full board ("dead" board)
            if temp_boards_won[next_board_for_player] != "" or is_board_full(temp_moves[next_board_for_player]):
                score += 20 # Excellent! Player is sent to a "dead" board, AI can play anywhere next turn

            # Scenario 2: Player is sent to a live board
            else:
                # Predict player's immediate win/block opportunity in the next board
                player_potential_win = find_potential_win_or_block(temp_moves[next_board_for_player], player_mark)
                if player_potential_win is not None:
                    # Player can immediately win their next board if sent here
                    score -= 50 # Bad! Avoid sending player to an immediately winning position

                # Check if sending player to a board where they can set up a fork (more complex)
                # For simplicity, if the next board for player has a central cell available, it's less desirable
                if temp_moves[next_board_for_player][4] == "":
                    score -= 5 # Player can take center of next board (often good for them)

            # --- Check for immediate blocks (preventing player's local win) ---
            # If the current board_idx is one where the player could have won in this turn
            # and AI's move blocks that win, give it high priority.
            player_potential_win_on_current_board = find_potential_win_or_block(moves[board_idx], player_mark)
            if player_potential_win_on_current_board == cell_idx:
                score += 70 # Crucial: Block opponent's immediate local win

            # --- General Positional Scoring (within the current board_idx) ---
            # Prioritize center, then corners for local moves as they offer more lines.
            if cell_idx == 4: score += 10 # Center cell
            elif cell_idx in [0, 2, 6, 8]: score += 5 # Corner cells

            # Add a small random factor to break ties and make AI less predictable (less "perfect")
            score += random.uniform(-0.1, 0.1)

            # --- Update best move(s) ---
            if score > best_score:
                best_score = score
                best_moves = [(board_idx, cell_idx)] # Start a new list of best moves
            elif score == best_score:
                best_moves.append((board_idx, cell_idx)) # Add to existing list if score is equal

    # If multiple moves have the same best score, pick one randomly to add variation
    if best_moves:
        return random.choice(best_moves)

    # Fallback: if no strategic move is found (should ideally not happen if game is playable)
    # This ensures the AI always makes a valid move if available.
    if valid_boards_to_play_in:
        board = random.choice(valid_boards_to_play_in)
        cell = random.choice(get_empty_cells(moves[board]))
        return board, cell

    return None, None # No moves left or unforeseen edge case

def find_potential_win_or_block(board, mark):
    """
    Helper for AI: Checks if a given player `mark` can win a local board
    in the next move, and returns the cell index needed to win, or None.
    """
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for line in lines:
        vals = [board[i] for i in line]
        if vals.count(mark) == 2 and vals.count("") == 1:
            return line[vals.index("")] # Returns the empty cell to complete the line
    return None

# --- UI Elements Classes ---
class Button:
    """A simple button class to handle image buttons with hover and click effects."""
    def __init__(self, image, pos, scale=1.0):
        original_width = image.get_width()
        original_height = image.get_height()
        self.image = pygame.transform.scale(image, (int(original_width * scale), int(original_height * scale)))
        self.rect = self.image.get_rect(center=pos)
        self.clicked = False # Prevents multiple clicks on a single press
        self.original_image = self.image # Store original for hover scaling

    def draw(self, surface):
        action = False
        mouse_pos = pygame.mouse.get_pos()

        # Hover effect: scale up slightly
        if self.rect.collidepoint(mouse_pos):
            hover_scale = 1.05
            hover_image = pygame.transform.scale(self.original_image, (int(self.rect.width * hover_scale), int(self.rect.height * hover_scale)))
            hover_rect = hover_image.get_rect(center=self.rect.center)
            surface.blit(hover_image, hover_rect)
        else:
            surface.blit(self.image, self.rect)

        # Click detection
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(mouse_pos) and not self.clicked:
            self.clicked = True
            click_sound.play() # Play sound on click
            action = True
        elif not pygame.mouse.get_pressed()[0]:
            self.clicked = False # Reset click state when mouse button is released
        return action

class Dropdown:
    """A customizable dropdown menu for selecting options."""
    def __init__(self, title, options, pos, width=200, height=40):
        self.title = title # Initial displayed text (e.g., selected track name)
        self.options = options # List of selectable options
        self.pos = pos # (x, y) for the top-left of the dropdown
        self.width = width
        self.height = height
        self.open = False # State: True if dropdown list is visible
        self.selected = title # Currently selected option
        self.font = FONT # Using the global FONT for consistency
        self.disabled_zone = [] # Stores rectangles that block input when dropdown is open

    def draw(self, screen_surface):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
        selected_option = None # To return the newly selected option

        # --- Draw main dropdown box ---
        rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)

        # Hover effect for main box
        is_hover = rect.collidepoint(mouse)
        color = (220, 220, 220) if is_hover else (200, 200, 200)

        pygame.draw.rect(screen_surface, color, rect)
        pygame.draw.rect(screen_surface, BLACK, rect, 2) # Border

        text = self.font.render(self.selected, True, BLACK)
        # Center the text vertically, align left with padding
        screen_surface.blit(text, (self.pos[0] + 10, self.pos[1] + (self.height - text.get_height()) // 2))

        # Handle dropdown click toggle
        if click and is_hover and not self.clicked: # Use self.clicked to debounce
            self.open = not self.open
            self.clicked = True
            pygame.time.wait(150) # Short delay to prevent rapid toggling
        elif not click:
            self.clicked = False

        # --- Draw dropdown options if open ---
        self.disabled_zone = [rect] # Always block clicks on the main button
        if self.open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.pos[0], self.pos[1] + (i + 1) * self.height, self.width, self.height)
                is_option_hover = option_rect.collidepoint(mouse)

                # Background hover color for options
                bg_color = (180, 180, 180) if is_option_hover else (220, 220, 220)
                pygame.draw.rect(screen_surface, bg_color, option_rect)
                pygame.draw.rect(screen_surface, BLACK, option_rect, 1) # Border

                opt_text = self.font.render(option, True, BLACK)
                screen_surface.blit(opt_text, (option_rect.x + 10, option_rect.y + (self.height - opt_text.get_height()) // 2))

                self.disabled_zone.append(option_rect) # Add option rectangles to disabled zone

                if click and is_option_hover and not self.clicked:
                    self.selected = option
                    selected_option = option # Capture the selected option
                    self.open = False
                    self.clicked = True # Debounce
                    pygame.time.wait(150)

        return selected_option # Return the selected option or None

    def is_open(self):
        """Returns True if the dropdown is currently open."""
        return self.open

    def blocks_input_at(self, pos):
        """Checks if a given position `pos` (e.g., mouse click) is within the dropdown's active area."""
        return any(rect.collidepoint(pos) for rect in self.disabled_zone)

# --- Game State Management Functions ---
def reset_game():
    """Resets all game state variables to their initial values."""
    moves = [["" for _ in range(9)] for _ in range(9)] # 9 mini-boards, each with 9 cells
    boards_won = ["" for _ in range(9)] # State of each mini-board ('X', 'O', or '')
    turn = "X" # X starts the game
    current_board = None # None means player can play in any board
    global_winner = "" # Overall game winner
    return moves, boards_won, turn, current_board, global_winner

def show_loading_screen(duration=2.5):
    """
    Displays a loading screen with a random tip and a progress bar.
    Fades out at the end.
    """
    start_time = time.time()
    tip = random.choice(LOADING_TIPS)
    bar_width = 400
    bar_height = 30
    bar_x = SCREEN_WIDTH // 2 - bar_width // 2
    bar_y = SCREEN_HEIGHT // 2 + 60
    load_color = (100, 200, 100)
    border_color = WHITE

    # Fade-in surface
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill(BLACK)
    fade_alpha = 255

    while True:
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1)

        screen.fill(DARK_GRAY)

        # Loading text
        loading_text = BIG_FONT.render("Loading...", True, WHITE)
        screen.blit(loading_text, (SCREEN_WIDTH // 2 - loading_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        # Tip text
        tip_rendered = FONT.render(tip, True, WHITE)
        screen.blit(tip_rendered, (SCREEN_WIDTH // 2 - tip_rendered.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

        # Draw progress bar border
        pygame.draw.rect(screen, border_color, (bar_x, bar_y, bar_width, bar_height), 2)
        # Draw filled progress bar
        current_fill_width = int(bar_width * progress)
        pygame.draw.rect(screen, load_color, (bar_x, bar_y, current_fill_width, bar_height))

        # Apply fade-in effect if active
        if fade_alpha > 0:
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
            fade_alpha = max(0, fade_alpha - 5) # Decrease alpha to fade out

        pygame.display.flip()
        clock.tick(60)

        if elapsed >= duration and fade_alpha == 0:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def show_game_over_screen(winner_text):
    """Displays a game over screen with winner/tie message and restart/quit options."""
    global current_music
    if current_music:
        current_music.stop() # Stop background music
    win_sound.play() # Play win sound effect

    restart_btn = Button(restart_button_img, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50), scale=0.8)
    quit_btn = Button(quit_button_img, (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 + 50), scale=0.8)

    # Fade-in effect
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill(BLACK)
    fade_alpha = 255

    while True:
        screen.fill(DARK_GRAY) # Background for game over screen

        # Winner text
        text_color = RED if "X" in winner_text else (BLUE if "O" in winner_text else WHITE)
        rendered_text = WINNER_FONT.render(winner_text, True, text_color)
        text_rect = rendered_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(rendered_text, text_rect)

        if restart_btn.draw(screen):
            return "restart"
        if quit_btn.draw(screen):
            return "quit"

        # Apply fade-in effect
        if fade_alpha > 0:
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
            fade_alpha = max(0, fade_alpha - 10) # Decrease alpha

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

def wrap_text(text, font_obj, max_width):
    """Wraps text into multiple lines to fit within a maximum width."""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font_obj.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip()) # Add the last line
    return lines

def show_rules_screen():
    """Displays the game rules, allowing scrolling."""
    try:
        with open("rules.txt", "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    except Exception as e:
        raw_lines = [f"Error loading rules: {str(e)}", "Please ensure rules.txt exists."]

    margin_x = 50
    line_spacing = 10
    wrapped_lines = []
    for line in raw_lines:
        wrapped = wrap_text(line.strip(), FONT, SCREEN_WIDTH - 2 * margin_x)
        wrapped_lines.extend(wrapped)

    scroll_y = 0 # Current scroll position
    velocity = 0 # For inertia scrolling
    friction = 0.9 # How fast velocity decays
    dragging = False
    drag_start_y = 0 # Y position where drag started

    # Calculate total content height and max scrollable amount
    content_height = len(wrapped_lines) * (FONT.get_height() + line_spacing)
    display_area_height = SCREEN_HEIGHT - 200 # Area for text, leaving space for top button
    max_scroll = max(0, content_height - display_area_height)

    back_button = Button(back_button_img, (SCREEN_WIDTH // 2, 80), scale=0.5)

    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill(BLACK)
    fade_alpha = 255

    showing_rules = True
    while showing_rules:
        screen.fill(BLACK) # Background for rules screen

        # Handle scroll inertia
        if not dragging:
            scroll_y += velocity
            velocity *= friction
            if abs(velocity) < 0.5:
                velocity = 0
        scroll_y = max(0, min(scroll_y, max_scroll))

        # Draw rules text
        y_offset_start = 150 # Starting Y position for the first line
        current_y = y_offset_start - scroll_y
        for line in wrapped_lines:
            rendered = FONT.render(line, True, WHITE)
            x = SCREEN_WIDTH // 2 - rendered.get_width() // 2
            screen.blit(rendered, (x, current_y))
            current_y += rendered.get_height() + line_spacing
            if current_y > SCREEN_HEIGHT + 50: # Stop drawing off-screen
                break
            if current_y < y_offset_start - 50: # Don't draw too far above screen
                continue

        # Draw back button
        if back_button.draw(screen):
            showing_rules = False

        # Scrollbar (right edge)
        if content_height > display_area_height: # Only show if content overflows
            bar_height = int(display_area_height * (display_area_height / content_height))
            bar_y = int(display_area_height * scroll_y / content_height) + (SCREEN_HEIGHT - display_area_height) // 2
            pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH - 20, bar_y, 10, bar_height), border_radius=5)

        # Hint text (top-center) for scrolling
        if max_scroll > 0 and abs(scroll_y - max_scroll) > 10 and abs(scroll_y) > 10:
             hint_text = FONT.render("⬆ Swipe/Scroll to read ⬇", True, (150, 150, 150))
             screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, 120))


        # Apply fade-in effect
        if fade_alpha > 0:
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
            fade_alpha = max(0, fade_alpha - 15)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    dragging = True
                    drag_start_y = event.pos[1]
                    velocity = 0 # Stop inertia when dragging starts
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dy = event.pos[1] - drag_start_y
                    scroll_y -= dy # Move content opposite to mouse drag
                    velocity = -dy # Set velocity for inertia
                    drag_start_y = event.pos[1]
            elif event.type == pygame.MOUSEWHEEL:
                scroll_y -= event.y * 20 # Adjust scroll speed for mouse wheel
                velocity = -event.y * 20 # Apply to velocity too

            # Touch input handling for mobile/touchscreens
            elif event.type == pygame.FINGERDOWN:
                dragging = True
                drag_start_y = event.y * SCREEN_HEIGHT # event.y is normalized [0,1]
                velocity = 0
            elif event.type == pygame.FINGERMOTION:
                if dragging:
                    dy = event.dy * SCREEN_HEIGHT # event.dy is normalized
                    scroll_y -= dy
                    velocity = -dy
            elif event.type == pygame.FINGERUP:
                dragging = False

        clock.tick(60)


# --- Top-right utility buttons ---
BUTTON_SCALE = 0.5 # Shrink large PNGs
BUTTON_PAD = 20 # Distance from screen edges / between buttons

# Quit button (top-right corner)
quit_button = Button(
    quit_button_img,
    (
        SCREEN_WIDTH - int(quit_button_img.get_width() * BUTTON_SCALE / 2) - BUTTON_PAD,
        BUTTON_PAD + int(quit_button_img.get_height() * BUTTON_SCALE / 2)
    ),
    scale=BUTTON_SCALE
)

# Restart button (directly under quit)
restart_button = Button(
    restart_button_img,
    (
        quit_button.rect.centerx,
        quit_button.rect.bottom + BUTTON_PAD + int(restart_button_img.get_height() * BUTTON_SCALE / 2)
    ),
    scale=BUTTON_SCALE
)

def handle_system_buttons(game_active=True):
    """
    Draws and handles interaction for system-level buttons (Restart, Quit).
    Returns True if a restart is requested, False otherwise.
    Quits the game directly if the quit button is pressed.
    """
    if game_active:
        if restart_button.draw(screen):
            return True # Restart requested
    if quit_button.draw(screen):
        pygame.quit()
        sys.exit()
    return False

def select_mode():
    """
    Displays the game mode selection screen (AI vs. Multiplayer)
    and music selection dropdown.
    Returns True for AI mode, False for Multiplayer mode, or None to quit.
    """
    global current_music, selected_track_name

    # Start playing selected music if not already playing
    if current_music is None or not pygame.mixer.get_busy():
        current_music = MUSIC_TRACKS[selected_track_name]
        current_music.play(-1) # Loop indefinitely

    ai_button = Button(ai_button_img, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
    multi_button = Button(multi_button_img, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    info_button = Button(info_btn_img, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200), scale=0.7)
    dropdown = Dropdown(selected_track_name, list(MUSIC_TRACKS.keys()), (SCREEN_WIDTH // 2 - 100, 100))

    while True:
        screen.fill(WHITE) # Background for mode selection

        # Draw dropdown first so it's on top
        selected_from_dropdown = dropdown.draw(screen)
        if selected_from_dropdown and selected_from_dropdown != selected_track_name:
            selected_track_name = selected_from_dropdown
            if current_music:
                current_music.stop()
            current_music = MUSIC_TRACKS[selected_track_name]
            current_music.play(-1)

        # Handle system buttons (Quit) on this screen
        if handle_system_buttons(game_active=False): # No restart option here
            return None # User chose to quit

        # Draw mode selection buttons.
        # Only process button clicks if dropdown is not blocking input.
        mouse_pos = pygame.mouse.get_pos()
        if not dropdown.blocks_input_at(mouse_pos):
            if ai_button.draw(screen):
                return True # AI Mode selected
            if multi_button.draw(screen):
                return False # Multiplayer Mode selected
            if info_button.draw(screen):
                show_rules_screen() # Show rules, then return to mode selection

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None # User closed window
            elif event.type == pygame.USEREVENT + 1: # Custom event for music ending (not strictly needed with -1 loop)
                if current_music:
                    current_music.play(-1) # Ensure music loops

            # Crucial: If dropdown is open and user clicks outside of it, close it
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if dropdown.is_open() and not dropdown.blocks_input_at(event.pos):
                    dropdown.open = False # Close dropdown if clicked outside

            # Any other click or event handling for the mode screen can go here,
            # but ensure it respects dropdown.blocks_input_at if necessary.


def main():
    """Main game loop function."""
    moves, boards_won, turn, current_board, global_winner = reset_game()
    ai_mode = False # Default

    show_loading_screen()
    mode_selection_result = select_mode()

    if mode_selection_result is None: # User quit from mode selection
        pygame.quit()
        sys.exit()
    else:
        ai_mode = mode_selection_result
        show_loading_screen() # Show loading screen again before starting game

    running = True
    while running:
        screen.fill(WHITE)
        screen.blit(board_bg, (OFFSET_X - 30, OFFSET_Y - 30)) # Background image
        draw_grid()
        draw_moves(moves, boards_won, current_board)

        # Display turn or winner message
        if global_winner == "":
            turn_color = RED if turn == "X" else BLUE
            turn_text = FONT.render(f"{turn}'s Turn", True, turn_color)
            screen.blit(turn_text, (OFFSET_X + BOARD_WIDTH // 2 - turn_text.get_width() // 2, OFFSET_Y + BOARD_HEIGHT + 10))
        elif global_winner == "Tie":
            tie_text = WINNER_FONT.render("It's a Tie!", True, DARK_GRAY)
            tie_rect = tie_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(tie_text, tie_rect)
            # Add buttons to restart or quit
            if show_game_over_screen("It's a Tie!") == "restart":
                moves, boards_won, turn, current_board, global_winner = reset_game()
                ai_mode = select_mode()
                if ai_mode is None:
                    running = False
                    break
                show_loading_screen()
                continue
            else: # Quit
                running = False
                break
        else: # A winner exists
            winner_message = f"{global_winner} Wins!"
            winner_color = RED if global_winner == "X" else BLUE
            win_text = WINNER_FONT.render(winner_message, True, winner_color)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(win_text, win_rect)
            # Add buttons to restart or quit
            if show_game_over_screen(winner_message) == "restart":
                moves, boards_won, turn, current_board, global_winner = reset_game()
                ai_mode = select_mode()
                if ai_mode is None:
                    running = False
                    break
                show_loading_screen()
                continue
            else: # Quit
                running = False
                break

        # Handle system buttons (Restart, Quit) during active gameplay
        if handle_system_buttons(game_active=True):
            show_loading_screen()
            moves, boards_won, turn, current_board, global_winner = reset_game()
            ai_mode = select_mode()
            if ai_mode is None: # User quit from mode selection after restart
                running = False
                break
            show_loading_screen()
            continue # Restart the game loop with new settings


        pygame.display.flip() # Update the full screen

        # AI's Turn Logic
        if ai_mode and turn == "O" and global_winner == "":
            pygame.time.delay(700) # Give AI a slight delay to "think" (UX improvement)
            board_index, cell_index = ai_move(moves, boards_won, current_board)

            if board_index is not None and cell_index is not None:
                click_sound.play() # Play click sound for AI move
                moves[board_index][cell_index] = turn

                if check_win(moves[board_index]):
                    boards_won[board_index] = turn

                next_board = cell_index
                # Determine the next current_board based on the AI's move
                if boards_won[next_board] != "" or is_board_full(moves[next_board]):
                    current_board = None # If next board is won or full, AI can play anywhere
                else:
                    current_board = next_board

                global_winner = game_winner(boards_won)
                # Check for global tie after AI's move
                if global_winner == "" and all(b != "" or is_board_full(moves[i]) for i, b in enumerate(boards_won)):
                    global_winner = "Tie"

                turn = "X" # Switch to player's turn
            else:
                # This state means AI couldn't find a move, likely global tie or game over.
                # The game_winner check above should handle this, but this is a fallback.
                print("AI could not make a move. Game might be over or in an unexpected state.")
                # Force a global tie if no moves left
                if global_winner == "":
                    global_winner = "Tie"


        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # Handle player's click (human turn only, and if game not over)
            if event.type == pygame.MOUSEBUTTONDOWN and global_winner == "" and (not ai_mode or turn == "X"):
                pos = pygame.mouse.get_pos()
                board_index, cell_index = get_board_and_cell(pos)

                if board_index is not None and cell_index is not None:
                    # Check if the move is valid according to Ultimate Tic Tac Toe rules
                    # (i.e., in the correct board or any board if previous was won/full, and cell is empty, and board not won)
                    is_valid_move = (current_board is None or current_board == board_index) and \
                                    moves[board_index][cell_index] == "" and \
                                    boards_won[board_index] == ""

                    if is_valid_move:
                        click_sound.play()

                        moves[board_index][cell_index] = turn
                        if check_win(moves[board_index]):
                            boards_won[board_index] = turn

                        next_board = cell_index # Player sends opponent to board matching cell_index
                        # Determine the next playable board
                        if boards_won[next_board] != "" or is_board_full(moves[next_board]):
                            current_board = None # If target board is won or full, next player can play anywhere
                        else:
                            current_board = next_board # Next player must play in 'next_board'

                        global_winner = game_winner(boards_won)
                        # Check for global tie after player's move
                        if global_winner == "" and all(b != "" or is_board_full(moves[i]) for i, b in enumerate(boards_won)):
                            global_winner = "Tie"

                        turn = "O" if turn == "X" else "X" # Switch turns


        # Draw hover effect for player's turn
        if global_winner == "" and (not ai_mode or turn == "X"):
            mouse_pos = pygame.mouse.get_pos()
            # Convert mouse position to global cell coordinates (0-8 for x, 0-8 for y)
            global_cell_x = (mouse_pos[0] - OFFSET_X) // CELL_SIZE
            global_cell_y = (mouse_pos[1] - OFFSET_Y) // CELL_SIZE

            # Ensure mouse is within the bounds of the entire 9x9 grid
            if 0 <= global_cell_x < 9 and 0 <= global_cell_y < 9:
                draw_hover(moves, boards_won, current_board, (global_cell_x, global_cell_y), turn)

        clock.tick(60) # Cap frame rate

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()