import pygame

from fairy_vs_dinosaur.ui.widgets import get_font


class GameRenderMixin:
    """Các cách vẽ khung hình theo từng trạng thái của game."""

    def _draw_background(self):
        self.screen.fill('black')
        self.screen.blit(self.background, (0, self.y_offset))

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
            for ghost in self.ghosts:
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
        scale = 1.0 + progress * 0.3
        alpha = int(255 * (1 - progress * 0.8))
        size = int(120 * scale)
        font = get_font('Arial', size, bold=True)
        center = (size, size)
        base_color = (0, 255, 255)
        bright_color = (100, 255, 255)

        text_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        glow_radius = int(20 * scale)
        for r in range(glow_radius, 0, -2):
            glow_alpha = int(50 * (r / glow_radius) * (alpha / 255))
            pygame.draw.circle(text_surface, (*bright_color, glow_alpha), center, size + r)

        shadow = font.render(str(count), True, (0, 50, 100))
        shadow.set_alpha(alpha // 2)
        text_surface.blit(shadow, shadow.get_rect(center=(size + 4, size + 4)))

        main_text = font.render(str(count), True, base_color)
        main_text.set_alpha(alpha)
        text_surface.blit(main_text, main_text.get_rect(center=center))

        highlight = font.render(str(count), True, bright_color)
        highlight.set_alpha(min(alpha, 200))
        text_surface.blit(highlight, highlight.get_rect(center=(size - 2, size - 2)))

        self.screen.blit(text_surface, text_surface.get_rect(center=(self.width // 2, self.height // 2)))

    def _draw_level_anim_frame(self):
        self._draw_background()
        self.ui.draw_header()
        self.level.draw_board()
        if self.show_hint and not self.dying and not self.just_reset:
            self.player.draw_path()
            for ghost in self.ghosts:
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
