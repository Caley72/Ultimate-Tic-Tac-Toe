import pygame
import sys
import random
import time

pygame.init()
pygame.mixer.init()

# Load and scale the icon
logo = pygame.image.load('assets/images/logo.png')
logo = pygame.transform.scale(logo, (50, 50))
pygame.display.set_icon(logo)

# Sound Variables
click_sound = pygame.mixer.Sound("assets/sound/click.mp3")
win_sound = pygame.mixer.Sound("assets/sound/win.mp3")
first = pygame.mixer.Sound("assets/sound/experimental-abstract-tech-glitch-179496.mp3")
second = pygame.mixer.Sound("assets/sound/cinematic-dark-trailer-130489.mp3")
third = pygame.mixer.Sound("assets/sound/coding-night-112186.mp3")
forth = pygame.mixer.Sound("assets/sound/many-moons-of-saturn-146147.mp3")

MUSIC_TRACKS = {
    "Abstract Glitch": first,
    "Cinematic Dark": second,
    "Coding Night": third,
    "Saturn Moons": forth
}

dropdown_open = False
selected_track_name = "Abstract Glitch"
current_music = None

# Images
ai_button_img = pygame.image.load("assets/images/ai-mode.png")
multi_button_img = pygame.image.load("assets/images/multiplayer.png")
restart_button_img = pygame.image.load("assets/images/restart.png")
quit_button_img = pygame.image.load("assets/images/quit.png")
info_btn_img = pygame.image.load("assets/images/info.png")
sound_btn_img = pygame.image.load("assets/images/sound.png")
back_button_img = pygame.image.load("assets/images/back.png")

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 3
CELL_SIZE = WIDTH // (GRID_SIZE * GRID_SIZE)
LINE_WIDTH = 3
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 100, 255)
GREEN = (0, 200, 0)
RED = (255, 50, 50)

FONT = pygame.font.SysFont(None, 40)

screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Ultimate Tic Tac Toe")

OFFSET_X = (SCREEN_WIDTH - WIDTH) // 2
OFFSET_Y = (SCREEN_HEIGHT - HEIGHT) // 2

clock = pygame.time.Clock()
#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 100, 255)
GREEN = (0, 200, 0)
RED = (255, 50, 50)
DARK_GRAY = (50, 50, 50)  # ← Add this

LOADING_TIPS = [
    "Tip: Focus the center, control the grid.",
    "Hint: Corners aren't just edges — they’re strategy.",
    "Tip: Outthink, don’t just outplay.",
    "Hint: Use small wins to control the big board.",
    "Tip: The last move can set the next trap.",
    "💡 Tip: Winning one board isn't enough. Think ahead.",
    "🤖 Did you know? The AI thinks 6 moves deep.",
    "🎯 Strategy: Send your opponent to weak boards.",
    "🌀 Rule: You must play in the board matching the cell you last picked.",
    "🔥 Pro Tip: Force a draw on a board to open up options.",
    "👁 Watch closely — your move decides theirs.",
    "⚔️ Rule: 3 local wins = global domination.",
    "⏳ Each move shapes the future. Plan wisely."
]

