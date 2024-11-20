"""
==========      ===========   =========     =====      ====     =========     ===========             ======            ===========
====  ====      ===========   =========     ====    ====        =========     ===========            =========          ====   ====
====  ====      ====   ====   ====          ====  ====           ====             ===               ====   ====         ====   ====
==========      ====   ====   ====          ========               ====           ===              ====     ====        ===========
====  ====      ====   ====   ====          =======                 ====          ===             ===============       ===========
====   ====     ====   ====   ====          ====  ====                ====        ===            =================      ====    ====
====    ====    ===========   =========     ====    ====        ==========        ===           ====           ====     ====     ====
====     ====   ===========   =========     ====      ====      ==========        ===          ====             ====    ====      ====
"""  
import pygame
import sys
import numpy as np
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
WIN_LINE_WIDTH = 15
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (23, 145, 135)
BUTTON_HOVER_COLOR = (20, 120, 115)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")

# Board
board = np.zeros((BOARD_ROWS, BOARD_COLS))


def draw_lines():
    pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT), LINE_WIDTH)


def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:
                pygame.draw.circle(screen, CIRCLE_COLOR, (int(col * SQUARE_SIZE + SQUARE_SIZE // 2), int(row * SQUARE_SIZE + SQUARE_SIZE // 2)), CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 2:
                pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)


def mark_square(row, col, player):
    board[row][col] = player


def available_square(row, col):
    return board[row][col] == 0


def is_board_full():
    return not np.any(board == 0)


def check_win(player):
    for col in range(BOARD_COLS):
        if board[0][col] == player and board[1][col] == player and board[2][col] == player:
            draw_vertical_winning_line(col, player)
            return True
    for row in range(BOARD_ROWS):
        if board[row][0] == player and board[row][1] == player and board[row][2] == player:
            draw_horizontal_winning_line(row, player)
            return True
    if board[2][0] == player and board[1][1] == player and board[0][2] == player:
        draw_asc_diagonal(player)
        return True
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        draw_desc_diagonal(player)
        return True
    return False


def draw_vertical_winning_line(col, player):
    posX = col * SQUARE_SIZE + SQUARE_SIZE // 2
    color = CIRCLE_COLOR if player == 1 else CROSS_COLOR
    pygame.draw.line(screen, color, (posX, 15), (posX, HEIGHT - 15), WIN_LINE_WIDTH)


def draw_horizontal_winning_line(row, player):
    posY = row * SQUARE_SIZE + SQUARE_SIZE // 2
    color = CIRCLE_COLOR if player == 1 else CROSS_COLOR
    pygame.draw.line(screen, color, (15, posY), (WIDTH - 15, posY), WIN_LINE_WIDTH)


def draw_asc_diagonal(player):
    color = CIRCLE_COLOR if player == 1 else CROSS_COLOR
    pygame.draw.line(screen, color, (15, HEIGHT - 15), (WIDTH - 15, 15), WIN_LINE_WIDTH)


def draw_desc_diagonal(player):
    color = CIRCLE_COLOR if player == 1 else CROSS_COLOR
    pygame.draw.line(screen, color, (15, 15), (WIDTH - 15, HEIGHT - 15), WIN_LINE_WIDTH)


def display_game_over_menu(message):
    screen.fill(BG_COLOR)
    font = pygame.font.Font(None, 54)
    text = font.render(message, True, TEXT_COLOR)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(text, text_rect)

    retry_button = create_button("Retry", (WIDTH // 2, HEIGHT // 2))
    close_button = create_button("Close", (WIDTH // 2, 2 * HEIGHT // 3))

    pygame.display.update()
    menu = True
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.collidepoint(event.pos):
                    menu = False
                    restart()
                    return
                elif close_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def display_start_menu():
    screen.fill(BG_COLOR)
    font = pygame.font.Font(None, 74)
    title = font.render("Tic Tac Toe", True, TEXT_COLOR)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title, title_rect)

    start_button = create_button("Start Game", (WIDTH // 2, HEIGHT // 2))
    quit_button = create_button("Quit", (WIDTH // 2, 2 * HEIGHT // 3))

    pygame.display.update()
    menu = True
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    menu = False
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def create_button(text, position):
    font = pygame.font.Font(None, 54)
    text_render = font.render(text, True, TEXT_COLOR)
    text_rect = text_render.get_rect(center=position)

    button_rect = text_rect.inflate(20, 20)
    button_color = BUTTON_COLOR if not button_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_HOVER_COLOR

    pygame.draw.rect(screen, button_color, button_rect)
    screen.blit(text_render, text_rect)

    return button_rect


def restart():
    global player, game_over
    screen.fill(BG_COLOR)
    draw_lines()
    board.fill(0)
    player = 1
    game_over = False


def ai_move():
    empty_squares = [(row, col) for row in range(BOARD_ROWS) for col in range(BOARD_COLS) if available_square(row, col)]
    return random.choice(empty_squares)


# Main loop
display_start_menu()
screen.fill(BG_COLOR)
draw_lines()
player = 1
game_over = False

# New variables for AI delay
ai_move_time = None  # Tracks when AI should move
ai_delay = 1000  # Delay in milliseconds (1 second)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over and player == 1:
            mouseX, mouseY = event.pos
            clicked_row, clicked_col = int(mouseY // SQUARE_SIZE), int(mouseX // SQUARE_SIZE)
            if available_square(clicked_row, clicked_col):
                mark_square(clicked_row, clicked_col, player)
                draw_figures()
                if check_win(player):
                    game_over = True
                    display_game_over_menu("Player wins!")
                elif is_board_full():
                    game_over = True
                    display_game_over_menu("It's a draw!")
                else:
                    player = 2  # Switch to AI
                    ai_move_time = pygame.time.get_ticks()  # Start the AI move delay timer

    # AI move logic with delay
    if player == 2 and not game_over:
        if ai_move_time is not None and pygame.time.get_ticks() - ai_move_time >= ai_delay:
            row, col = ai_move()
            mark_square(row, col, player)
            draw_figures()
            if check_win(player):
                game_over = True
                display_game_over_menu("AI wins!")
            elif is_board_full():
                game_over = True
                display_game_over_menu("It's a draw!")
            else:
                player = 1  # Switch back to the player
            ai_move_time = None  # Reset the timer

    pygame.display.update()