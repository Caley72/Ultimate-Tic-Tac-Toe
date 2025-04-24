import pygame
import sys

pygame.init()

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

def draw_grid():
    # Draw thick lines for main grid
    for i in range(1, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (0, i * HEIGHT // GRID_SIZE), (WIDTH, i * HEIGHT // GRID_SIZE), 5)
        pygame.draw.line(screen, BLACK, (i * WIDTH // GRID_SIZE, 0), (i * WIDTH // GRID_SIZE, HEIGHT), 5)
    # Draw thin lines for cells
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

    # Highlight active board
    if current_board is not None and boards_won[current_board] == "":
        bx, by = current_board % 3, current_board // 3
        rect = pygame.Rect(bx * 3 * CELL_SIZE, by * 3 * CELL_SIZE, 3 * CELL_SIZE, 3 * CELL_SIZE)
        pygame.draw.rect(screen, BLUE, rect, 4)

    # Show won boards
    for i in range(9):
        if boards_won[i]:
            bx, by = i % 3, i // 3
            center = (bx * 3 * CELL_SIZE + CELL_SIZE * 1.5, by * 3 * CELL_SIZE + CELL_SIZE * 1.5)
            color = GREEN if boards_won[i] == "X" else RED
            pygame.draw.circle(screen, color, center, CELL_SIZE)

def check_win(board):
    lines = [
        [0,1,2], [3,4,5], [6,7,8],  # rows
        [0,3,6], [1,4,7], [2,5,8],  # cols
        [0,4,8], [2,4,6]            # diagonals
    ]
    for a,b,c in lines:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return ""

def game_winner(boards_won):
    return check_win(boards_won)

def main():
    moves = [["" for _ in range(9)] for _ in range(9)]
    boards_won = ["" for _ in range(9)]
    turn = "X"
    current_board = None
    winner = ""

    running = True
    while running:
        screen.fill(WHITE)
        draw_grid()
        draw_moves(moves, boards_won, current_board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN and winner == "":
                pos = pygame.mouse.get_pos()
                board_index, cell_index = get_board_and_cell(pos)

                if (current_board is None or current_board == board_index) and \
                   moves[board_index][cell_index] == "" and \
                   boards_won[board_index] == "":

                    moves[board_index][cell_index] = turn
                    if check_win(moves[board_index]):
                        boards_won[board_index] = turn

                    next_board = cell_index
                    if boards_won[next_board] or all(m != "" for m in moves[next_board]):
                        current_board = None  # any board
                    else:
                        current_board = next_board

                    winner = game_winner(boards_won)
                    turn = "O" if turn == "X" else "X"

        if winner:
            text = FONT.render(f"{winner} wins!", True, BLACK)
            screen.blit(text, (WIDTH // 2 - 70, HEIGHT - 40))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
