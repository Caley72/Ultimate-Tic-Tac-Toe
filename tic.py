import pygame
import sys
import random
import time
import math


pygame.init()
pygame.mixer.init()

#Sound Variables
click_sound = pygame.mixer.Sound("assets/sound/click.mp3")
win_sound = pygame.mixer.Sound("assets/sound/win.mp3")


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

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Tic Tac Toe")

clock = pygame.time.Clock()

def draw_grid():
    for i in range(1, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (0, i * HEIGHT // GRID_SIZE), (WIDTH, i * HEIGHT // GRID_SIZE), 5)
        pygame.draw.line(screen, BLACK, (i * WIDTH // GRID_SIZE, 0), (i * WIDTH // GRID_SIZE, HEIGHT), 5)
    for i in range(1, GRID_SIZE * GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 1)
        pygame.draw.line(screen, GRAY, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), 1)

def get_board_and_cell(pos):
    x, y = pos
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
                px = (bx * 3 + cx) * CELL_SIZE + CELL_SIZE // 2
                py = (by * 3 + cy) * CELL_SIZE + CELL_SIZE // 2
                text = FONT.render(val, True, RED if val == "X" else BLUE)
                text_rect = text.get_rect(center=(px, py))
                screen.blit(text, text_rect)

    if current_board is not None and boards_won[current_board] == "":
        bx, by = current_board % 3, current_board // 3
        rect = pygame.Rect(bx * 3 * CELL_SIZE, by * 3 * CELL_SIZE, 3 * CELL_SIZE, 3 * CELL_SIZE)
        pygame.draw.rect(screen, BLUE, rect, 4)

    for i in range(9):
        if boards_won[i]:
            bx, by = i % 3, i // 3
            center = (bx * 3 * CELL_SIZE + CELL_SIZE * 1.5, by * 3 * CELL_SIZE + CELL_SIZE * 1.5)
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
        rect = pygame.Rect(global_x * CELL_SIZE, global_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (0, 255, 0), rect, 3)  # Solid green outline

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

def ai_move(moves, boards_won, current_board, difficulty="normal"):
    def random_move():
        valid_boards = [i for i in range(9) if boards_won[i] == "" and any(cell == "" for cell in moves[i])]
        if current_board is not None and current_board in valid_boards:
            board = current_board
        else:
            board = random.choice(valid_boards)
        empty_cells = [i for i in range(9) if moves[board][i] == ""]
        return board, random.choice(empty_cells)

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
        best_move = (None, None)

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
                            best_move = (board, cell)
                        alpha = max(alpha, score)
                    else:
                        if score < best_score:
                            best_score = score
                            best_move = (board, cell)
                        beta = min(beta, score)

                    if beta <= alpha:
                        break

        return best_score, best_move[0], best_move[1]

    if difficulty == "easy":
        return random_move()
    elif difficulty == "normal":
        _, b, c = minimax(moves, boards_won, current_board, depth=2, alpha=float("-inf"), beta=float("inf"), is_max=True, ai="O", player="X")
        return b, c
    elif difficulty == "hard":
        _, b, c = minimax(moves, boards_won, current_board, depth=4, alpha=float("-inf"), beta=float("inf"), is_max=True, ai="O", player="X")
        return b, c

def reset_game():
    return [["" for _ in range(9)] for _ in range(9)], ["" for _ in range(9)], "X", None, "", False

def main():
    hover_cell = [0, 0]  # global coordinates (0-8, 0-8)
    moves, boards_won, turn, current_board, winner, ai_mode = reset_game()

    selecting_mode = True
    while selecting_mode:
        screen.fill(WHITE)
        title = FONT.render("Press A for AI Mode or M for Multiplayer", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    ai_mode = True
                    selecting_mode = False
                elif event.key == pygame.K_m:
                    ai_mode = False
                    selecting_mode = False

    difficulty = "normal"
    if ai_mode:
        selecting_difficulty = True
        while selecting_difficulty:
            screen.fill(WHITE)
            prompt = FONT.render("Press 1 (Easy), 2 (Normal), 3 (Hard)", True, BLACK)
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        difficulty = "easy"
                        selecting_difficulty = False
                    elif event.key == pygame.K_2:
                        difficulty = "normal"
                        selecting_difficulty = False
                    elif event.key == pygame.K_3:
                        difficulty = "hard"
                        selecting_difficulty = False

    running = True
    while running:
        screen.fill(WHITE)
        draw_grid()
        draw_moves(moves, boards_won, current_board)
        turn_color = RED if turn == "X" else BLUE
        turn_text = FONT.render(f"{turn}'s Turn", True, turn_color)
        screen.blit(turn_text, (WIDTH // 2 - turn_text.get_width() // 2, HEIGHT - 30))

        if winner:
            text = FONT.render(f"{winner} wins!", True, BLACK)
            screen.blit(text, (WIDTH // 2 - 70, HEIGHT - 40))
            win_sound.play()

        pygame.display.flip()

        if ai_mode and turn == "O" and not winner:
            pygame.time.delay(500)
            board_index, cell_index = ai_move(moves, boards_won, current_board, difficulty)

        else:
            board_index, cell_index = None, None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                moves, boards_won, turn, current_board, winner, ai_mode = reset_game()
                selecting_mode = True
                while selecting_mode:
                    screen.fill(WHITE)
                    title = FONT.render("Press A for AI Mode or M for Multiplayer", True, BLACK)
                    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 20))
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_a:
                                ai_mode = True
                                selecting_mode = False
                            elif event.key == pygame.K_m:
                                ai_mode = False
                                selecting_mode = False

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
                if check_win(moves[board_index]):
                    boards_won[board_index] = turn
                winner = game_winner(boards_won)
                if winner:
                    win_sound.play()
                turn = "O" if turn == "X" else "X"

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
