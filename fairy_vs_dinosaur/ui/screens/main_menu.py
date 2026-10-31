import pygame

from fairy_vs_dinosaur.audio.sound_manager import SoundManager
from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.core.game import PacmanGame
from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.settings_store import load_settings
from fairy_vs_dinosaur.ui import theme
from fairy_vs_dinosaur.ui.screens.about import AboutMenu
from fairy_vs_dinosaur.ui.screens.history import HistoryMenu
from fairy_vs_dinosaur.ui.screens.settings import SettingsMenu
from fairy_vs_dinosaur.ui.widgets import draw_close_button, draw_menu_button

# Tranh nền là một cảnh đối đầu ở giữa khung hình: các nút nằm ở dải đất dưới cùng để không che cảnh đó
BUTTON_HEIGHT = 44
BUTTON_BOTTOM_MARGIN = 10
BUTTON_GAP = 10
PLAY_BUTTON_WIDTH = 256
BUTTON_WIDTH = 212
SCRIM_HEIGHT = 110
SCRIM_ALPHA = 215


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
        self.background = pygame.transform.smoothscale(background_raw, (self.width, self.height))
        self.scrim = self._build_scrim()

        self.buttons = self._build_buttons()
        self.focus_index = None  # Nút đang chọn bằng bàn phím

        self.close_rect = pygame.Rect(self.width - 46, 14, 36, 36)
        self.close_hover = False
        self.prev_close_hover = False
        self.hover_states = [False] * len(self.buttons)
        self.prev_hover_states = [False] * len(self.buttons)

        self.sound_manager.play_menu_music()

    def _build_buttons(self):
        actions = [("play_game", self.start_game), ("history", self.history),
                   ("settings", self.settings), ("about_game", self.about)]
        total = PLAY_BUTTON_WIDTH + (len(actions) - 1) * (BUTTON_WIDTH + BUTTON_GAP)
        x = (self.width - total) // 2
        y = self.height - BUTTON_HEIGHT - BUTTON_BOTTOM_MARGIN
        buttons = []
        for i, (key, action) in enumerate(actions):
            width = PLAY_BUTTON_WIDTH if i == 0 else BUTTON_WIDTH
            buttons.append({"key": key, "text": get_translation(key), "action": action,
                            "rect": pygame.Rect(x, y, width, BUTTON_HEIGHT)})
            x += width + BUTTON_GAP
        return buttons

    def _build_scrim(self):
        """Dải tối dần ở chân tranh, để các nút tách khỏi chi tiết của nền đất."""
        scrim = pygame.Surface((self.width, SCRIM_HEIGHT), pygame.SRCALPHA)
        for y in range(SCRIM_HEIGHT):
            alpha = int(SCRIM_ALPHA * (y / SCRIM_HEIGHT) ** 2)
            pygame.draw.line(scrim, (*theme.NIGHT, alpha), (0, y), (self.width, y))
        return scrim

    def draw_buttons(self):
        for i, button in enumerate(self.buttons):
            highlighted = self.hover_states[i] or i == self.focus_index
            draw_menu_button(self.screen, button["rect"], button["text"], highlighted, size=22,
                             style='primary' if i == 0 else 'normal')

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
            if event.type == pygame.KEYDOWN:
                result = self._handle_key(event.key)
                if result is not None:
                    return result
            elif event.type == pygame.MOUSEMOTION:
                self.focus_index = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        self.sound_manager.button_click_sound.play()
                        return button["action"]()
                if self.close_rect.collidepoint(mouse_pos):
                    self.sound_manager.button_click_sound.play()
                    return False
        return True

    def _handle_key(self, key):
        """Trái/phải chọn nút, Enter kích hoạt. Enter khi chưa chọn gì sẽ vào chơi luôn."""
        if key in (pygame.K_LEFT, pygame.K_RIGHT):
            step = 1 if key == pygame.K_RIGHT else -1
            start = self.focus_index if self.focus_index is not None else (-1 if step > 0 else 0)
            self.focus_index = (start + step) % len(self.buttons)
            self.sound_manager.button_hover_sound.play()
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            button = self.buttons[self.focus_index if self.focus_index is not None else 0]
            self.sound_manager.button_click_sound.play()
            return button["action"]()
        return None

    def _draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.scrim, (0, self.height - SCRIM_HEIGHT))
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