def draw_grid():
    for i in range(1, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (OFFSET_X, OFFSET_Y + i * HEIGHT // GRID_SIZE), (OFFSET_X + WIDTH, OFFSET_Y + i * HEIGHT // GRID_SIZE), 5)
        pygame.draw.line(screen, BLACK, (OFFSET_X + i * WIDTH // GRID_SIZE, OFFSET_Y), (OFFSET_X + i * WIDTH // GRID_SIZE, OFFSET_Y + HEIGHT), 5)
    for i in range(1, GRID_SIZE * GRID_SIZE):
        pygame.draw.line(screen, GRAY, (OFFSET_X, OFFSET_Y + i * CELL_SIZE), (OFFSET_X + WIDTH, OFFSET_Y + i * CELL_SIZE), 1)
        pygame.draw.line(screen, GRAY, (OFFSET_X + i * CELL_SIZE, OFFSET_Y), (OFFSET_X + i * CELL_SIZE, OFFSET_Y + HEIGHT), 1)

def get_board_and_cell(pos):
    x, y = pos
    x -= OFFSET_X
    y -= OFFSET_Y
    if x < 0 or y < 0 or x >= WIDTH or y >= HEIGHT:
        return None, None
    board_x = x // (CELL_SIZE * GRID_SIZE)
    board_y = y // (CELL_SIZE * GRID_SIZE)
    cell_x = (x % (CELL_SIZE * GRID_SIZE)) // CELL_SIZE
    cell_y = (y % (CELL_SIZE * GRID_SIZE)) // CELL_SIZE
    return board_x + board_y * GRID_SIZE, cell_x + cell_y * GRID_SIZE

def draw_moves(moves, boards_won, current_board):
    for board in range(9):
        for cell in range(9):
            val = moves[board][cell]
            if val:
                bx, by = board % 3, board // 3
                cx, cy = cell % 3, cell // 3
                px = OFFSET_X + (bx * 3 + cx) * CELL_SIZE + CELL_SIZE // 2
                py = OFFSET_Y + (by * 3 + cy) * CELL_SIZE + CELL_SIZE // 2
                text = FONT.render(val, True, RED if val == "X" else BLUE)
                text_rect = text.get_rect(center=(px, py))
                screen.blit(text, text_rect)

    if current_board is not None and boards_won[current_board] == "":
        bx, by = current_board % 3, current_board // 3
        rect = pygame.Rect(OFFSET_X + bx * 3 * CELL_SIZE, OFFSET_Y + by * 3 * CELL_SIZE, 3 * CELL_SIZE, 3 * CELL_SIZE)
        pygame.draw.rect(screen, BLUE, rect, 4)

    for i in range(9):
        if boards_won[i]:
            bx, by = i % 3, i // 3
            center = (OFFSET_X + bx * 3 * CELL_SIZE + CELL_SIZE * 1.5, OFFSET_Y + by * 3 * CELL_SIZE + CELL_SIZE * 1.5)
            color = GREEN if boards_won[i] == "X" else RED
            pygame.draw.circle(screen, color, center, CELL_SIZE)

def draw_hover(moves, boards_won, current_board, hover_cell, turn):
    global_x, global_y = hover_cell
    board_x, cell_x = global_x // 3, global_x % 3
    board_y, cell_y = global_y // 3, global_y % 3
    board_index = board_x + board_y * 3
    cell_index = cell_x + cell_y * 3

    if (current_board is None or current_board == board_index) and \
       moves[board_index][cell_index] == "" and \
       boards_won[board_index] == "":
        rect = pygame.Rect(OFFSET_X + global_x * CELL_SIZE, OFFSET_Y + global_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (0, 255, 0), rect, 3)# Solid green outline

class Button:
    def __init__(self, image, pos, scale=1.0):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect(center=pos)
        self.clicked = False

    def draw(self, surface):
        action = False
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            # Optional: hover effect (scale up)
            hover_image = pygame.transform.scale(self.image, (int(self.rect.width * 1.05), int(self.rect.height * 1.05)))
            hover_rect = hover_image.get_rect(center=self.rect.center)
            surface.blit(hover_image, hover_rect)
        else:
            surface.blit(self.image, self.rect)

        # Click detection
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(mouse_pos) and not self.clicked:
            self.clicked = True
            click_sound.play()
            action = True
        elif not pygame.mouse.get_pressed()[0]:
            self.clicked = False
        return action

class Dropdown:
    def __init__(self, title, options, pos, width=200, height=40):
        self.title = title
        self.options = options
        self.pos = pos
        self.width = width
        self.height = height
        self.open = False
        self.hover_index = -1
        self.selected = title
        self.font = pygame.font.SysFont(None, 32)
        self.disabled_zone = []

    def is_open(self):
        return self.open

    def blocks_input_at(self, pos):
        return any(rect.collidepoint(pos) for rect in self.disabled_zone)

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        # --- Draw main dropdown box
        rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)

        # Hover effect
        is_hover = rect.collidepoint(mouse)
        color = (220, 220, 220) if is_hover else (200, 200, 200)

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        text = self.font.render(self.selected, True, (0, 0, 0))
        screen.blit(text, (self.pos[0] + 10, self.pos[1] + 8))

        # Handle dropdown click toggle
        if click and is_hover:
            self.open = not self.open
            pygame.time.wait(150)

        # --- Draw dropdown options
        self.disabled_zone = [rect]
        if self.open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.pos[0], self.pos[1] + (i + 1) * self.height, self.width, self.height)
                is_option_hover = option_rect.collidepoint(mouse)

                # Background hover color
                bg_color = (180, 180, 180) if is_option_hover else (220, 220, 220)
                pygame.draw.rect(screen, bg_color, option_rect)
                pygame.draw.rect(screen, (0, 0, 0), option_rect, 1)

                opt_text = self.font.render(option, True, (0, 0, 0))
                screen.blit(opt_text, (option_rect.x + 10, option_rect.y + 8))

                self.disabled_zone.append(option_rect)

                if click and is_option_hover:
                    self.selected = option
                    self.open = False
                    pygame.time.wait(150)

                    # Music switch
                    global selected_track_name, current_music
                    selected_track_name = self.selected
                    if current_music:
                        current_music.stop()
                    current_music = MUSIC_TRACKS[self.selected]
                    current_music.play(-1)

    def is_open(self):
        return self.open

    def blocks_input_at(self, pos):
        return any(rect.collidepoint(pos) for rect in self.disabled_zone)

def check_win(board):
    lines = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    for a,b,c in lines:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return ""

def game_winner(boards_won):
    return check_win(boards_won)

def ai_move(moves, boards_won, current_board):
    def evaluate(boards_won, ai, player):
        result = check_win(boards_won)
        if result == ai:
            return 10
        elif result == player:
            return -10
        return 0

    def minimax(moves, boards_won, current_board, depth, alpha, beta, is_max, ai, player):
        result = check_win(boards_won)
        if depth == 0 or result:
            return evaluate(boards_won, ai, player), None, None

        valid_boards = [i for i in range(9) if boards_won[i] == "" and any(c == "" for c in moves[i])]
        if current_board is not None and current_board in valid_boards:
            boards_to_check = [current_board]
        else:
            boards_to_check = valid_boards

        best_score = float('-inf') if is_max else float('inf')
        best_moves = []

        for board in boards_to_check:
            for cell in range(9):
                if moves[board][cell] == "":
                    moves[board][cell] = ai if is_max else player
                    original_win = boards_won[board]
                    if check_win(moves[board]):
                        boards_won[board] = ai if is_max else player

                    next_board = cell
                    if boards_won[next_board] or all(m != "" for m in moves[next_board]):
                        new_current = None
                    else:
                        new_current = next_board

                    score, _, _ = minimax(moves, boards_won, new_current, depth - 1, alpha, beta, not is_max, ai, player)

                    moves[board][cell] = ""
                    boards_won[board] = original_win

                    if is_max:
                        if score > best_score:
                            best_score = score
                            best_moves = [(board, cell)]
                        elif score == best_score:
                            best_moves.append((board, cell))
                        alpha = max(alpha, score)
                    else:
                        if score < best_score:
                            best_score = score
                            best_moves = [(board, cell)]
                        elif score == best_score:
                            best_moves.append((board, cell))
                        beta = min(beta, score)

                    if beta <= alpha:
                        break
        if best_moves:
            best_move = random.choice(best_moves)
        else:
            best_move = (None, None)

        return best_score, best_move[0], best_move[1]
    _, b, c = minimax(moves, boards_won, current_board, depth=6, alpha=float("-inf"), beta=float("inf"), is_max=True, ai="O", player="X")
    return b, c
def reset_game():
    return [["" for _ in range(9)] for _ in range(9)], ["" for _ in range(9)], "X", None, "", False 
def show_loading_screen(duration=3.5):  # duration in seconds
    start_time = time.time()
    tip = random.choice(LOADING_TIPS)  # ← Select a random tip each time
    bar_width = 400
    bar_height = 30
    bar_x = SCREEN_WIDTH // 2 - bar_width // 2
    bar_y = SCREEN_HEIGHT // 2 + 60
    load_color = (100, 200, 100)
    border_color = WHITE

    while time.time() - start_time < duration:
        screen.fill(DARK_GRAY)
        # Tip text
        tip_rendered = FONT.render(tip, True, WHITE)
        screen.blit(tip_rendered, (SCREEN_WIDTH // 2 - tip_rendered.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        # Loading text
        text = BIG_FONT.render("Loading...", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        # Calculate progress
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1)
        current_width = int(bar_width * progress)
        # Draw bar border
        pygame.draw.rect(screen, border_color, (bar_x, bar_y, bar_width, bar_height), 2)
        # Draw filled bar
        pygame.draw.rect(screen, load_color, (bar_x, bar_y, current_width, bar_height))

        pygame.display.flip()
        clock.tick(60)

def blocks_input_at(self, pos):
    return any(rect.collidepoint(pos) for rect in self.disabled_zone)

def select_mode():
    global current_music
    if current_music:
        current_music.play(-1)
    else:
        current_music = MUSIC_TRACKS[selected_track_name]
        current_music.play(-1)

    ai_button = Button(ai_button_img, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
    multi_button = Button(multi_button_img, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    info_button = Button(info_btn_img,(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200), scale=0.7)
    dropdown = Dropdown("Abstract Glitch", list(MUSIC_TRACKS.keys()), (SCREEN_WIDTH // 2 - 100, 100))

    while True:
        screen.fill(WHITE)
        dropdown.draw(screen)
        mouse_pos = pygame.mouse.get_pos()
        # Only allow button clicks if dropdown isn't in the way
        if ai_button.draw(screen) and not dropdown.blocks_input_at(mouse_pos):
            return True
        if multi_button.draw(screen):
            return False
        if info_button.draw(screen):
            show_rules_screen()
        if handle_system_buttons():
            return None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.USEREVENT + 1:
                if current_music:
                    current_music.play(-1)

            # Optional: if user clicks and dropdown blocks, skip all clicks
            if event.type == pygame.MOUSEBUTTONDOWN and dropdown.blocks_input_at(event.pos):
                continue  # Ignore this click

        pygame.display.update()
        clock.tick(60)

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

def show_rules_screen():
    try:
        with open("rules.txt", "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    except Exception as e:
        raw_lines = [f"Error loading rules: {str(e)}"]

    # Word-wrap and center
    margin_x = 50
    line_spacing = 10
    wrapped_lines = []
    for line in raw_lines:
        wrapped = wrap_text(line.strip(), FONT, SCREEN_WIDTH - 2 * margin_x)
        wrapped_lines.extend(wrapped)

    # Prepare scroll
    scroll_y = 0
    velocity = 0
    friction = 0.9
    dragging = False
    drag_start_y = 0
    content_height = len(wrapped_lines) * (FONT.get_height() + line_spacing)
    max_scroll = max(0, content_height - (SCREEN_HEIGHT - 200))  # leave room for top buttons

    # Back button
    back_button = Button(back_button_img, (SCREEN_WIDTH // 2, 80), scale=0.5)

    # Fade-in
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))
    fade_alpha = 255

    showing = True
    while showing:
        screen.fill(BLACK)

        # Handle scroll inertia
        if not dragging:
            scroll_y += velocity
            velocity *= friction
            if abs(velocity) < 0.5:
                velocity = 0
        scroll_y = max(0, min(scroll_y, max_scroll))

        # Draw text
        y = 150 - scroll_y
        for line in wrapped_lines:
            rendered = FONT.render(line.strip(), True, WHITE)
            x = SCREEN_WIDTH // 2 - rendered.get_width() // 2
            screen.blit(rendered, (x, y))
            y += rendered.get_height() + line_spacing

        # Draw back button
        if back_button.draw(screen):
            showing = False

        # Scrollbar (right edge)
        if content_height > SCREEN_HEIGHT - 200:
            bar_height = int((SCREEN_HEIGHT - 200) * (SCREEN_HEIGHT - 200) / content_height)
            bar_y = int((SCREEN_HEIGHT - 200) * scroll_y / content_height) + 150
            pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH - 10, bar_y, 5, bar_height), border_radius=3)

        # Hint text (top-center)
        if scroll_y < 20:
            hint_text = FONT.render("⬆️ Swipe up to read more ⬇️", True, (150, 150, 150))
            screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, 120))

        # Fade-in
        if fade_alpha > 0:
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
            fade_alpha -= 15

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    drag_start_y = event.pos[1]
                    velocity = 0

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dy = event.pos[1] - drag_start_y
                    scroll_y -= dy
                    velocity = -dy
                    drag_start_y = event.pos[1]

            elif event.type == pygame.FINGERDOWN:
                dragging = True
                drag_start_y = event.y * SCREEN_HEIGHT
                velocity = 0

            elif event.type == pygame.FINGERMOTION:
                if dragging:
                    dy = event.dy * SCREEN_HEIGHT
                    scroll_y -= dy
                    velocity = -dy

            elif event.type == pygame.FINGERUP:
                dragging = False
# ── Top-right utility buttons ──────────────────────────────────────────
BUTTON_SCALE  = 0.5          # shrink large PNGs
BUTTON_PAD    = 20           # distance from screen edges / between buttons

# Quit button (top-right corner)
quit_button = Button(
    quit_button_img,
    (
        SCREEN_WIDTH - int(quit_button_img.get_width()  * BUTTON_SCALE / 2) - BUTTON_PAD,
        BUTTON_PAD + int(quit_button_img.get_height()   * BUTTON_SCALE / 2)
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
# ───────────────────────────────────────────────────────────────────────
FONT = pygame.font.SysFont(None, 40)
BIG_FONT = pygame.font.SysFont(None, 80)  # Add this line
def handle_system_buttons():
    """Draw Quit / Restart and return True if a restart was clicked."""
    # Draw Quit first so it appears above Restart in z-order
    if quit_button.draw(screen):
        pygame.quit()
        sys.exit()

    if restart_button.draw(screen):
        return True        # signal caller to reset game

    return False

def main():
    moves, boards_won, turn, current_board, winner, _ = reset_game()
    show_loading_screen()
    ai_mode = select_mode()
    show_loading_screen()
    ai_mode = select_mode()
    if ai_mode is None:
        pygame.quit()
        sys.exit()

    # We skip difficulty since it's always hardcoded now
    difficulty = None

    running = True
    while running:
        screen.fill(WHITE)
        # System buttons (Quit / Restart)
        if restart_button.draw(screen):
            show_loading_screen()
            moves, boards_won, turn, current_board, winner, ai_mode = reset_game()
            ai_mode = select_mode()
            if ai_mode is None:
                pygame.quit()
                sys.exit()
            show_loading_screen()

            difficulty = None
            continue
        # Draw the game state
        draw_grid()
        draw_moves(moves, boards_won, current_board)

        if winner == "":
            turn_color = RED if turn == "X" else BLUE
            turn_text = FONT.render(f"{turn}'s Turn", True, turn_color)
            screen.blit(turn_text, (WIDTH // 2 - turn_text.get_width() // 2, HEIGHT - 30))
        elif winner == "Tie":
            tie_text = FONT.render("It's a Tie!", True, DARK_GRAY)
            screen.blit(tie_text, (WIDTH // 2 - tie_text.get_width() // 2, HEIGHT - 30))
        else:
            win_text = FONT.render(f"{winner} Wins!", True, BLACK)
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT - 30))


        pygame.display.flip()

        if ai_mode and turn == "O" and not winner:
            pygame.time.delay(500)
            board_index, cell_index = ai_move(moves, boards_won, current_board)

        else:
            board_index, cell_index = None, None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                moves, boards_won, turn, current_board, winner, ai_mode = reset_game()
                ai_mode = select_mode()

            if event.type == pygame.MOUSEBUTTONDOWN and winner == "" and (not ai_mode or turn == "X"):
                pos = pygame.mouse.get_pos()
                board_index, cell_index = get_board_and_cell(pos)

        if board_index is not None and cell_index is not None and winner == "":
            if (current_board is None or current_board == board_index) and \
               moves[board_index][cell_index] == "" and \
               boards_won[board_index] == "":
                click_sound.play()

                moves[board_index][cell_index] = turn
                if check_win(moves[board_index]):
                    boards_won[board_index] = turn

                next_board = cell_index
                if boards_won[next_board] or all(m != "" for m in moves[next_board]):
                    current_board = None
                else:
                    current_board = next_board
                winner = game_winner(boards_won)
                if winner:
                    win_sound.play()
                elif all(board != "" or all(cell != "" for cell in moves[i]) for i, board in enumerate(boards_won)):
                    winner = "Tie, all"
                turn = "O" if turn == "X" else "X"
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()