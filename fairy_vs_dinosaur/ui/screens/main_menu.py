import json
import os

import pygame

from fairy_vs_dinosaur.audio.sound_manager import SoundManager
from fairy_vs_dinosaur.core.game import PacmanGame
from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui.screens.about import AboutMenu
from fairy_vs_dinosaur.ui.screens.history import HistoryMenu
from fairy_vs_dinosaur.ui.screens.settings import SettingsMenu


class MainMenu:
    def __init__(self):
        pygame.init()
        self.width = 1024
        self.height = 585
        self.screen = pygame.display.set_mode([self.width, self.height], pygame.NOFRAME)
        self.timer = pygame.time.Clock()
        self.fps = 60
        # Thêm SoundManager
        self.sound_manager = SoundManager()
        # Load settings ngay từ đầu
        self.settings_file = "game_settings.json"
        self.load_settings()
        self.apply_audio_settings()

        # Load background image với scaling
        background_raw = pygame.image.load("assets/Mainmenu/background.png").convert()
        self.background = pygame.transform.scale(background_raw, (self.width, self.height))

        # Fonts - sử dụng font fantasy style
        self.button_font = pygame.font.SysFont('arial', 28, bold=True)
        self.title_font = pygame.font.SysFont('arial', 48, bold=True)

        # Màu sắc mới - phù hợp với vibe fairy vs dinosaur
        self.button_colors = {
            'normal': {
                'bg_start': (70, 130, 180, 180),  # Steel blue nhạt
                'bg_end': (30, 80, 120, 180),  # Dark slate blue
                'border': (120, 180, 220, 220),  # Light steel blue
                'text': (220, 240, 255),  # Very light blue
                'glow': (80, 150, 200, 60)  # Blue glow nhẹ
            },
            'hover': {
                'bg_start': (220, 160, 50, 200),  # Goldenrod
                'bg_end': (180, 120, 30, 200),  # Dark goldenrod
                'border': (255, 215, 100, 240),  # Light gold
                'text': (255, 255, 240),  # Off-white
                'glow': (255, 200, 80, 80)  # Gold glow
            }
        }

        # Close button colors
        self.close_colors = {
            'normal': {
                'bg_start': (180, 70, 70, 180),
                'bg_end': (140, 40, 40, 180),
                'border': (220, 120, 120, 220),
                'glow': (200, 100, 100, 60)
            },
            'hover': {
                'bg_start': (220, 80, 80, 200),
                'bg_end': (180, 50, 50, 200),
                'border': (255, 150, 150, 240),
                'glow': (255, 120, 120, 80)
            }
        }

        # Buttons list - điều chỉnh kích thước và vị trí
        button_width = 320
        button_height = 70
        spacing = 75
        # ĐIỀU CHỈNH: Di chuyển các nút xuống thêm nữa
        start_y = self.height // 2 - 30  # Thay đổi từ -80 thành -30 (xuống thêm 50 pixel)

        self.buttons = [
            {
                "text": get_translation("play_game"),
                "rect": pygame.Rect(self.width // 2 - button_width // 2, start_y, button_width, button_height),
                "action": self.start_game
            },
            {
                "text": get_translation("history"),
                "rect": pygame.Rect(self.width // 2 - button_width // 2, start_y + spacing, button_width,
                                    button_height),
                "action": self.history
            },
            {
                "text": get_translation("settings"),
                "rect": pygame.Rect(self.width // 2 - button_width // 2, start_y + 2 * spacing, button_width,
                                    button_height),
                "action": self.settings
            },
            {
                "text": get_translation("about_game"),
                "rect": pygame.Rect(self.width // 2 - button_width // 2, start_y + 3 * spacing, button_width,
                                    button_height),
                "action": self.about
            }
        ]

        # Close button (X) - thiết kế mới
        self.close_rect = pygame.Rect(self.width - 45, 15, 35, 35)
        self.close_hover = False
        self.prev_close_hover = False

        # Hover states
        self.hover_states = [False] * len(self.buttons)
        self.prev_hover_states = [False] * len(self.buttons)

        # Phát nhạc menu khi khởi động
        self.sound_manager.play_menu_music()

    def load_settings(self):
        """Load settings từ file, nếu không có thì tạo mặc định"""
        default_settings = {
            "music_volume": 0.8,
            "sfx_volume": 0.8,
            "music_enabled": True,
            "sfx_enabled": True,
            "control_scheme": "Arrow Keys",
            "language": "English"
        }

        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                self.game_settings = default_settings.copy()
                self.game_settings.update(loaded)
                self.save_settings()  # Save to add any new keys if needed
            else:
                self.game_settings = default_settings
                self.save_settings()
        except Exception as e:
            print(f"Lỗi khi load settings: {e}")
            self.game_settings = default_settings
            self.save_settings()

    def save_settings(self):
        """Lưu settings vào file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.game_settings, f, indent=4)
        except:
            print("Không thể lưu settings")

    def apply_audio_settings(self):
        """Áp dụng cài đặt âm thanh cho toàn bộ game"""
        # Áp dụng cho music
        if self.game_settings["music_enabled"]:
            pygame.mixer.music.set_volume(self.game_settings["music_volume"])
        else:
            pygame.mixer.music.set_volume(0)

        # Áp dụng cho tất cả sound effects
        sfx_volume = self.game_settings["sfx_volume"] if self.game_settings["sfx_enabled"] else 0

        # Cập nhật volume cho tất cả sound effects trong sound_manager
        for attr_name in dir(self.sound_manager):
            attr = getattr(self.sound_manager, attr_name)
            if isinstance(attr, pygame.mixer.Sound):
                attr.set_volume(sfx_volume)

    def draw_gradient_rect(self, surface, rect, start_color, end_color, border_color=None, border_width=0,
                           border_radius=0):
        """Vẽ hình chữ nhật gradient với viền"""
        # Main gradient
        bg_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            a = int(start_color[3] + (end_color[3] - start_color[3]) * ratio)
            color = (r, g, b, a)
            pygame.draw.line(bg_surface, color, (0, y), (rect.width, y))

        # Apply border radius bằng cách vẽ lên surface tròn
        if border_radius > 0:
            rounded_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(rounded_surface, (255, 255, 255, 255), (0, 0, rect.width, rect.height),
                             border_radius=border_radius)
            rounded_surface.blit(bg_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(rounded_surface, rect.topleft)

            # Vẽ viền
            if border_color and border_width > 0:
                pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=border_radius)
        else:
            surface.blit(bg_surface, rect.topleft)
            if border_color and border_width > 0:
                pygame.draw.rect(surface, border_color, rect, width=border_width)

    def draw_buttons(self):
        for i, button in enumerate(self.buttons):
            rect = button["rect"]
            hover = self.hover_states[i]
            colors = self.button_colors['hover'] if hover else self.button_colors['normal']

            # Shadow effect - mềm mại hơn
            shadow_rect = rect.move(4, 4)
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 40), (0, 0, shadow_rect.width, shadow_rect.height),
                             border_radius=20)
            self.screen.blit(shadow_surface, shadow_rect.topleft)

            # Glow effect on hover - tinh tế hơn
            if hover:
                glow_rect = rect.inflate(16, 16)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, colors['glow'], (0, 0, glow_rect.width, glow_rect.height),
                                 border_radius=25)
                self.screen.blit(glow_surface, glow_rect.topleft)

            # Button background với gradient và border radius
            self.draw_gradient_rect(
                self.screen, rect,
                colors['bg_start'], colors['bg_end'],
                border_color=colors['border'],
                border_width=3,
                border_radius=18
            )

            # Text đơn giản không có icon
            text_color = colors['text']
            text = self.button_font.render(button["text"], True, text_color)
            text_rect = text.get_rect(center=rect.center)

            # Text shadow nhẹ
            shadow_text = self.button_font.render(button["text"], True, (0, 0, 0, 100))
            self.screen.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
            self.screen.blit(text, text_rect)

    def draw_close_button(self):
        colors = self.close_colors['hover'] if self.close_hover else self.close_colors['normal']

        # Shadow
        shadow_rect = self.close_rect.move(2, 2)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), (0, 0, shadow_rect.width, shadow_rect.height),
                         border_radius=8)
        self.screen.blit(shadow_surface, shadow_rect.topleft)

        # Glow effect
        if self.close_hover:
            glow_rect = self.close_rect.inflate(10, 10)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, colors['glow'], (0, 0, glow_rect.width, glow_rect.height),
                             border_radius=12)
            self.screen.blit(glow_surface, glow_rect.topleft)

        # Close button background
        self.draw_gradient_rect(
            self.screen, self.close_rect,
            colors['bg_start'], colors['bg_end'],
            border_color=colors['border'],
            border_width=2,
            border_radius=10
        )

        # Text X
        close_font = pygame.font.SysFont('arial', 20, bold=True)
        close_text = close_font.render("×", True, (255, 255, 255))
        text_rect = close_text.get_rect(center=self.close_rect.center)
        self.screen.blit(close_text, text_rect)

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, button in enumerate(self.buttons):
                    if button["rect"].collidepoint(mouse_pos):
                        self.sound_manager.button_click_sound.play()
                        return button["action"]()
                if self.close_rect.collidepoint(mouse_pos):
                    self.sound_manager.button_click_sound.play()
                    return False
        return True

    def fade_out(self):
        fade_surface = pygame.Surface((self.width, self.height)).convert_alpha()
        fade_surface.fill((0, 0, 0))
        for alpha in range(0, 256, 5):
            fade_surface.set_alpha(alpha)
            self.screen.blit(self.background, (0, 0))
            self.draw_buttons()
            self.draw_close_button()
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.timer.tick(60)

    def start_game(self):
        self.sound_manager.fade_out_menu_music(1000)
        self.fade_out()

        # THAY ĐỔI: Tạo game với kích thước cửa sổ game
        game = PacmanGame()
        game.set_main_menu(self)  # Truyền reference tới main menu

        result = game.run()

        # KHI QUAY VỀ TỪ GAME: khôi phục kích thước và âm thanh menu
        if result == 'menu':

            game.player.ai_path = []
            # Khôi phục kích thước cửa sổ menu
            self.screen = pygame.display.set_mode([self.width, self.height], pygame.NOFRAME)
            # Phát lại nhạc menu
            self.sound_manager.play_menu_music()

            return True
        else:
            return False

    def history(self):
        """Hàm xử lý cho nút HISTORY"""
        self.sound_manager.button_click_sound.play()
        # Tạo history menu với callback để quay lại
        history_menu = HistoryMenu(self.screen, self.sound_manager, self.background, self.back_from_history)
        result = history_menu.run()
        return True

    def settings(self):
        """Hiển thị màn hình settings"""
        self.sound_manager.button_click_sound.play()

        # Tạo settings menu với callback để quay lại
        settings_menu = SettingsMenu(self.screen, self.sound_manager, self.background, self.back_from_settings)
        result = settings_menu.run()

        # Nếu apply thành công, cập nhật lại âm thanh menu
        if result == 'apply':
            self.game_settings = settings_menu.settings  # Cập nhật self.game_settings từ settings_menu
            self.apply_audio_settings()  # Áp dụng lại audio settings

        # Update buttons text if language changed
        self.buttons[0]["text"] = get_translation("play_game")
        self.buttons[1]["text"] = get_translation("history")
        self.buttons[2]["text"] = get_translation("settings")
        self.buttons[3]["text"] = get_translation("about_game")

        return True

    def back_from_settings(self):
        """Callback để quay lại từ settings"""
        # Không cần làm gì đặc biệt, chỉ cần thoát khỏi settings
        pass

    def back_from_history(self):
        """Callback để quay lại từ history"""
        pass

    def about(self):
        """Hiển thị màn hình about game"""
        self.sound_manager.button_click_sound.play()
        # Tạo about menu với callback để quay lại
        about_menu = AboutMenu(self.screen, self.sound_manager, self.background, self.back_from_about)
        about_menu.run()
        return True
    def back_from_about(self):
        """Callback để quay lại từ about"""
        pass
    def run(self):
        running = True
        while running:
            self.timer.tick(self.fps)
            running = self.handle_events()
            mouse_pos = pygame.mouse.get_pos()
            self.update_hover(mouse_pos)
            # VẼ LẠI TOÀN BỘ MENU
            self.screen.blit(self.background, (0, 0))
            self.draw_buttons()
            self.draw_close_button()
            pygame.display.flip()
        pygame.quit()
