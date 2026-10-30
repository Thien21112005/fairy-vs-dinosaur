import json
import os

import pygame

from fairy_vs_dinosaur.config import SETTINGS_FILE
from fairy_vs_dinosaur.i18n import get_translation


class SettingsMenu:
    def __init__(self, screen, sound_manager, background, back_callback):
        self.screen = screen
        self.sound_manager = sound_manager
        self.background = background
        self.back_callback = back_callback
        self.width, self.height = screen.get_size()

        # Load settings từ file
        self.settings_file = SETTINGS_FILE
        self.load_settings()

        # Apply initial settings
        self.apply_audio_settings()

        # Fonts - changed to 'times' for a more elegant, fantasy-like feel (if available; falls back to system default)
        self.title_font = pygame.font.SysFont('times', 48, bold=True)
        self.section_font = pygame.font.SysFont('times', 32, bold=True)
        self.option_font = pygame.font.SysFont('times', 24)
        self.button_font = pygame.font.SysFont('times', 28, bold=True)
        self.volume_font = pygame.font.SysFont('times', 20)

        # Updated theme colors to better match the image: dark mystical tones, gold title, blue buttons, light text for contrast
        self.panel_color = (20, 40, 60, 180)  # Semi-transparent dark blueish-purple panel to blend with background
        self.bg_color = (0, 0, 0, 128)  # Semi-transparent dark overlay (kept same)
        self.title_color = (184, 134, 11)  # Goldish rusty color like the title in the image
        self.section_color = (150, 150, 150)  # Lighter gray for sections
        self.text_color = (220, 220, 220)  # Light text for better contrast on dark panel
        self.highlight_color = (100, 200, 255)  # Blue glow highlight to match fairy/mushroom tones
        self.slider_bg_color = (50, 50, 50)  # Dark gray slider bg
        self.slider_color = (0, 191, 255)  # Blue slider fill
        self.slider_knob_color = (100, 100, 100)  # Dark gray knob
        self.toggle_on_color = (0, 200, 100)  # Greenish for ON, matching forest elements
        self.toggle_off_color = (200, 50, 50)  # Reddish for OFF, matching dinosaur
        self.button_color = (70, 130, 180)  # Blue buttons like in the image
        self.button_hover_color = (50, 100, 150)  # Darker blue hover
        self.shadow_color = (0, 0, 0, 50)  # Soft shadow for panel

        # Control scheme options
        self.control_schemes = ["Arrow Keys", "WASD", "Mixed"]  # Keep in English as technical terms

        # Language options
        self.languages = ["English", "Vietnamese", "French", "Spanish"]  # Keep names in English

        # Panel dimensions - reverted height to original since fullscreen is removed
        self.panel_width = 700
        self.panel_height = 550
        self.panel_x = (self.width - self.panel_width) // 2
        self.panel_y = (self.height - self.panel_height) // 2
        self.panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)

        # UI Elements - adjusted to fit inside panel
        panel_inner_x = self.panel_x + 50
        panel_inner_y = self.panel_y + 120  # Adjusted for better spacing
        self.back_button_rect = pygame.Rect(self.panel_x + 100, self.panel_y + self.panel_height - 80, 200, 50)
        self.apply_button_rect = pygame.Rect(self.panel_x + self.panel_width - 300, self.panel_y + self.panel_height - 80, 200, 50)

        # Slider positions - moved right to avoid label overlap, width reduced for better fit
        self.music_slider_rect = pygame.Rect(panel_inner_x + 220, panel_inner_y, 250, 20)
        self.sfx_slider_rect = pygame.Rect(panel_inner_x + 220, panel_inner_y + 60, 250, 20)

        # Toggle positions - moved right to add space after percentage
        self.music_toggle_rect = pygame.Rect(panel_inner_x + 530, panel_inner_y - 5, 80, 30)
        self.sfx_toggle_rect = pygame.Rect(panel_inner_x + 530, panel_inner_y + 55, 80, 30)

        # Selector positions - aligned with sliders, adjusted spacing
        self.control_selector_rect = pygame.Rect(panel_inner_x + 220, panel_inner_y + 120, 250, 40)
        self.language_selector_rect = pygame.Rect(panel_inner_x + 220, panel_inner_y + 190, 250, 40)

        # Hover states
        self.back_hover = False
        self.apply_hover = False
        self.prev_back_hover = False
        self.prev_apply_hover = False
        self.music_slider_hover = False
        self.sfx_slider_hover = False
        self.dragging_music = False
        self.dragging_sfx = False

        # Temp settings for apply
        self.temp_settings = self.settings.copy()

        # Preview sound for testing volume
        self.preview_sound = self.sound_manager.button_click_sound

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
                self.settings = default_settings.copy()
                self.settings.update(loaded)
                self.save_settings()  # Save to add any new keys if needed
            else:
                self.settings = default_settings
                self.save_settings()
        except Exception as e:
            print(f"Lỗi khi load settings: {e}")
            self.settings = default_settings
            self.save_settings()

    def save_settings(self):
        """Lưu settings vào file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except:
            print("Không thể lưu settings")

    def apply_settings(self):
        """Áp dụng settings"""
        self.settings = self.temp_settings.copy()
        self.save_settings()

        # Áp dụng âm thanh ngay lập tức
        self.apply_audio_settings()

    def apply_audio_settings(self):
        """Áp dụng cài đặt âm thanh cho toàn bộ game"""
        # Áp dụng cho music
        if self.settings["music_enabled"]:
            pygame.mixer.music.set_volume(self.settings["music_volume"])
        else:
            pygame.mixer.music.set_volume(0)

        # Áp dụng cho tất cả sound effects
        sfx_volume = self.settings["sfx_volume"] if self.settings["sfx_enabled"] else 0

        # Cập nhật volume cho tất cả sound effects trong sound_manager
        for attr_name in dir(self.sound_manager):
            attr = getattr(self.sound_manager, attr_name)
            if isinstance(attr, pygame.mixer.Sound):
                attr.set_volume(sfx_volume)

    def draw_slider(self, surface, rect, value, hover=False, dragging=False):
        """Vẽ thanh slider với hiển thị giá trị"""
        # Background
        pygame.draw.rect(surface, self.slider_bg_color, rect, border_radius=10)

        # Filled portion
        fill_width = int(value * rect.width)
        fill_rect = pygame.Rect(rect.left, rect.top, fill_width, rect.height)
        pygame.draw.rect(surface, self.slider_color, fill_rect, border_radius=10)

        # Knob
        knob_x = rect.left + fill_width - 10
        knob_rect = pygame.Rect(knob_x, rect.top - 5, 20, 30)
        knob_color = self.highlight_color if hover or dragging else self.slider_knob_color
        pygame.draw.rect(surface, knob_color, knob_rect, border_radius=10)

        # Volume text
        volume_text = self.volume_font.render(f"{int(value * 100)}%", True, self.text_color)
        volume_y = rect.centery - volume_text.get_height() // 2
        surface.blit(volume_text, (rect.right + 10, volume_y))

        return knob_rect

    def draw_toggle(self, surface, rect, state):
        """Vẽ nút toggle kiểu slide"""
        # Background
        bg_color = self.toggle_on_color if state else self.toggle_off_color
        pygame.draw.rect(surface, bg_color, rect, border_radius=15)

        # Knob
        knob_x = rect.right - 30 if state else rect.left + 5
        knob_rect = pygame.Rect(knob_x, rect.top + 5, 20, 20)
        pygame.draw.circle(surface, (255, 255, 255), knob_rect.center, 10)

        # Text
        state_text = get_translation("on") if state else get_translation("off")
        text_color = (255, 255, 255)
        state_surface = self.volume_font.render(state_text, True, text_color)
        text_x = rect.centerx - state_surface.get_width() // 2
        text_y = rect.centery - state_surface.get_height() // 2
        surface.blit(state_surface, (text_x, text_y))

        return rect

    def draw_option_selector(self, surface, rect, options, selected_index):
        """Vẽ selector cho các tùy chọn"""
        # Background
        pygame.draw.rect(surface, self.slider_bg_color, rect, border_radius=20)
        pygame.draw.rect(surface, (100, 100, 100), rect, 2, border_radius=20)  # Slightly darker border

        # Text
        text = self.option_font.render(options[selected_index], True, self.text_color)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

        # Arrows (triangles)
        arrow_color = (150, 150, 150)  # Lighter arrows
        arrow_size = 10

        # Left arrow (pointing left)
        left_arrow = [
            (rect.left + 20 + arrow_size, rect.centery - arrow_size // 2),
            (rect.left + 20, rect.centery),
            (rect.left + 20 + arrow_size, rect.centery + arrow_size // 2)
        ]
        pygame.draw.polygon(surface, arrow_color, left_arrow)

        # Right arrow (pointing right)
        right_arrow = [
            (rect.right - 20 - arrow_size, rect.centery - arrow_size // 2),
            (rect.right - 20, rect.centery),
            (rect.right - 20 - arrow_size, rect.centery + arrow_size // 2)
        ]
        pygame.draw.polygon(surface, arrow_color, right_arrow)

        return rect

    def draw_icon(self, surface, icon_type, pos):
        """Vẽ icon đơn giản bên trái slider - updated colors for better visibility"""
        icon_color = self.highlight_color  # Use highlight color for icons
        if icon_type == "music":
            # Music note icon
            pygame.draw.rect(surface, icon_color, (pos[0], pos[1] + 10, 5, 20))  # Stem
            pygame.draw.ellipse(surface, icon_color, (pos[0] + 5, pos[1] + 25, 15, 10))  # Note head
            pygame.draw.line(surface, icon_color, (pos[0] + 5, pos[1]), (pos[0] + 5, pos[1] + 10), 3)  # Flag
        elif icon_type == "sound":
            # Speaker icon
            pygame.draw.rect(surface, icon_color, (pos[0], pos[1], 15, 30))  # Body
            pygame.draw.polygon(surface, icon_color, [(pos[0] + 15, pos[1] + 5), (pos[0] + 30, pos[1] + 15), (pos[0] + 15, pos[1] + 25)])  # Cone

    def draw(self):
        """Vẽ toàn bộ giao diện settings - added shadow, icons, and semi-transparent panel with Surface"""
        # Draw main menu background
        self.screen.blit(self.background, (0, 0))

        # Overlay background
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        self.screen.blit(bg_surface, (0, 0))

        # Shadow for panel (added for nice visual effect)
        shadow_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, self.shadow_color, (0, 0, self.panel_width, self.panel_height), border_radius=30)
        self.screen.blit(shadow_surface, (self.panel_x + 5, self.panel_y + 5))

        # Main panel - using Surface for true semi-transparency and rounded corners
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.panel_color, (0, 0, self.panel_width, self.panel_height), border_radius=30)
        self.screen.blit(panel_surface, (self.panel_x, self.panel_y))

        # Title - added slight glow effect by drawing outline
        title_text = self.title_font.render(get_translation("settings"), True, self.title_color)
        title_rect = title_text.get_rect(center=(self.width // 2, self.panel_y + 50))
        # Glow: draw slightly offset with semi-transparent color
        glow_color = (255, 255, 255, 100)
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            glow_text = self.title_font.render(get_translation("settings"), True, self.highlight_color)
            self.screen.blit(glow_text, title_rect.move(dx, dy))
        self.screen.blit(title_text, title_rect)

        # Music label
        music_text = self.option_font.render(get_translation("music"), True, self.text_color)
        music_rect = music_text.get_rect(midleft=(self.panel_x + 50, self.music_slider_rect.centery))
        self.screen.blit(music_text, music_rect)

        music_toggle_rect = self.draw_toggle(self.screen, self.music_toggle_rect, self.temp_settings["music_enabled"])
        music_knob_rect = self.draw_slider(self.screen, self.music_slider_rect,
                                           self.temp_settings["music_volume"],
                                           self.music_slider_hover, self.dragging_music)

        # Sound Effects label
        sfx_text = self.option_font.render(get_translation("sound_effects"), True, self.text_color)
        sfx_rect = sfx_text.get_rect(midleft=(self.panel_x + 50, self.sfx_slider_rect.centery))
        self.screen.blit(sfx_text, sfx_rect)

        sfx_toggle_rect = self.draw_toggle(self.screen, self.sfx_toggle_rect, self.temp_settings["sfx_enabled"])
        sfx_knob_rect = self.draw_slider(self.screen, self.sfx_slider_rect,
                                         self.temp_settings["sfx_volume"],
                                         self.sfx_slider_hover, self.dragging_sfx)

        # Control Scheme label
        scheme_text = self.option_font.render(get_translation("control_scheme"), True, self.text_color)
        scheme_rect = scheme_text.get_rect(midleft=(self.panel_x + 50, self.control_selector_rect.centery))
        self.screen.blit(scheme_text, scheme_rect)

        selected_scheme = self.control_schemes.index(self.temp_settings["control_scheme"])
        control_selector_rect = self.draw_option_selector(self.screen, self.control_selector_rect,
                                                          self.control_schemes, selected_scheme)

        # Language label
        lang_text = self.option_font.render(get_translation("language"), True, self.text_color)
        lang_rect = lang_text.get_rect(midleft=(self.panel_x + 50, self.language_selector_rect.centery))
        self.screen.blit(lang_text, lang_rect)

        selected_lang = self.languages.index(self.temp_settings["language"])
        language_selector_rect = self.draw_option_selector(self.screen, self.language_selector_rect,
                                                           self.languages, selected_lang)

        # === BUTTONS ===
        # Back button
        back_color = self.button_hover_color if self.back_hover else self.button_color
        pygame.draw.rect(self.screen, back_color, self.back_button_rect, border_radius=25)
        pygame.draw.rect(self.screen, (255, 255, 255), self.back_button_rect, 2, border_radius=25)  # Added border for better look
        back_text = self.button_font.render(get_translation("back"), True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)

        # Apply button
        apply_color = self.button_hover_color if self.apply_hover else self.button_color
        pygame.draw.rect(self.screen, apply_color, self.apply_button_rect, border_radius=25)
        pygame.draw.rect(self.screen, (255, 255, 255), self.apply_button_rect, 2, border_radius=25)  # Added border
        apply_text = self.button_font.render(get_translation("apply"), True, (255, 255, 255))
        apply_text_rect = apply_text.get_rect(center=self.apply_button_rect.center)
        self.screen.blit(apply_text, apply_text_rect)

        return {
            "music_toggle": music_toggle_rect,
            "sfx_toggle": sfx_toggle_rect,
            "music_slider": music_knob_rect,
            "sfx_slider": sfx_knob_rect,
            "control_selector": control_selector_rect,
            "language_selector": language_selector_rect,
            "back_button": self.back_button_rect,
            "apply_button": self.apply_button_rect
        }

    def handle_events(self, event):
        """Xử lý sự kiện trong settings"""
        mouse_pos = pygame.mouse.get_pos()
        ui_elements = self.draw()  # Note: draw() now returns the rects

        # Update hover states
        self.back_hover = self.back_button_rect.collidepoint(mouse_pos)
        self.apply_hover = self.apply_button_rect.collidepoint(mouse_pos)
        self.music_slider_hover = self.music_slider_rect.collidepoint(mouse_pos)
        self.sfx_slider_hover = self.sfx_slider_rect.collidepoint(mouse_pos)

        # Check for hover sound
        if self.back_hover and not self.prev_back_hover:
            self.sound_manager.button_hover_sound.play()
        if self.apply_hover and not self.prev_apply_hover:
            self.sound_manager.button_hover_sound.play()

        self.prev_back_hover = self.back_hover
        self.prev_apply_hover = self.apply_hover

        if event.type == pygame.MOUSEBUTTONDOWN:
            if ui_elements["back_button"].collidepoint(mouse_pos):
                self.sound_manager.button_click_sound.play()
                return 'back'

            elif ui_elements["apply_button"].collidepoint(mouse_pos):
                self.sound_manager.button_click_sound.play()
                self.apply_settings()
                return 'apply'

            elif ui_elements["music_toggle"].collidepoint(mouse_pos):
                self.temp_settings["music_enabled"] = not self.temp_settings["music_enabled"]
                self.sound_manager.button_click_sound.play()
                self.preview_audio_settings()

            elif ui_elements["sfx_toggle"].collidepoint(mouse_pos):
                self.temp_settings["sfx_enabled"] = not self.temp_settings["sfx_enabled"]
                self.sound_manager.button_click_sound.play()
                self.preview_audio_settings()

            elif ui_elements["music_slider"].collidepoint(mouse_pos) or self.music_slider_rect.collidepoint(mouse_pos):
                self.dragging_music = True
                self.update_music_volume(mouse_pos)

            elif ui_elements["sfx_slider"].collidepoint(mouse_pos) or self.sfx_slider_rect.collidepoint(mouse_pos):
                self.dragging_sfx = True
                self.update_sfx_volume(mouse_pos)

            elif ui_elements["control_selector"].collidepoint(mouse_pos):
                current_index = self.control_schemes.index(self.temp_settings["control_scheme"])
                if mouse_pos[0] < ui_elements["control_selector"].centerx:
                    new_index = (current_index - 1) % len(self.control_schemes)
                else:
                    new_index = (current_index + 1) % len(self.control_schemes)
                self.temp_settings["control_scheme"] = self.control_schemes[new_index]
                self.sound_manager.button_click_sound.play()

            elif ui_elements["language_selector"].collidepoint(mouse_pos):
                current_index = self.languages.index(self.temp_settings["language"])
                if mouse_pos[0] < ui_elements["language_selector"].centerx:
                    new_index = (current_index - 1) % len(self.languages)
                else:
                    new_index = (current_index + 1) % len(self.languages)
                self.temp_settings["language"] = self.languages[new_index]
                self.sound_manager.button_click_sound.play()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_music = False
            self.dragging_sfx = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_music:
                self.update_music_volume(mouse_pos)
            if self.dragging_sfx:
                self.update_sfx_volume(mouse_pos)

        return None

    def update_music_volume(self, mouse_pos):
        relative_x = max(0, min(mouse_pos[0] - self.music_slider_rect.left, self.music_slider_rect.width))
        self.temp_settings["music_volume"] = relative_x / self.music_slider_rect.width
        self.preview_audio_settings()

    def update_sfx_volume(self, mouse_pos):
        relative_x = max(0, min(mouse_pos[0] - self.sfx_slider_rect.left, self.sfx_slider_rect.width))
        self.temp_settings["sfx_volume"] = relative_x / self.sfx_slider_rect.width
        self.preview_audio_settings()

    def preview_audio_settings(self):
        if self.temp_settings["music_enabled"]:
            pygame.mixer.music.set_volume(self.temp_settings["music_volume"])
        else:
            pygame.mixer.music.set_volume(0)

        sfx_volume = self.temp_settings["sfx_volume"] if self.temp_settings["sfx_enabled"] else 0
        for attr_name in dir(self.sound_manager):
            attr = getattr(self.sound_manager, attr_name)
            if isinstance(attr, pygame.mixer.Sound):
                attr.set_volume(sfx_volume)

    def run(self):
        running = True
        result = None
        original_settings = self.settings.copy()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    result = 'back'
                else:
                    event_result = self.handle_events(event)
                    if event_result in ['back', 'apply']:
                        running = False
                        result = event_result
            self.draw()
            pygame.display.flip()
        if result == 'back':
            self.temp_settings = original_settings.copy()
            self.apply_audio_settings()  # Revert audio
        return result
