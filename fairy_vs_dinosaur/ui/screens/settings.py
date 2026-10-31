import pygame

from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.settings_store import CONTROL_SCHEMES, LANGUAGES, load_settings, save_settings
from fairy_vs_dinosaur.ui import theme
from fairy_vs_dinosaur.ui.theme import body_font, fit_font, strong_font
from fairy_vs_dinosaur.ui.widgets import (BUTTON_STYLES, chamfered_slab, dimmed_backdrop, draw_divider,
                                          draw_menu_button, draw_panel, draw_slab_button, draw_text, draw_title)

PANEL_WIDTH = 672
PANEL_HEIGHT = 450
PANEL_PADDING = 36
CONTROL_COLUMN = 236  # Lề trái của cột điều khiển, tính từ mép panel
LABEL_WIDTH = CONTROL_COLUMN - PANEL_PADDING - 12
FIRST_ROW = 108
TOGGLE_SIZE = (116, 34)
SLIDER_WIDTH = 212
SLIDER_TRACK_HEIGHT = 8
ACTION_BUTTON_SIZE = (200, 50)


class SettingsMenu:
    def __init__(self, screen, sound_manager, background):
        self.screen = screen
        self.sound_manager = sound_manager
        self.background = dimmed_backdrop(background)
        self.width, self.height = screen.get_size()

        self.settings = load_settings()
        self.sound_manager.apply_settings(self.settings)

        # Control scheme options
        self.control_schemes = CONTROL_SCHEMES

        # Language options
        self.languages = LANGUAGES

        self.panel_rect = pygame.Rect((self.width - PANEL_WIDTH) // 2, (self.height - PANEL_HEIGHT) // 2,
                                      PANEL_WIDTH, PANEL_HEIGHT)
        self.panel_x, self.panel_y = self.panel_rect.topleft

        control_x = self.panel_x + CONTROL_COLUMN
        right_edge = self.panel_rect.right - PANEL_PADDING
        row_y = self.panel_y + FIRST_ROW

        self.music_slider_rect = pygame.Rect(control_x, row_y + 7, SLIDER_WIDTH, 20)
        self.sfx_slider_rect = pygame.Rect(control_x, row_y + 67, SLIDER_WIDTH, 20)
        self.music_toggle_rect = pygame.Rect((right_edge - TOGGLE_SIZE[0], row_y), TOGGLE_SIZE)
        self.sfx_toggle_rect = pygame.Rect((right_edge - TOGGLE_SIZE[0], row_y + 60), TOGGLE_SIZE)
        self.control_selector_rect = pygame.Rect(control_x, row_y + 118, right_edge - control_x, 44)
        self.language_selector_rect = pygame.Rect(control_x, row_y + 178, right_edge - control_x, 44)

        button_y = self.panel_rect.bottom - ACTION_BUTTON_SIZE[1] - 28
        self.back_button_rect = pygame.Rect((self.panel_x + PANEL_PADDING, button_y), ACTION_BUTTON_SIZE)
        self.apply_button_rect = pygame.Rect((right_edge - ACTION_BUTTON_SIZE[0], button_y), ACTION_BUTTON_SIZE)

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
        track = pygame.Rect(rect.left, rect.centery - SLIDER_TRACK_HEIGHT // 2, rect.width, SLIDER_TRACK_HEIGHT)
        pygame.draw.rect(surface, theme.NIGHT, track, border_radius=3)
        fill_width = int(value * rect.width)
        pygame.draw.rect(surface, theme.CRYSTAL, (track.x, track.y, fill_width, track.height), border_radius=3)
        pygame.draw.rect(surface, theme.COPPER_DARK, track, width=1, border_radius=3)

        knob_rect = pygame.Rect(0, 0, 16, 28)
        knob_rect.center = (rect.left + fill_width, rect.centery)
        colors = BUTTON_STYLES['active' if hover or dragging else 'normal']
        fill = colors['edge'] if not (hover or dragging) else colors['fill']
        surface.blit(chamfered_slab(knob_rect.size, fill, colors['edge'], chamfer=4, edge_width=1), knob_rect)

        draw_text(surface, f"{int(value * 100)}%", body_font(18), theme.PARCHMENT,
                  midleft=(rect.right + 14, rect.centery))
        return knob_rect

    def draw_toggle(self, surface, rect, state):
        """Vẽ công tắc: núm ở một đầu, chữ ở phần còn lại để không che nhau"""
        colors = draw_slab_button(surface, rect, 'on' if state else 'off')

        knob_size = rect.height - 12
        knob_x = rect.right - knob_size - 6 if state else rect.left + 6
        knob_rect = pygame.Rect(knob_x, rect.top + 6, knob_size, knob_size)
        pygame.draw.rect(surface, theme.NIGHT if state else theme.MIST, knob_rect, border_radius=3)

        label = get_translation("on") if state else get_translation("off")
        text_area = rect.width - knob_size - 18
        text_x = rect.left + 6 + text_area // 2 if state else knob_rect.right + 3 + text_area // 2
        font = fit_font(strong_font, label, text_area - 4, 17)
        draw_text(surface, label, font, colors['text'], center=(text_x, rect.centery))
        return rect

    def draw_option_selector(self, surface, rect, options, selected_index):
        """Vẽ selector cho các tùy chọn: bấm nửa trái lùi, nửa phải tiến"""
        colors = draw_slab_button(surface, rect, 'normal')
        draw_text(surface, options[selected_index], strong_font(20), colors['text'], center=rect.center)

        mouse_pos = pygame.mouse.get_pos()
        for sign, x in ((-1, rect.left + 22), (1, rect.right - 22)):
            half = rect.left if sign < 0 else rect.centerx
            hover = pygame.Rect(half, rect.top, rect.width // 2, rect.height).collidepoint(mouse_pos)
            color = theme.FLAME if hover else theme.COPPER_LIGHT
            points = [(x - sign * 5, rect.centery - 7), (x + sign * 3, rect.centery), (x - sign * 5, rect.centery + 7)]
            pygame.draw.lines(surface, color, False, points, 3)
        return rect

    def _draw_row_label(self, key, row_rect):
        text = get_translation(key)
        font = fit_font(strong_font, text, LABEL_WIDTH, 21)
        draw_text(self.screen, text, font, theme.PARCHMENT, midleft=(self.panel_x + PANEL_PADDING, row_rect.centery))

    def draw(self):
        """Vẽ toàn bộ giao diện settings"""
        self.screen.blit(self.background, (0, 0))
        draw_panel(self.screen, self.panel_rect)

        center_x = self.panel_rect.centerx
        draw_title(self.screen, get_translation("settings"), (center_x, self.panel_y + 44), 40, PANEL_WIDTH - 60)
        draw_divider(self.screen, (center_x, self.panel_y + 78), 360)

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

        draw_menu_button(self.screen, self.back_button_rect, get_translation("back"), self.back_hover)
        draw_menu_button(self.screen, self.apply_button_rect, get_translation("apply"), self.apply_hover,
                         style='primary')

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

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.sound_manager.button_click_sound.play()
            return 'back'

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
