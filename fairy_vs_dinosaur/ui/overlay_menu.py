import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui import theme
from fairy_vs_dinosaur.ui.theme import body_font, label_font, strong_font
from fairy_vs_dinosaur.ui.widgets import (draw_divider, draw_menu_button, draw_panel, draw_text, draw_title,
                                          scale_pixel_art)

CONFIRM_WIDTH = 440
CONFIRM_HEIGHT = 190
CONFIRM_BUTTON_WIDTH = 150
CONFIRM_BUTTON_HEIGHT = 46
BAR_HEIGHT = 14


class OverlayMenu:
    """Menu nổi trên màn chơi (pause, level complete): nền mờ, thanh tiến độ, các nút và hộp thoại xác nhận."""

    WIDTH = 420
    HEIGHT = 400
    BUTTON_WIDTH = 280
    BUTTON_HEIGHT = 50
    BUTTON_MARGIN = 14
    TITLE_KEY = ""

    def __init__(self, game):
        self.game = game
        self.x = (game.width - self.WIDTH) // 2
        self.y = (game.height - self.HEIGHT) // 2

        self.buttons = self._build_buttons()
        self.selected_index = 0
        self.hover_states = [False] * len(self.buttons)
        self.prev_hover_states = [False] * len(self.buttons)
        self.background_surface = None

        self.show_confirm = False
        self.confirm_selected = 0
        self.confirm_action = None
        self.confirm_hover = [False, False]
        self.prev_confirm_hover = [False, False]

        try:
            fairy_raw = pygame.image.load(asset("images/fairy/blue/tile003.png")).convert_alpha()
            self.fairy_icon = scale_pixel_art(fairy_raw, (30, 30))
        except (pygame.error, FileNotFoundError):
            print("Không thể load hình nàng tiên. Sử dụng hình tròn thay thế.")
            self.fairy_icon = None

    def _build_buttons(self):
        raise NotImplementedError

    def _buttons_start_y(self):
        raise NotImplementedError

    def _confirm_question(self):
        raise NotImplementedError

    def _execute_confirm_action(self):
        raise NotImplementedError

    def _draw_extra_info(self, screen):
        """Thông tin thêm giữa thanh tiến độ và các nút."""

    def _button_rect(self, index):
        return pygame.Rect(
            self.game.width // 2 - self.BUTTON_WIDTH // 2,
            self._buttons_start_y() + index * (self.BUTTON_HEIGHT + self.BUTTON_MARGIN),
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )

    def _confirm_button_rect(self, index):
        gap = 16
        left = self.game.width // 2 - CONFIRM_BUTTON_WIDTH - gap // 2
        top = self.game.height // 2 + CONFIRM_HEIGHT // 2 - CONFIRM_BUTTON_HEIGHT - 22
        return pygame.Rect(left + index * (CONFIRM_BUTTON_WIDTH + gap), top, CONFIRM_BUTTON_WIDTH, CONFIRM_BUTTON_HEIGHT)

    # --- Vẽ ---

    def _draw_overlay(self, screen):
        self._draw_blur_background(screen)
        draw_panel(screen, pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT))
        self._draw_menu_title(screen)
        self._draw_progress_bar(screen)
        self._draw_extra_info(screen)
        for i, button in enumerate(self.buttons):
            highlighted = self.hover_states[i] or i == self.selected_index
            draw_menu_button(screen, self._button_rect(i), button["text"], highlighted, size=25)
        if self.show_confirm:
            self._draw_confirm_dialog(screen)

    def _draw_blur_background(self, screen):
        if self.background_surface is None:
            self.background_surface = screen.copy()
            dim = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
            dim.fill((*theme.NIGHT, 190))
            self.background_surface.blit(dim, (0, 0))

        screen.blit(self.background_surface, (0, 0))

    def _draw_menu_title(self, screen):
        center_x = self.game.width // 2
        draw_title(screen, get_translation(self.TITLE_KEY), (center_x, self.y + 42), 40, self.WIDTH - 32)
        draw_divider(screen, (center_x, self.y + 76), self.WIDTH - 110)

    def _draw_progress_bar(self, screen):
        total_pellets = self.game.level.initial_pellets
        if total_pellets > 0:
            collected_pellets = total_pellets - self.game.level.remaining_pellets
            percent_complete = collected_pellets / total_pellets
        else:
            total_pellets = 1
            collected_pellets = 0
            percent_complete = 0

        bar_width = self.BUTTON_WIDTH
        bar_x = self.x + (self.WIDTH - bar_width) // 2
        bar_y = self.y + 124

        draw_text(screen, "PROGRESS", label_font(16), theme.COPPER_LIGHT, bottomleft=(bar_x, bar_y - 5))
        draw_text(screen, f"{collected_pellets}/{total_pellets}  ·  {percent_complete * 100:.1f}%", body_font(16),
                  theme.PARCHMENT, bottomright=(bar_x + bar_width, bar_y - 4))

        pygame.draw.rect(screen, theme.NIGHT, (bar_x, bar_y, bar_width, BAR_HEIGHT), border_radius=3)
        if percent_complete > 0:
            fill_width = max(6, int(bar_width * percent_complete))
            pygame.draw.rect(screen, theme.CRYSTAL, (bar_x, bar_y, fill_width, BAR_HEIGHT), border_radius=3)
        pygame.draw.rect(screen, theme.COPPER_DARK, (bar_x, bar_y, bar_width, BAR_HEIGHT), width=1, border_radius=3)

        if self.fairy_icon:
            fairy_x = bar_x + int(bar_width * percent_complete)
            screen.blit(self.fairy_icon, self.fairy_icon.get_rect(center=(fairy_x, bar_y + BAR_HEIGHT // 2 - 1)))

    def _draw_confirm_dialog(self, screen):
        dialog = pygame.Rect(0, 0, CONFIRM_WIDTH, CONFIRM_HEIGHT)
        dialog.center = (self.game.width // 2, self.game.height // 2)
        draw_panel(screen, dialog)

        font = strong_font(23)
        y = dialog.y + 28
        for line in self._wrap_text(self._confirm_question(), font, dialog.width - 64):
            y = draw_text(screen, line, font, theme.PARCHMENT, midtop=(dialog.centerx, y)).bottom + 2

        for i, option in enumerate([get_translation("yes"), get_translation("no")]):
            highlighted = self.confirm_hover[i] or i == self.confirm_selected
            draw_menu_button(screen, self._confirm_button_rect(i), option, highlighted)

    @staticmethod
    def _wrap_text(text, font, max_width):
        lines = []
        current_line = []
        for word in text.split(' '):
            if font.size(' '.join(current_line + [word]))[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    # --- Hover ---

    def _update_overlay_hover(self, mouse_pos):
        if self.show_confirm:
            self._update_confirm_hover(mouse_pos)
        else:
            self._update_menu_hover(mouse_pos)

    def _update_menu_hover(self, mouse_pos):
        for i in range(len(self.buttons)):
            current_hover = self._button_rect(i).collidepoint(mouse_pos)
            if current_hover and not self.prev_hover_states[i]:
                self.game.sound_manager.button_hover_sound.play()
            self.hover_states[i] = current_hover
            self.prev_hover_states[i] = current_hover
            if current_hover:
                self.selected_index = i

    def _update_confirm_hover(self, mouse_pos):
        new_hover = [self._confirm_button_rect(i).collidepoint(mouse_pos) for i in range(2)]
        for i in range(2):
            if new_hover[i] and not self.prev_confirm_hover[i]:
                self.game.sound_manager.button_hover_sound.play()
                self.confirm_selected = i
            self.prev_confirm_hover[i] = new_hover[i]
        self.confirm_hover = new_hover

    # --- Sự kiện ---

    def _handle_confirm_keydown(self, event):
        if event.key == pygame.K_LEFT:
            self.confirm_selected = 0
            self.game.sound_manager.button_hover_sound.play()
            return True
        if event.key == pygame.K_RIGHT:
            self.confirm_selected = 1
            self.game.sound_manager.button_hover_sound.play()
            return True
        if event.key == pygame.K_RETURN:
            return self._execute_confirm_action()
        return False

    def _handle_menu_keydown(self, event):
        if event.key in [pygame.K_UP, pygame.K_w]:
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
            self.game.sound_manager.button_hover_sound.play()
            return True
        if event.key in [pygame.K_DOWN, pygame.K_s]:
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            self.game.sound_manager.button_hover_sound.play()
            return True
        if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.game.sound_manager.button_click_sound.play()
            self.buttons[self.selected_index]["action"]()
            return True
        return False

    def _handle_overlay_click(self, mouse_pos):
        if self.show_confirm:
            if self._confirm_button_rect(0).collidepoint(mouse_pos):
                self.game.sound_manager.button_click_sound.play()
                return self._execute_confirm_action()
            if self._confirm_button_rect(1).collidepoint(mouse_pos):
                self.game.sound_manager.button_click_sound.play()
                self.show_confirm = False
                return True
            return False

        for i, button in enumerate(self.buttons):
            if self._button_rect(i).collidepoint(mouse_pos):
                self.game.sound_manager.button_click_sound.play()
                button["action"]()
                return True
        return False

    def _ask_confirm(self, action):
        self.show_confirm = True
        self.confirm_action = action
        self.confirm_selected = 0
