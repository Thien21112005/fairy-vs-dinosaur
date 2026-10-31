import pygame

from fairy_vs_dinosaur.ui import theme
from fairy_vs_dinosaur.ui.widgets import outlined_text


class GameRenderMixin:
    """Các cách vẽ khung hình theo từng trạng thái của game."""

    _countdown_dim = None
    _countdown_digits = {}

    def _draw_background(self):
        self.screen.fill(theme.NIGHT)
        self.screen.blit(self.background, (0, self.y_offset))
        self.ui.draw_footer()

    def _draw_visible_ghosts(self):
        for ghost in self.visible_ghosts():
            ghost.draw()

    def _draw_controls(self):
        self.ui.draw_ready()
        self.ui.draw_lives()
        self.ui.draw_hint_button()
        self.ui.draw_ghost_toggle_buttons()
        self.ui.draw_solve_button()

    def _draw_compact_scene(self):
        """Bản đồ và nhân vật, không có nút điều khiển: dùng làm nền cho đếm ngược và các màn phủ."""
        self._draw_background()
        self.level.draw_board()
        self.player.draw()
        self._draw_visible_ghosts()
        self.ui.draw_header()
        self.ui.draw_lives()

    def _draw_full_scene(self):
        self._draw_background()
        self.ui.draw_header()
        self.level.draw_board()
        if self.show_hint and not self.dying and not self.just_reset:
            self.player.draw_path()
            for ghost in self.visible_ghosts():
                ghost.draw_path()
        self.player.draw()
        self._draw_visible_ghosts()
        self._draw_controls()

    def fade_in(self):
        fade_surface = pygame.Surface((self.width, self.height)).convert_alpha()
        fade_surface.fill((0, 0, 0))
        for alpha in range(255, -1, -5):
            fade_surface.set_alpha(alpha)
            self._draw_full_scene()
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.timer.tick(60)

    def draw_game_screen(self):
        self._draw_full_scene()
        self.pause_menu.draw(self.screen)
        pygame.display.flip()

    def _draw_countdown_frame(self, count):
        self._draw_compact_scene()
        if count > 0:
            self._draw_countdown_number(count)
        pygame.display.flip()

    def _draw_countdown_number(self, count):
        progress = 1.0 - (self.countdown_timer % 1.0)  # 0.0 -> 1.0 trong mỗi giây
        scale = 1.0 + 0.35 * (1.0 - progress) ** 3  # Đập mạnh rồi lắng xuống
        alpha = 255 if progress < 0.7 else int(255 * (1.0 - progress) / 0.3)

        if GameRenderMixin._countdown_dim is None:
            GameRenderMixin._countdown_dim = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            GameRenderMixin._countdown_dim.fill((*theme.NIGHT, 130))
        self.screen.blit(self._countdown_dim, (0, 0))

        if count not in self._countdown_digits:
            self._countdown_digits[count] = outlined_text(str(count), theme.display_font(150), theme.STONE,
                                                          theme.COPPER_DARK, width=4)
        digit = self._countdown_digits[count]
        size = (int(digit.get_width() * scale), int(digit.get_height() * scale))
        scaled = pygame.transform.smoothscale(digit, size)
        scaled.set_alpha(alpha)
        self.screen.blit(scaled, scaled.get_rect(center=(self.width // 2, self.height // 2)))

    def _draw_level_anim_frame(self):
        self._draw_background()
        self.ui.draw_header()
        self.level.draw_board()
        if self.show_hint and not self.dying and not self.just_reset:
            self.player.draw_path()
            for ghost in self.visible_ghosts():
                ghost.draw_path()
        self._draw_visible_ghosts()
        self._draw_controls()
        self.level_anim.draw()
        pygame.display.flip()

    def _draw_dying_frame(self):
        self._draw_background()
        self.level.draw_board()
        self.player.draw()
        self._draw_visible_ghosts()
        self.ui.draw_header()
        self._draw_controls()

        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.width, self.height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surface, (0, 0))

        pygame.display.flip()

    def _draw_playing_frame(self, dt):
        self._draw_background()
        self.ui.draw_header()
        self.level.draw_board()

        # Chỉ vẽ đường đi khi bật hint và không ở chuỗi chết hoặc vừa reset
        if self.show_hint and not self.dying and not self.just_reset:
            for ghost in self.visible_ghosts():
                ghost.draw_path()
            if self.ai_mode:
                self.player.draw_path()

        self.player.draw()
        self._draw_visible_ghosts()
        self._draw_controls()
        self._update_floating_scores(dt)
        pygame.display.flip()

    def _update_floating_scores(self, dt):
        remaining = []
        for points, x, y, timer in self.floating_scores:
            timer -= dt
            if timer > 0:
                remaining.append((points, x, y, timer))
                image = self.score_images[points]
                self.screen.blit(image, (x - image.get_width() / 2, y - image.get_height() / 2))
        self.floating_scores = remaining
