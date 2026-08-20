"""
  _____ _   _          _____ _     _           _       _             
 |_   _| | | |        /  ___| |   (_)         | |     | |            
   | | | |_| |__   _  \ `--.| |    _ _ __   __| | __ _| |_ ___  ___  
   | | | __| '_ \ | |  `--. \ |   | | '_ \ / _` |/ _` | __/ _ \/ __| 
   | | | |_| | | || | /\__/ / |___| | | | | (_| | (_| | ||  __/\__ \ 
   \_/  \__|_| |_(_)| \____/\____/_|_| |_|\__,_|\__,_|\__\___||___/ 
                                                                    
                  Premium Edition with Smart AI & Modern UI
"""

import pygame
import sys
import numpy as np
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 900
GAME_SIZE = 600
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = GAME_SIZE // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3

# Colors - Premium Neon Theme
BG_COLOR = (15, 15, 35)
GAME_BG = (25, 25, 55)
LINE_COLOR = (100, 100, 150)
LINE_GLOW = (150, 150, 200)
CIRCLE_COLOR = (0, 255, 200)  # Cyan neon
CIRCLE_GLOW = (0, 200, 150)
CROSS_COLOR = (255, 50, 100)  # Pink neon
CROSS_GLOW = (200, 0, 80)
TEXT_COLOR = (255, 255, 255)
GOLD = (255, 215, 0)
BUTTON_COLOR = (60, 60, 120)
BUTTON_HOVER = (100, 100, 180)
BUTTON_ACTIVE = (150, 150, 220)
PANEL_COLOR = (30, 30, 60, 240)

# Sound frequencies
SOUND_CLICK = 800
SOUND_WIN = 600
SOUND_DRAW = 400
SOUND_MOVE = 1000


class GameState(Enum):
    MENU = 1
    MODE_SELECT = 2
    SETTINGS = 3
    PLAYING = 4
    GAME_OVER = 5


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class GameMode(Enum):
    PVP = 1
    PVAI = 2


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(30, 60)
        self.max_life = self.life
        self.size = random.randint(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        size = int(self.size * (self.life / self.max_life))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)


