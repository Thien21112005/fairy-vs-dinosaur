import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui.game_over import GameOverScreen
from fairy_vs_dinosaur.ui.widgets import draw_gradient_rect, draw_soft_rect, get_font

SOLVE_OPTIONS = ["BFS", "DFS", "UCS", "ASTAR", "GREEDY", "HILL CLIMBING", "BEAM"]


class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont('monospace', 20, bold=True)
        lives_icon_raw = pygame.image.load(asset("images/fairy/blue/tile003.png")).convert_alpha()
        self.lives_icon = pygame.transform.smoothscale(lives_icon_raw, (self.game.pac_w, self.game.pac_h))
        self.hint_hover = False
        self.ghost_hover = [False] * 4  # Blinky, Pinky, Inky, Clyde
        self.show_blinky = True
        self.show_pinky = True
        self.show_inky = True
        self.show_clyde = True

        self.game_over = GameOverScreen(game)
        self.ghost_colors = [
            (255, 0, 0),  # Blinky
            (255, 184, 255),  # Pinky
            (0, 255, 255),  # Inky
            (255, 165, 0)  # Clyde
        ]
        self.ghost_labels = ["B", "P", "I", "C"]

        button_y = self.game.height - self.game.bottom_offset + 10
        button_width = 40
        spacing = 10
        hint_width = 80
        solve_width = 120
        total_width = 4 * button_width + 3 * spacing + spacing * 2 + hint_width + solve_width
        current_x = self.game.width // 2 - total_width // 2

        self.ghost_rects = []
        for _ in range(4):
            self.ghost_rects.append(pygame.Rect(current_x, button_y, button_width, 25))
            current_x += button_width + spacing

        self.hint_rect = pygame.Rect(current_x, button_y, hint_width, 25)
        current_x += hint_width + spacing
        self.solve_rect = pygame.Rect(current_x, button_y, solve_width, 25)

        self.solve_hover = False
        self.solve_menu_visible = False
        self.solve_options = SOLVE_OPTIONS
        self.solve_option_hover = [False] * len(self.solve_options)
        self.solve_option_rects = []
        self.selected_solve = None

    def visible_ghost_flags(self):
        return [self.show_blinky, self.show_pinky, self.show_inky, self.show_clyde]

    def draw_header(self):
        screen = self.game.screen
        white = (255, 255, 255)

        screen.blit(self.font.render(get_translation("1up"), True, white), (self.game.width // 4 - 60, 10))
        screen.blit(self.font.render(f"{self.game.score:06d}", True, white), (self.game.width // 4 - 60, 30))

        text_high = self.font.render(get_translation("high_score"), True, white)
        screen.blit(text_high, (self.game.width // 2 - text_high.get_width() // 2, 10))
        high_score_text = self.font.render(f"{self.game.high_score:06d}", True, white)
        screen.blit(high_score_text, (self.game.width // 2 - high_score_text.get_width() // 2, 30))

        minutes = int(self.game.play_time // 60000)
        seconds = int((self.game.play_time // 1000) % 60)
        milliseconds = int(self.game.play_time % 1000)
        screen.blit(self.font.render(get_translation("time"), True, white), (3 * self.game.width // 4 - 30, 10))
        screen.blit(self.font.render(f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}", True, white),
                    (3 * self.game.width // 4 - 50, 30))

        self.game.pause_menu.draw_pause_button(screen)

    def draw_ready(self):
        if self.game.show_ready:
            ready_text = self.font.render(get_translation("ready"), True, (255, 255, 0))
            text_w, text_h = ready_text.get_size()
            ready_y = 18 * self.game.num1_r + self.game.y_offset + self.game.num1_r // 2 - text_h // 2
            self.game.screen.blit(ready_text, (self.game.width // 2 - text_w // 2, ready_y))

    def draw_lives(self):
        base_y = self.game.height - self.game.bottom_offset - 10
        for i in range(self.game.lives - 1):
            self.game.screen.blit(self.lives_icon, (20 + i * (self.game.pac_w + 5), base_y + 15))

    def draw_hint_button(self):
        screen = self.game.screen
        glow_rect = self.hint_rect.inflate(4, 4)
        if self.game.show_hint:
            start, end, border, text_color = (255, 255, 150), (255, 165, 0), (255, 255, 100), (0, 0, 0)
            draw_gradient_rect(screen, self.hint_rect, start, end, border_radius=10)
            draw_soft_rect(screen, glow_rect, (255, 255, 150, 128), border_radius=12)
        else:
            text_color = (255, 255, 255)
            if self.hint_hover:
                start, end, border = (120, 200, 255), (70, 130, 180), (150, 200, 255)
                draw_soft_rect(screen, glow_rect, (150, 150, 200, 128), border_radius=12)
            else:
                start, end, border = (70, 130, 180), (50, 50, 80), (100, 100, 160)
            draw_gradient_rect(screen, self.hint_rect, start, end, border_radius=10)

        pygame.draw.rect(screen, border, self.hint_rect, width=3, border_radius=10)
        hint_text = self.font.render("HINT", True, text_color)
        screen.blit(hint_text, hint_text.get_rect(center=self.hint_rect.center))

    def draw_ghost_toggle_buttons(self):
        screen = self.game.screen
        for i, rect in enumerate(self.ghost_rects):
            color = self.ghost_colors[i]
            if self.visible_ghost_flags()[i]:
                start = tuple(min(255, c + 50) for c in color)
                end = color
                border = tuple(min(255, c + 100) for c in color)
                text_color = (0, 0, 0) if sum(color) > 400 else (255, 255, 255)
            else:
                start, end, border, text_color = (150, 150, 150), (100, 100, 100), (200, 200, 200), (255, 255, 255)

            if self.ghost_hover[i]:
                draw_soft_rect(screen, rect.inflate(6, 6), (255, 255, 255, 100), border_radius=10)
                start = tuple(min(255, c + 30) for c in start)
                end = tuple(min(255, c + 30) for c in end)

            draw_gradient_rect(screen, rect, start, end, border_radius=8)
            pygame.draw.rect(screen, border, rect, width=2, border_radius=8)
            label_text = self.font.render(self.ghost_labels[i], True, text_color)
            screen.blit(label_text, label_text.get_rect(center=rect.center))

    def _fit_font(self, text, max_width, start_size, min_size):
        """Font mặc định nếu chữ vừa, nếu không thì giảm cỡ dần tới khi vừa."""
        if self.font.size(text)[0] <= max_width:
            return self.font
        size = start_size
        font = get_font('monospace', size, bold=True)
        while size > min_size and font.size(text)[0] > max_width:
            size -= 1
            font = get_font('monospace', size, bold=True)
        return font

    def draw_solve_button(self):
        screen = self.game.screen
        if self.solve_menu_visible:
            start, end, border, text_color = (255, 230, 100), (255, 150, 0), (255, 255, 150), (0, 0, 0)
            draw_soft_rect(screen, self.solve_rect.inflate(6, 6), (255, 220, 50, 180), border_radius=12)
        else:
            text_color = (255, 255, 255)
            if self.solve_hover:
                start, end, border = (140, 210, 255), (80, 140, 200), (170, 220, 255)
                draw_soft_rect(screen, self.solve_rect.inflate(4, 4), (100, 180, 255, 150), border_radius=12)
            else:
                start, end, border = (80, 140, 200), (40, 60, 100), (120, 160, 220)

        draw_gradient_rect(screen, self.solve_rect, start, end, border_radius=10)
        pygame.draw.rect(screen, border, self.solve_rect, width=3, border_radius=10)

        label = self.selected_solve.upper() if self.selected_solve else "SOLVE"
        font = self._fit_font(label, self.solve_rect.width - 15, 16, 10)
        solve_text = font.render(label, True, text_color)
        screen.blit(solve_text, solve_text.get_rect(center=self.solve_rect.center))

        if self.solve_menu_visible:
            self._draw_solve_dropdown()

    def _draw_solve_dropdown(self):
        screen = self.game.screen
        total_height = len(self.solve_options) * 32

        shadow_surface = pygame.Surface((154, total_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 80), pygame.Rect(0, 0, 154, total_height + 4), border_radius=10)
        screen.blit(shadow_surface, (self.solve_rect.x - 2, self.solve_rect.y - total_height - 2))

        dropdown = pygame.Surface((150, total_height), pygame.SRCALPHA)
        draw_gradient_rect(dropdown, pygame.Rect(0, 0, 150, total_height), (60, 80, 120, 240), (30, 40, 70, 240),
                           border_color=(100, 140, 200, 255), border_width=2, border_radius=8)
        screen.blit(dropdown, (self.solve_rect.x, self.solve_rect.y - total_height))

        self.solve_option_rects = []
        for i, option in enumerate(self.solve_options):
            opt_rect = pygame.Rect(self.solve_rect.x, self.solve_rect.y - (i + 1) * 32, 150, 30)
            self.solve_option_rects.append(opt_rect)

            option_color = (100, 160, 220, 200) if self.solve_option_hover[i] else (80, 120, 180, 200)
            draw_soft_rect(screen, opt_rect, option_color, border_radius=6)

            font = self._fit_font(option, opt_rect.width - 15, 14, 8)
            opt_text = font.render(option, True, (255, 255, 255))
            screen.blit(opt_text, opt_text.get_rect(center=opt_rect.center))

    def update_hover(self, mouse_pos):
        hover_sound = self.game.sound_manager.button_hover_sound

        prev_hint_hover = self.hint_hover
        prev_solve_hover = self.solve_hover
        prev_ghost_hover = self.ghost_hover.copy()
        prev_option_hover = self.solve_option_hover.copy()

        self.hint_hover = self.hint_rect.collidepoint(mouse_pos)
        self.solve_hover = self.solve_rect.collidepoint(mouse_pos)
        self.ghost_hover = [rect.collidepoint(mouse_pos) for rect in self.ghost_rects]
        self.solve_option_hover = [False] * len(self.solve_options)
        if self.solve_menu_visible:
            self.solve_option_hover = [rect.collidepoint(mouse_pos) for rect in self.solve_option_rects]

        if (self.hint_hover and not prev_hint_hover) or (self.solve_hover and not prev_solve_hover):
            hover_sound.play()
        for i in range(4):
            if self.ghost_hover[i] and not prev_ghost_hover[i]:
                hover_sound.play()
        if self.solve_menu_visible:
            for i in range(len(self.solve_options)):
                if self.solve_option_hover[i] and not prev_option_hover[i]:
                    hover_sound.play()
