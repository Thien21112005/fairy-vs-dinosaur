import pygame

from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui.widgets import draw_gradient_rect, draw_soft_rect


class GameOverScreen:
    def __init__(self, game):
        self.game = game
        self.visible = False
        self.selected = 0  # 0: Restart, 1: Main Menu
        self.hover = [False, False]
        self.font_large = pygame.font.SysFont('monospace', 72, bold=True)
        self.font_medium = pygame.font.SysFont('monospace', 36, bold=True)
        self.font_small = pygame.font.SysFont('monospace', 24, bold=True)
        self.fade_alpha = 0
        self.fade_speed = 3

    def _option_rect(self, index):
        return pygame.Rect(self.game.width // 2 - 120, self.game.height // 2 + index * 70 - 20, 240, 50)

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
        width, height = self.game.width, self.game.height

        # Gradient từ đen sang đỏ đậm, fade in theo alpha
        overlay = pygame.Surface((width, height))
        for y in range(height):
            pygame.draw.line(overlay, (int(50 * (y / height)), 0, 0), (0, y), (width, y))
        overlay.set_alpha(self.fade_alpha)
        screen.blit(overlay, (0, 0))

        title = get_translation("game_over")
        title_text = self.font_large.render(title, True, (255, 50, 50))
        title_rect = title_text.get_rect(center=(width // 2, height // 3 - 20))
        screen.blit(self.font_large.render(title, True, (100, 0, 0)), (title_rect.x + 4, title_rect.y + 4))

        glow = pygame.Surface((title_rect.width + 20, title_rect.height + 20), pygame.SRCALPHA)
        glow.blit(title_text, (10, 10))
        glow = pygame.transform.smoothscale(glow, (title_rect.width + 40, title_rect.height + 40))
        glow.set_alpha(50)
        screen.blit(glow, (title_rect.x - 20, title_rect.y - 20))
        screen.blit(title_text, title_rect)

        score_text = self.font_small.render(f"{get_translation('final_score')}: {self.game.score:06d}", True,
                                            (255, 255, 100))
        screen.blit(score_text, score_text.get_rect(center=(width // 2, title_rect.bottom + 20)))

        for i, option in enumerate([get_translation("restart"), get_translation("main_menu")]):
            self._draw_option(option, i)

    def _draw_option(self, option, index):
        screen = self.game.screen
        rect = self._option_rect(index)

        if index == self.selected or self.hover[index]:
            gradient_start, gradient_end, border_color = (255, 200, 0), (200, 100, 0), (255, 255, 100)
            if self.hover[index]:
                draw_soft_rect(screen, rect.inflate(8, 8), (255, 255, 150, 100), border_radius=12)
        else:
            gradient_start, gradient_end, border_color = (100, 100, 100), (50, 50, 50), (150, 150, 150)

        draw_gradient_rect(screen, rect, gradient_start, gradient_end, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0, 100), rect.move(2, 2), width=3, border_radius=10)
        pygame.draw.rect(screen, border_color, rect, width=3, border_radius=10)

        text = self.font_medium.render(option, True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

        if index == self.selected:
            arrow = self.font_medium.render(">", True, (255, 255, 0))
            screen.blit(arrow, (rect.x - 40, text_rect.y))
            screen.blit(arrow, (rect.right + 10, text_rect.y))

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
