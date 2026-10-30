import pygame

from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui.overlay_menu import OverlayMenu

CONFIRM_RESTART = 1
CONFIRM_MAIN_MENU = 2


class PauseMenu(OverlayMenu):
    TITLE_KEY = "paused"

    def __init__(self, game):
        super().__init__(game)
        self.visible = False
        self.pause_button_hover = False
        self.prev_pause_button_hover = False
        self.pause_button_rect = pygame.Rect(self.game.width - 50, 10, 40, 40)

    def _build_buttons(self):
        return [
            {"text": get_translation("resume"), "action": self.resume_game},
            {"text": get_translation("restart"), "action": self.confirm_restart},
            {"text": get_translation("main_menu"), "action": self.confirm_main_menu}
        ]

    def _buttons_start_y(self):
        return self.y + 150

    def _confirm_question(self):
        if self.confirm_action == CONFIRM_RESTART:
            return "Restart the game? Progress will not be saved."
        return "Return to main menu? Progress will not be saved."

    def draw_pause_button(self, screen):
        """Vẽ nút pause nhỏ ở góc phải"""
        if self.pause_button_hover:
            colors = {'bg': (255, 215, 0), 'bg_dark': (235, 195, 0), 'border': (255, 255, 150)}
        else:
            colors = {'bg': (80, 80, 140), 'bg_dark': (60, 60, 120), 'border': (100, 160, 200)}

        pygame.draw.rect(screen, (0, 0, 0, 100), self.pause_button_rect.move(2, 2), border_radius=12)

        width, height = self.pause_button_rect.size
        button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(height):
            ratio = y / height
            color = (
                int(colors['bg'][0] * (1 - ratio) + colors['bg_dark'][0] * ratio),
                int(colors['bg'][1] * (1 - ratio) + colors['bg_dark'][1] * ratio),
                int(colors['bg'][2] * (1 - ratio) + colors['bg_dark'][2] * ratio)
            )
            pygame.draw.line(button_surface, color, (0, y), (width, y))

        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, width, height), border_radius=10)
        button_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(button_surface, self.pause_button_rect.topleft)

        pygame.draw.rect(screen, colors['border'], self.pause_button_rect, width=3, border_radius=10)
        self._draw_pause_icon(screen)

    def _draw_pause_icon(self, screen):
        bar_width = 6
        bar_height = 22
        bar_spacing = 5

        left_bar_x = self.pause_button_rect.centerx - bar_width - bar_spacing // 2
        right_bar_x = self.pause_button_rect.centerx + bar_spacing // 2
        bar_y = self.pause_button_rect.centery - bar_height // 2

        pygame.draw.rect(screen, (50, 50, 50, 100), (left_bar_x + 1, bar_y + 1, bar_width, bar_height))
        pygame.draw.rect(screen, (50, 50, 50, 100), (right_bar_x + 1, bar_y + 1, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (left_bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (right_bar_x, bar_y, bar_width, bar_height))

    def draw(self, screen):
        if self.visible:
            self._draw_overlay(screen)
        else:
            self.draw_pause_button(screen)

    def update_hover(self, mouse_pos):
        current_pause_hover = self.pause_button_rect.collidepoint(mouse_pos)
        if current_pause_hover and not self.prev_pause_button_hover:
            self.game.sound_manager.button_hover_sound.play()
        self.pause_button_hover = current_pause_hover
        self.prev_pause_button_hover = current_pause_hover

        if self.visible:
            self._update_overlay_hover(mouse_pos)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_click()
        return False

    def _handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            return self._handle_escape()
        if not self.visible:
            return False
        if self.show_confirm:
            return self._handle_confirm_keydown(event)
        return self._handle_menu_keydown(event)

    def _handle_escape(self):
        if not self.visible:
            self.pause_game()
        elif self.show_confirm:
            self.show_confirm = False
        else:
            self.resume_game()
        return True

    def _handle_mouse_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.visible:
            return self._handle_overlay_click(mouse_pos)
        if self.pause_button_rect.collidepoint(mouse_pos):
            self.pause_game()
            return True
        return False

    def _execute_confirm_action(self):
        if self.confirm_selected != 0:
            self.show_confirm = False
        elif self.confirm_action == CONFIRM_RESTART:
            self.game.restart_game()
        else:
            self.game.return_code = 'menu'
            self.game.running = False
        return True

    def pause_game(self):
        if not self.visible and not self.game.dying and not self.game.ui.game_over.visible:
            self.visible = True
            self.background_surface = None
            self.game.sound_manager.button_click_sound.play()

            self.game.sound_manager.stop_ghost()
            self.game.sound_manager.stop_power()
            self.game.sound_manager.pause_turn_egg()

            if self.game.sound_manager.intro_channel.get_busy():
                self.game.sound_manager.pause_intro()

            self.selected_index = 0

    def resume_game(self):
        if self.visible:
            self.visible = False
            self.game.sound_manager.button_click_sound.play()
            self.game.countdown_active = True
            self.game.countdown_timer = 3.0

    def confirm_restart(self):
        self._ask_confirm(CONFIRM_RESTART)

    def confirm_main_menu(self):
        self._ask_confirm(CONFIRM_MAIN_MENU)
