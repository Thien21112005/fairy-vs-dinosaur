import pygame

from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui import theme
from fairy_vs_dinosaur.ui.theme import label_font, strong_font
from fairy_vs_dinosaur.ui.widgets import draw_divider, draw_menu_button, draw_text, draw_title

MAX_DIM_ALPHA = 225


class GameOverScreen:
    def __init__(self, game):
        self.game = game
        self.visible = False
        self.selected = 0  # 0: Restart, 1: Main Menu
        self.hover = [False, False]
        self.fade_alpha = 0
        self.fade_speed = 3
        self.dim = self._build_dim()

    def _build_dim(self):
        """Màn tối dần về phía đỏ than phía dưới, gợi lại ngọn lửa của khủng long."""
        width, height = self.game.width, self.game.height
        dim = pygame.Surface((width, height))
        for y in range(height):
            ratio = y / height
            color = [int(theme.NIGHT[i] + (theme.BLOOD_DARK[i] - theme.NIGHT[i]) * ratio * 0.6) for i in range(3)]
            pygame.draw.line(dim, color, (0, y), (width, y))
        return dim

    def _option_rect(self, index):
        return pygame.Rect(self.game.width // 2 - 150, self.game.height // 2 + index * 66 + 10, 300, 52)

    def show(self):
        self.visible = True
        self.fade_alpha = 0

    def update(self, mouse_pos):
        self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)

        prev_hover = self.hover.copy()
        self.hover = [self._option_rect(i).collidepoint(mouse_pos) for i in range(2)]
        for i in range(2):
            if self.hover[i] and not prev_hover[i]:
                self.game.sound_manager.button_hover_sound.play()
            if self.hover[i]:
                self.selected = i

    def draw(self):
        screen = self.game.screen
        center_x = self.game.width // 2

        self.dim.set_alpha(min(self.fade_alpha, MAX_DIM_ALPHA))
        screen.blit(self.dim, (0, 0))

        title_y = self.game.height // 2 - 130
        draw_title(screen, get_translation("game_over"), (center_x, title_y), 76, self.game.width - 48,
                   color=theme.FLAME_LIGHT, edge=theme.BLOOD)
        draw_divider(screen, (center_x, title_y + 50), 340)

        score_y = title_y + 88
        label = get_translation("final_score")
        label_surface_width = label_font(22).size(label)[0]
        value = f"{self.game.score:06d}"
        total = label_surface_width + 14 + strong_font(28).size(value)[0]
        left = center_x - total // 2
        draw_text(screen, label, label_font(22), theme.COPPER_LIGHT, midleft=(left, score_y))
        draw_text(screen, value, strong_font(28), theme.PARCHMENT, midright=(left + total, score_y))

        for i, option in enumerate([get_translation("restart"), get_translation("main_menu")]):
            draw_menu_button(screen, self._option_rect(i), option, i == self.selected or self.hover[i], size=26)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s]:
                step = -1 if event.key in [pygame.K_UP, pygame.K_w] else 1
                self.selected = (self.selected + step) % 2
                self.game.sound_manager.button_hover_sound.play()
            elif event.key == pygame.K_RETURN:
                self._activate(self.selected)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i in range(2):
                if self._option_rect(i).collidepoint(mouse_pos):
                    self._activate(i)
                    break

    def _activate(self, index):
        self.game.sound_manager.button_click_sound.play()
        self.game.sound_manager.game_over_channel.stop()
        if index == 0:
            self.game.restart_game()
        else:
            self.game.return_code = 'menu'
            self.game.running = False
