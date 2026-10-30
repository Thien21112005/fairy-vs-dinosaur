import pygame

from fairy_vs_dinosaur.audio.sound_manager import SoundManager
from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.core.game import PacmanGame
from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.settings_store import load_settings
from fairy_vs_dinosaur.ui.screens.about import AboutMenu
from fairy_vs_dinosaur.ui.screens.history import HistoryMenu
from fairy_vs_dinosaur.ui.screens.settings import SettingsMenu
from fairy_vs_dinosaur.ui.widgets import draw_close_button, draw_menu_button


class MainMenu:
    def __init__(self):
        pygame.init()
        self.width = 1024
        self.height = 585
        self.screen = pygame.display.set_mode([self.width, self.height], pygame.NOFRAME)
        self.timer = pygame.time.Clock()
        self.fps = 60
        self.sound_manager = SoundManager()
        self.game_settings = load_settings()
        self.sound_manager.apply_settings(self.game_settings)

        background_raw = pygame.image.load(asset("images/menu/background.png")).convert()
        self.background = pygame.transform.scale(background_raw, (self.width, self.height))

        self.button_font = pygame.font.SysFont('arial', 28, bold=True)

        button_width = 320
        button_height = 70
        spacing = 75
        start_y = self.height // 2 - 30
        button_x = self.width // 2 - button_width // 2
        self.buttons = [
            {"key": key, "text": get_translation(key), "action": action,
             "rect": pygame.Rect(button_x, start_y + i * spacing, button_width, button_height)}
            for i, (key, action) in enumerate([("play_game", self.start_game), ("history", self.history),
                                               ("settings", self.settings), ("about_game", self.about)])
        ]

        self.close_rect = pygame.Rect(self.width - 45, 15, 35, 35)
        self.close_hover = False
        self.prev_close_hover = False
        self.hover_states = [False] * len(self.buttons)
        self.prev_hover_states = [False] * len(self.buttons)

        self.sound_manager.play_menu_music()

    def draw_buttons(self):
        for i, button in enumerate(self.buttons):
            draw_menu_button(self.screen, button["rect"], button["text"], self.button_font, self.hover_states[i])

    def draw_close_button(self):
        draw_close_button(self.screen, self.close_rect, self.close_hover)

    def update_hover(self, mouse_pos):
        for i, button in enumerate(self.buttons):
            current_hover = button["rect"].collidepoint(mouse_pos)
            if current_hover and not self.prev_hover_states[i]:
                self.sound_manager.button_hover_sound.play()
            self.hover_states[i] = current_hover
            self.prev_hover_states[i] = current_hover

        current_close_hover = self.close_rect.collidepoint(mouse_pos)
        if current_close_hover and not self.prev_close_hover:
            self.sound_manager.button_hover_sound.play()
        self.close_hover = current_close_hover
        self.prev_close_hover = current_close_hover

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        self.sound_manager.button_click_sound.play()
                        return button["action"]()
                if self.close_rect.collidepoint(mouse_pos):
                    self.sound_manager.button_click_sound.play()
                    return False
        return True

    def _draw(self):
        self.screen.blit(self.background, (0, 0))
        self.draw_buttons()
        self.draw_close_button()

    def fade_out(self):
        fade_surface = pygame.Surface((self.width, self.height)).convert_alpha()
        fade_surface.fill((0, 0, 0))
        for alpha in range(0, 256, 5):
            fade_surface.set_alpha(alpha)
            self._draw()
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.timer.tick(60)

    def start_game(self):
        self.sound_manager.fade_out_menu_music(1000)
        self.fade_out()

        game = PacmanGame()
        if game.run() != 'menu':
            return False

        # Quay về từ game: khôi phục kích thước cửa sổ và nhạc menu
        self.screen = pygame.display.set_mode([self.width, self.height], pygame.NOFRAME)
        self.sound_manager.play_menu_music()
        return True

    def history(self):
        self.sound_manager.button_click_sound.play()
        HistoryMenu(self.screen, self.sound_manager, self.background).run()
        return True

    def settings(self):
        self.sound_manager.button_click_sound.play()

        settings_menu = SettingsMenu(self.screen, self.sound_manager, self.background)
        if settings_menu.run() == 'apply':
            self.game_settings = settings_menu.settings
            self.sound_manager.apply_settings(self.game_settings)

        # Ngôn ngữ có thể đã đổi
        for button in self.buttons:
            button["text"] = get_translation(button["key"])
        return True

    def about(self):
        self.sound_manager.button_click_sound.play()
        AboutMenu(self.screen, self.sound_manager, self.background).run()
        return True

    def run(self):
        running = True
        while running:
            self.timer.tick(self.fps)
            running = self.handle_events()
            self.update_hover(pygame.mouse.get_pos())
            self._draw()
            pygame.display.flip()
        pygame.quit()
