import pygame

from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.settings_store import CONTROL_SCHEMES, LANGUAGES, load_settings, save_settings


class SettingsMenu:
    def __init__(self, screen, sound_manager, background):
        self.screen = screen
        self.sound_manager = sound_manager
        self.background = background
        self.width, self.height = screen.get_size()

        self.settings = load_settings()
        self.sound_manager.apply_settings(self.settings)

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
        self.control_schemes = CONTROL_SCHEMES

        # Language options
        self.languages = LANGUAGES

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

    def apply_settings(self):
        self.settings = self.temp_settings.copy()
        save_settings(self.settings)
        self.sound_manager.apply_settings(self.settings)

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

    def _draw_row_label(self, key, row_rect):
        label = self.option_font.render(get_translation(key), True, self.text_color)
        self.screen.blit(label, label.get_rect(midleft=(self.panel_x + 50, row_rect.centery)))

    def _draw_text_button(self, rect, key, hover):
        pygame.draw.rect(self.screen, self.button_hover_color if hover else self.button_color, rect, border_radius=25)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=25)
        text = self.button_font.render(get_translation(key), True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=rect.center))

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
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            glow_text = self.title_font.render(get_translation("settings"), True, self.highlight_color)
            self.screen.blit(glow_text, title_rect.move(dx, dy))
        self.screen.blit(title_text, title_rect)

        self._draw_row_label("music", self.music_slider_rect)

        music_toggle_rect = self.draw_toggle(self.screen, self.music_toggle_rect, self.temp_settings["music_enabled"])
        music_knob_rect = self.draw_slider(self.screen, self.music_slider_rect,
                                           self.temp_settings["music_volume"],
                                           self.music_slider_hover, self.dragging_music)

        self._draw_row_label("sound_effects", self.sfx_slider_rect)

        sfx_toggle_rect = self.draw_toggle(self.screen, self.sfx_toggle_rect, self.temp_settings["sfx_enabled"])
        sfx_knob_rect = self.draw_slider(self.screen, self.sfx_slider_rect,
                                         self.temp_settings["sfx_volume"],
                                         self.sfx_slider_hover, self.dragging_sfx)

        self._draw_row_label("control_scheme", self.control_selector_rect)

        selected_scheme = self.control_schemes.index(self.temp_settings["control_scheme"])
        control_selector_rect = self.draw_option_selector(self.screen, self.control_selector_rect,
                                                          self.control_schemes, selected_scheme)

        self._draw_row_label("language", self.language_selector_rect)

        selected_lang = self.languages.index(self.temp_settings["language"])
        language_selector_rect = self.draw_option_selector(self.screen, self.language_selector_rect,
                                                           self.languages, selected_lang)

        self._draw_text_button(self.back_button_rect, "back", self.back_hover)
        self._draw_text_button(self.apply_button_rect, "apply", self.apply_hover)

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
                self.sound_manager.apply_settings(self.temp_settings)

            elif ui_elements["sfx_toggle"].collidepoint(mouse_pos):
                self.temp_settings["sfx_enabled"] = not self.temp_settings["sfx_enabled"]
                self.sound_manager.button_click_sound.play()
                self.sound_manager.apply_settings(self.temp_settings)

            elif ui_elements["music_slider"].collidepoint(mouse_pos) or self.music_slider_rect.collidepoint(mouse_pos):
                self.dragging_music = True
                self.update_music_volume(mouse_pos)

            elif ui_elements["sfx_slider"].collidepoint(mouse_pos) or self.sfx_slider_rect.collidepoint(mouse_pos):
                self.dragging_sfx = True
                self.update_sfx_volume(mouse_pos)

            elif ui_elements["control_selector"].collidepoint(mouse_pos):
                self._step_option("control_scheme", self.control_schemes, ui_elements["control_selector"], mouse_pos)

            elif ui_elements["language_selector"].collidepoint(mouse_pos):
                self._step_option("language", self.languages, ui_elements["language_selector"], mouse_pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_music = False
            self.dragging_sfx = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_music:
                self.update_music_volume(mouse_pos)
            if self.dragging_sfx:
                self.update_sfx_volume(mouse_pos)

        return None

    def _step_option(self, key, options, rect, mouse_pos):
        step = -1 if mouse_pos[0] < rect.centerx else 1
        self.temp_settings[key] = options[(options.index(self.temp_settings[key]) + step) % len(options)]
        self.sound_manager.button_click_sound.play()

    def update_music_volume(self, mouse_pos):
        relative_x = max(0, min(mouse_pos[0] - self.music_slider_rect.left, self.music_slider_rect.width))
        self.temp_settings["music_volume"] = relative_x / self.music_slider_rect.width
        self.sound_manager.apply_settings(self.temp_settings)

    def update_sfx_volume(self, mouse_pos):
        relative_x = max(0, min(mouse_pos[0] - self.sfx_slider_rect.left, self.sfx_slider_rect.width))
        self.temp_settings["sfx_volume"] = relative_x / self.sfx_slider_rect.width
        self.sound_manager.apply_settings(self.temp_settings)

    def run(self):
        running = True
        result = None
        original_settings = self.settings.copy()

        clock = pygame.time.Clock()
        while running:
            clock.tick(60)
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
            self.sound_manager.apply_settings(self.settings)  # Hoàn tác phần nghe thử
        return result