class Button:
    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.clicked = False
        self.animation_offset = 0

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered:
            self.animation_offset = min(self.animation_offset + 2, 5)
        else:
            self.animation_offset = max(self.animation_offset - 2, 0)

    def draw(self, screen):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        rect = self.rect.copy()
        rect.y -= self.animation_offset
        
        # Glow effect
        if self.hovered:
            glow_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*BUTTON_HOVER[:3], 100), glow_surf.get_rect(), border_radius=15)
            screen.blit(glow_surf, (rect.x - 10, rect.y - 10))
        
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, TEXT_COLOR, rect, 2, border_radius=10)
        
        text_render = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_render.get_rect(center=rect.center)
        text_rect.y -= self.animation_offset
        screen.blit(text_render, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class TicTacToe:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tic Tac Toe - Premium Edition")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        self.reset_game()
        self.state = GameState.MENU
        self.game_mode = GameMode.PVAI
        self.difficulty = Difficulty.MEDIUM
        self.sound_enabled = True
        self.scores = {'player1': 0, 'player2': 0, 'draws': 0}
        self.particles = []
        self.winning_line = None
        self.winning_line_progress = 0
        self.current_player = 1
        self.ai_thinking = False
        self.ai_move_time = 0
        
        # Create buttons
        self.create_menu_buttons()
        self.create_mode_buttons()
        self.create_settings_buttons()
        self.create_game_over_buttons()

    def reset_game(self):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.game_over = False
        self.current_player = 1
        self.winning_line = None
        self.winning_line_progress = 0
        self.particles = []

    def create_menu_buttons(self):
        self.btn_play = Button(WIDTH//2 - 150, 300, 300, 60, "Play Game")
        self.btn_settings = Button(WIDTH//2 - 150, 400, 300, 60, "Settings")
        self.btn_quit = Button(WIDTH//2 - 150, 500, 300, 60, "Quit")

    def create_mode_buttons(self):
        self.btn_pvp = Button(WIDTH//2 - 150, 300, 300, 60, "Player vs Player")
        self.btn_pvai = Button(WIDTH//2 - 150, 400, 300, 60, "Player vs AI")
        self.btn_back_mode = Button(WIDTH//2 - 100, 700, 200, 50, "Back", 36)

    def create_settings_buttons(self):
        self.btn_easy = Button(WIDTH//2 - 150, 250, 300, 50, "Easy")
        self.btn_medium = Button(WIDTH//2 - 150, 330, 300, 50, "Medium")
        self.btn_hard = Button(WIDTH//2 - 150, 410, 300, 50, "Hard (Unbeatable)")
        self.btn_sound = Button(WIDTH//2 - 150, 500, 300, 50, "Sound: ON")
        self.btn_back_settings = Button(WIDTH//2 - 100, 700, 200, 50, "Back", 36)

    def create_game_over_buttons(self):
        self.btn_retry = Button(WIDTH//2 - 150, 500, 300, 60, "Play Again")
        self.btn_menu = Button(WIDTH//2 - 150, 580, 300, 60, "Main Menu")

    def play_sound(self, frequency, duration=100, volume=0.3):
        if not self.sound_enabled:
            return
        try:
            sample_rate = 44100
            n_samples = int(sample_rate * duration / 1000)
            buf = bytes([int(128 + volume * 127 * math.sin(2 * math.pi * frequency * t / sample_rate)) 
                        for t in range(n_samples)])
            sound = pygame.mixer.Sound(buffer=buf)
            sound.play()
        except:
            pass

    def spawn_particles(self, x, y, color, count=30):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def draw_gradient_bg(self):
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            color = tuple(int(BG_COLOR[i] * (1 - ratio) + (BG_COLOR[i] + 20) * ratio) for i in range(3))
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

    def draw_game_panel(self):
        panel_rect = pygame.Rect(WIDTH//2 - GAME_SIZE//2 - 20, 150, GAME_SIZE + 40, GAME_SIZE + 40)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, BUTTON_HOVER, panel_rect, 3, border_radius=20)

    def draw_board(self):
        offset_x = WIDTH//2 - GAME_SIZE//2
        offset_y = 170
        
        # Draw grid lines with glow
        for i in range(1, BOARD_ROWS):
            # Horizontal
            start_pos = (offset_x, offset_y + i * SQUARE_SIZE)
            end_pos = (offset_x + GAME_SIZE, offset_y + i * SQUARE_SIZE)
            pygame.draw.line(self.screen, LINE_COLOR, start_pos, end_pos, 8)
            pygame.draw.line(self.screen, LINE_GLOW, start_pos, end_pos, 3)
            
            # Vertical
            start_pos = (offset_x + i * SQUARE_SIZE, offset_y)
            end_pos = (offset_x + i * SQUARE_SIZE, offset_y + GAME_SIZE)
            pygame.draw.line(self.screen, LINE_COLOR, start_pos, end_pos, 8)
            pygame.draw.line(self.screen, LINE_GLOW, start_pos, end_pos, 3)

    def draw_figures(self):
        offset_x = WIDTH//2 - GAME_SIZE//2
        offset_y = 170
        
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                center_x = offset_x + col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = offset_y + row * SQUARE_SIZE + SQUARE_SIZE // 2
                
                if self.board[row][col] == 1:
                    # Draw circle with glow
                    glow_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*CIRCLE_GLOW, 100), (SQUARE_SIZE//2, SQUARE_SIZE//2), CIRCLE_RADIUS + 10)
                    self.screen.blit(glow_surf, (center_x - SQUARE_SIZE//2, center_y - SQUARE_SIZE//2))
                    pygame.draw.circle(self.screen, CIRCLE_COLOR, (center_x, center_y), CIRCLE_RADIUS, 8)
                    
                elif self.board[row][col] == 2:
                    # Draw cross with glow
                    space = SQUARE_SIZE // 4
                    glow_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    pygame.draw.line(glow_surf, (*CROSS_GLOW, 100), 
                                   (space, SQUARE_SIZE - space), (SQUARE_SIZE - space, space), 15)
                    pygame.draw.line(glow_surf, (*CROSS_GLOW, 100), 
                                   (space, space), (SQUARE_SIZE - space, SQUARE_SIZE - space), 15)
                    self.screen.blit(glow_surf, (center_x - SQUARE_SIZE//2, center_y - SQUARE_SIZE//2))
                    
                    pygame.draw.line(self.screen, CROSS_COLOR, 
                                   (center_x - SQUARE_SIZE//2 + space, center_y + SQUARE_SIZE//2 - space),
                                   (center_x + SQUARE_SIZE//2 - space, center_y - SQUARE_SIZE//2 + space), 12)
                    pygame.draw.line(self.screen, CROSS_COLOR, 
                                   (center_x - SQUARE_SIZE//2 + space, center_y - SQUARE_SIZE//2 + space),
                                   (center_x + SQUARE_SIZE//2 - space, center_y + SQUARE_SIZE//2 - space), 12)

    def check_win(self, player):
        # Check rows
        for row in range(BOARD_ROWS):
            if np.all(self.board[row, :] == player):
                self.winning_line = ('row', row)
                return True
        
        # Check columns
        for col in range(BOARD_COLS):
            if np.all(self.board[:, col] == player):
                self.winning_line = ('col', col)
                return True
        
        # Check diagonals
        if np.all(np.diag(self.board) == player):
            self.winning_line = ('diag', 'main')
            return True
        
        if np.all(np.diag(np.fliplr(self.board)) == player):
            self.winning_line = ('diag', 'anti')
            return True
        
        return False

    def draw_winning_line(self):
        if not self.winning_line:
            return
        
        offset_x = WIDTH//2 - GAME_SIZE//2
        offset_y = 170
        
        self.winning_line_progress = min(self.winning_line_progress + 5, 100)
        progress = self.winning_line_progress / 100
        
        color = CIRCLE_COLOR if self.current_player == 1 else CROSS_COLOR
        
        if self.winning_line[0] == 'row':
            row = self.winning_line[1]
            y = offset_y + row * SQUARE_SIZE + SQUARE_SIZE // 2
            start_x = offset_x
            end_x = offset_x + int(GAME_SIZE * progress)
            pygame.draw.line(self.screen, color, (start_x, y), (end_x, y), 10)
            
        elif self.winning_line[0] == 'col':
            col = self.winning_line[1]
            x = offset_x + col * SQUARE_SIZE + SQUARE_SIZE // 2
            start_y = offset_y
            end_y = offset_y + int(GAME_SIZE * progress)
            pygame.draw.line(self.screen, color, (x, start_y), (x, end_y), 10)
            
        elif self.winning_line[0] == 'diag':
            if self.winning_line[1] == 'main':
                start_pos = (offset_x + 20, offset_y + 20)
                end_pos = (offset_x + int((GAME_SIZE - 40) * progress) + 20, 
                          offset_y + int((GAME_SIZE - 40) * progress) + 20)
            else:
                start_pos = (offset_x + GAME_SIZE - 20, offset_y + 20)
                end_pos = (offset_x + GAME_SIZE - 20 - int((GAME_SIZE - 40) * progress), 
                          offset_y + 20 + int((GAME_SIZE - 40) * progress))
            pygame.draw.line(self.screen, color, start_pos, end_pos, 10)

    def minimax(self, board, depth, is_maximizing):
        # Check terminal states
        if np.all(board[0, :] == 2) or np.all(board[1, :] == 2) or np.all(board[2, :] == 2) or \
           np.all(board[:, 0] == 2) or np.all(board[:, 1] == 2) or np.all(board[:, 2] == 2) or \
           np.all(np.diag(board) == 2) or np.all(np.diag(np.fliplr(board)) == 2):
            return 10 - depth
        
        if np.all(board[0, :] == 1) or np.all(board[1, :] == 1) or np.all(board[2, :] == 1) or \
           np.all(board[:, 0] == 1) or np.all(board[:, 1] == 1) or np.all(board[:, 2] == 1) or \
           np.all(np.diag(board) == 1) or np.all(np.diag(np.fliplr(board)) == 1):
            return depth - 10
        
        if not np.any(board == 0):
            return 0
        
        if is_maximizing:
            best_score = -float('inf')
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    if board[row][col] == 0:
                        board[row][col] = 2
                        score = self.minimax(board, depth + 1, False)
                        board[row][col] = 0
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    if board[row][col] == 0:
                        board[row][col] = 1
                        score = self.minimax(board, depth + 1, True)
                        board[row][col] = 0
                        best_score = min(score, best_score)
            return best_score

    def get_ai_move(self):
        empty_squares = [(row, col) for row in range(BOARD_ROWS) 
                        for col in range(BOARD_COLS) if self.board[row][col] == 0]
        
        if not empty_squares:
            return None
        
        if self.difficulty == Difficulty.EASY:
            return random.choice(empty_squares)
        
        elif self.difficulty == Difficulty.MEDIUM:
            # 50% chance of best move, 50% random
            if random.random() < 0.5:
                return random.choice(empty_squares)
        
        # Hard difficulty - use minimax
        best_score = -float('inf')
        best_move = None
        
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board[row][col] == 0:
                    self.board[row][col] = 2
                    score = self.minimax(self.board, 0, False)
                    self.board[row][col] = 0
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)
        
        return best_move if best_move else random.choice(empty_squares)

    def handle_click(self, pos):
        if self.game_over or self.ai_thinking:
            return
        
        offset_x = WIDTH//2 - GAME_SIZE//2
        offset_y = 170
        
        if offset_x <= pos[0] <= offset_x + GAME_SIZE and \
           offset_y <= pos[1] <= offset_y + GAME_SIZE:
            
            col = (pos[0] - offset_x) // SQUARE_SIZE
            row = (pos[1] - offset_y) // SQUARE_SIZE
            
            if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
                if self.board[row][col] == 0 and self.current_player == 1:
                    self.make_move(row, col)

    def make_move(self, row, col):
        self.board[row][col] = self.current_player
        self.play_sound(SOUND_MOVE if not self.game_over else SOUND_CLICK)
        
        if self.check_win(self.current_player):
            self.game_over = True
            self.spawn_particles(WIDTH//2, HEIGHT//2, 
                               CIRCLE_COLOR if self.current_player == 1 else CROSS_COLOR, 50)
            self.play_sound(SOUND_WIN, 300, 0.5)
            
            if self.game_mode == GameMode.PVAI:
                if self.current_player == 1:
                    self.scores['player1'] += 1
                else:
                    self.scores['player2'] += 1
            else:
                if self.current_player == 1:
                    self.scores['player1'] += 1
                else:
                    self.scores['player2'] += 1
                    
        elif not np.any(self.board == 0):
            self.game_over = True
            self.scores['draws'] += 1
            self.play_sound(SOUND_DRAW, 200, 0.4)
        else:
            self.current_player = 3 - self.current_player  # Switch player (1->2, 2->1)
            
            if self.game_mode == GameMode.PVAI and self.current_player == 2 and not self.game_over:
                self.ai_thinking = True
                self.ai_move_time = pygame.time.get_ticks()

    def draw_scores(self):
        mode_text = "PvP" if self.game_mode == GameMode.PVP else "PvAI"
        score_text = f"{mode_text} | P1: {self.scores['player1']} | Draws: {self.scores['draws']} | P2/AI: {self.scores['player2']}"
        score_render = self.font_small.render(score_text, True, GOLD)
        score_rect = score_render.get_rect(center=(WIDTH//2, 120))
        self.screen.blit(score_render, score_rect)

    def draw_current_turn(self):
        if self.game_over:
            return
        
        turn_text = f"Player {'X' if self.current_player == 1 else 'O'}'s Turn"
        color = CIRCLE_COLOR if self.current_player == 1 else CROSS_COLOR
        turn_render = self.font_medium.render(turn_text, True, color)
        turn_rect = turn_render.get_rect(center=(WIDTH//2, 80))
        self.screen.blit(turn_render, turn_rect)

    def run(self):
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.state == GameState.MENU:
                    self.btn_play.update(mouse_pos)
                    self.btn_settings.update(mouse_pos)
                    self.btn_quit.update(mouse_pos)
                    
                    if self.btn_play.is_clicked(event):
                        self.state = GameState.MODE_SELECT
                        self.play_sound(SOUND_CLICK)
                    elif self.btn_settings.is_clicked(event):
                        self.state = GameState.SETTINGS
                        self.play_sound(SOUND_CLICK)
                    elif self.btn_quit.is_clicked(event):
                        running = False
                
                elif self.state == GameState.MODE_SELECT:
                    self.btn_pvp.update(mouse_pos)
                    self.btn_pvai.update(mouse_pos)
                    self.btn_back_mode.update(mouse_pos)
                    
                    if self.btn_pvp.is_clicked(event):
                        self.game_mode = GameMode.PVP
                        self.reset_game()
                        self.state = GameState.PLAYING
                        self.play_sound(SOUND_CLICK)
                    elif self.btn_pvai.is_clicked(event):
                        self.game_mode = GameMode.PVAI
                        self.reset_game()
                        self.state = GameState.PLAYING
                        self.play_sound(SOUND_CLICK)
                    elif self.btn_back_mode.is_clicked(event):
                        self.state = GameState.MENU
                        self.play_sound(SOUND_CLICK)
                
                elif self.state == GameState.SETTINGS:
                    self.btn_easy.update(mouse_pos)
                    self.btn_medium.update(mouse_pos)
                    self.btn_hard.update(mouse_pos)
                    self.btn_sound.update(mouse_pos)
                    self.btn_back_settings.update(mouse_pos)
                    
                    if self.btn_easy.is_clicked(event):
                        self.difficulty = Difficulty.EASY
                        self.play_sound(SOUND_CLICK)
                    elif self.btn_medium.is_clicked(event):
                        self.difficulty = Difficulty.MEDIUM
                        self.play_sound(SOUND_CLICK)
                    elif self.btn_hard.is_clicked(event):
                        self.difficulty = Difficulty.HARD
                        self.play_sound(SOUND_CLICK)
                    elif self.btn_sound.is_clicked(event):
                        self.sound_enabled = not self.sound_enabled
                        self.btn_sound.text = f"Sound: {'ON' if self.sound_enabled else 'OFF'}"
                        self.play_sound(SOUND_CLICK if self.sound_enabled else 200)
                    elif self.btn_back_settings.is_clicked(event):
                        self.state = GameState.MENU
                        self.play_sound(SOUND_CLICK)
                
                elif self.state == GameState.PLAYING:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.handle_click(event.pos)
                    
                    # AI move handling
                    if self.ai_thinking and self.game_mode == GameMode.PVAI:
                        if pygame.time.get_ticks() - self.ai_move_time >= 800:
                            ai_move = self.get_ai_move()
                            if ai_move:
                                self.make_move(ai_move[0], ai_move[1])
                            self.ai_thinking = False
                
                elif self.state == GameState.GAME_OVER:
                    self.btn_retry.update(mouse_pos)
                    self.btn_menu.update(mouse_pos)
                    
                    if self.btn_retry.is_clicked(event):
                        self.reset_game()
                        self.state = GameState.PLAYING
                        self.play_sound(SOUND_CLICK)
                    elif self.btn_menu.is_clicked(event):
                        self.state = GameState.MENU
                        self.play_sound(SOUND_CLICK)
            
            # Update particles
            self.particles = [p for p in self.particles if p.update()]
            
            # Draw everything
            self.draw_gradient_bg()
            
            if self.state == GameState.MENU:
                title = self.font_large.render("TIC TAC TOE", True, TEXT_COLOR)
                subtitle = self.font_medium.render("Premium Edition", True, GOLD)
                self.screen.blit(title, title.get_rect(center=(WIDTH//2, 180)))
                self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH//2, 250)))
                self.btn_play.draw(self.screen)
                self.btn_settings.draw(self.screen)
                self.btn_quit.draw(self.screen)
                
            elif self.state == GameState.MODE_SELECT:
                title = self.font_large.render("Select Mode", True, TEXT_COLOR)
                self.screen.blit(title, title.get_rect(center=(WIDTH//2, 150)))
                self.btn_pvp.draw(self.screen)
                self.btn_pvai.draw(self.screen)
                self.btn_back_mode.draw(self.screen)
                
            elif self.state == GameState.SETTINGS:
                title = self.font_large.render("Settings", True, TEXT_COLOR)
                diff_title = self.font_medium.render(f"Difficulty: {self.difficulty.name}", True, GOLD)
                self.screen.blit(title, title.get_rect(center=(WIDTH//2, 120)))
                self.screen.blit(diff_title, diff_title.get_rect(center=(WIDTH//2, 200)))
                self.btn_easy.draw(self.screen)
                self.btn_medium.draw(self.screen)
                self.btn_hard.draw(self.screen)
                self.btn_sound.draw(self.screen)
                self.btn_back_settings.draw(self.screen)
                
            elif self.state == GameState.PLAYING or self.state == GameState.GAME_OVER:
                self.draw_game_panel()
                self.draw_board()
                self.draw_figures()
                self.draw_winning_line()
                self.draw_scores()
                self.draw_current_turn()
                
                if self.game_over:
                    # Semi-transparent overlay
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 180))
                    self.screen.blit(overlay, (0, 0))
                    
                    if self.winning_line:
                        winner = "Player X" if self.current_player == 1 else ("Player O" if self.game_mode == GameMode.PVP else "AI")
                        msg = f"{winner} Wins!"
                        color = CIRCLE_COLOR if self.current_player == 1 else CROSS_COLOR
                    else:
                        msg = "It's a Draw!"
                        color = GOLD
                    
                    msg_render = self.font_large.render(msg, True, color)
                    self.screen.blit(msg_render, msg_render.get_rect(center=(WIDTH//2, 350)))
                    self.btn_retry.draw(self.screen)
                    self.btn_menu.draw(self.screen)
            
            # Draw particles
            for particle in self.particles:
                particle.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = TicTacToe()
    game.run()
