import pygame

from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui.overlay_menu import OverlayMenu
from fairy_vs_dinosaur.ui.widgets import draw_slab_button

CONFIRM_RESTART = 1
CONFIRM_MAIN_MENU = 2


class PauseMenu(OverlayMenu):
    TITLE_KEY = "paused"

    def __init__(self, game):
        super().__init__(game)
        self.visible = False
        self.pause_button_hover = False
        self.prev_pause_button_hover = False
        self.pause_button_rect = pygame.Rect(self.game.width - 48, 5, 40, 40)

    def _build_buttons(self):
        return [
            {"text": get_translation("resume"), "action": self.resume_game},
            {"text": get_translation("restart"), "action": self.confirm_restart},
            {"text": get_translation("main_menu"), "action": self.confirm_main_menu}
        ]

    def _buttons_start_y(self):
        return self.y + 176

    def _confirm_question(self):
        if self.confirm_action == CONFIRM_RESTART:
            return "Restart the game? Progress will not be saved."
        return "Return to main menu? Progress will not be saved."

    def draw_pause_button(self, screen):
        """Vẽ nút pause nhỏ ở góc phải"""
        colors = draw_slab_button(screen, self.pause_button_rect, 'active' if self.pause_button_hover else 'normal')
        bar_width, bar_height, gap = 5, 16, 5
        top = self.pause_button_rect.centery - bar_height // 2
        left = self.pause_button_rect.centerx - bar_width - gap // 2
        pygame.draw.rect(screen, colors['text'], (left, top, bar_width, bar_height))
        pygame.draw.rect(screen, colors['text'], (left + bar_width + gap, top, bar_width, bar_height))

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
