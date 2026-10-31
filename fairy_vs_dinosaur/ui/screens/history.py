import pandas as pd
import pygame

from fairy_vs_dinosaur.core.history_log import clear_history, load_history
from fairy_vs_dinosaur.ui import theme
from fairy_vs_dinosaur.ui.screens.history_chart import render_comparison_chart
from fairy_vs_dinosaur.ui.screens.history_table import draw_summary_table, table_height
from fairy_vs_dinosaur.ui.theme import body_font, display_font, strong_font
from fairy_vs_dinosaur.ui.widgets import (dimmed_backdrop, draw_close_button, draw_divider, draw_menu_button,
                                          draw_panel, draw_scrollbar, draw_text, draw_title)

TITLE = "ALGORITHM PERFORMANCE HISTORY"
VIEW_TOP = 78
VIEW_BOTTOM_MARGIN = 72
SIDE_MARGIN = 50
PANEL_GAP = 16
PANEL_HEADING_Y = 32
PANEL_HEADING_HEIGHT = 62
EMPTY_PANEL_HEIGHT = 240
SCROLL_STEP = 40
BUTTON_WIDTH = 240
BUTTON_HEIGHT = 46


class HistoryMenu:
    def __init__(self, screen, sound_manager, background):
        self.screen = screen
        self.sound_manager = sound_manager
        self.background = dimmed_backdrop(background)
        self.running = True
        self.timer = pygame.time.Clock()
        self.fps = 60

        self.data = load_history()
        self.df = pd.DataFrame(self.data) if self.data else pd.DataFrame()
        self.chart_image = None
        if not self.df.empty:
            self.generate_chart()

        width, height = self.screen.get_size()
        self.view_rect = pygame.Rect(SIDE_MARGIN, VIEW_TOP, width - 2 * SIDE_MARGIN,
                                     height - VIEW_TOP - VIEW_BOTTOM_MARGIN)

        button_y = height - VIEW_BOTTOM_MARGIN + (VIEW_BOTTOM_MARGIN - BUTTON_HEIGHT) // 2
        self.buttons = [
            {
                "text": "Clear History",
                "rect": pygame.Rect(width // 2 - BUTTON_WIDTH - 12, button_y, BUTTON_WIDTH, BUTTON_HEIGHT),
                "action": self.clear_history,
                "style": 'danger'
            },
            {
                "text": "Back to Menu",
                "rect": pygame.Rect(width // 2 + 12, button_y, BUTTON_WIDTH, BUTTON_HEIGHT),
                "action": self.back,
                "style": 'normal'
            }
        ]

        self.close_rect = pygame.Rect(width - 46, 14, 36, 36)
        self.close_hover = False
        self.hover_states = [False] * len(self.buttons)

        self.scroll_offset = 0
        self.max_scroll = 0
        self.content_height = 0
        self.table_panel_height = 0
        self.chart_panel_height = 0
        self.calculate_content_height()

    def calculate_content_height(self):
        """Tính chiều cao nội dung cuộn, tiêu đề và các nút nằm cố định bên ngoài."""
        if self.df.empty:
            self.table_panel_height = EMPTY_PANEL_HEIGHT
            self.chart_panel_height = 0
            self.content_height = EMPTY_PANEL_HEIGHT
        else:
            self.table_panel_height = table_height(self.df['algorithm'].nunique())
            self.chart_panel_height = 0
            self.content_height = self.table_panel_height
            if self.chart_image:
                self.chart_panel_height = PANEL_HEADING_HEIGHT + self.chart_image.get_height() + 12
                self.content_height += PANEL_GAP + self.chart_panel_height
        self.max_scroll = max(0, self.content_height - self.view_rect.height)
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)

    def clear_history(self):
        self.data = []
        self.df = pd.DataFrame()
        self.chart_image = None
        clear_history()
        self.sound_manager.button_click_sound.play()
        self.calculate_content_height()

    def generate_chart(self):
        if self.df.empty:
            return
        try:
            self.chart_image = render_comparison_chart(self.df)
        except (ValueError, KeyError, TypeError, pygame.error) as e:
            print(f"Error generating chart: {e}")

    def draw_panel(self, y, height, title):
        panel_rect = pygame.Rect(self.view_rect.x, y, self.view_rect.width - 16, height)
        draw_panel(self.screen, panel_rect)
        draw_text(self.screen, title, display_font(25), theme.STONE, midleft=(panel_rect.x + 24, y + PANEL_HEADING_Y))
        return panel_rect

    def draw_table(self):
        y = self.view_rect.y - self.scroll_offset

        if self.df.empty:
            panel = self.draw_panel(y, self.table_panel_height, "Performance Data")
            draw_text(self.screen, "No Algorithm History Available", strong_font(26), theme.PARCHMENT,
                      center=(panel.centerx, panel.centery + 4))
            draw_text(self.screen, "Complete levels using AI algorithms to see performance data here", body_font(19),
                      theme.MIST, center=(panel.centerx, panel.centery + 40))
            return

        panel = self.draw_panel(y, self.table_panel_height, "Algorithm Performance Summary")
        draw_summary_table(self.screen, panel, self.df)

    def draw_chart(self):
        if self.chart_image:
            y = self.view_rect.y - self.scroll_offset + self.table_panel_height + PANEL_GAP
            panel = self.draw_panel(y, self.chart_panel_height, "Performance Visualization")
            self.screen.blit(self.chart_image, self.chart_image.get_rect(midtop=(panel.centerx, y + PANEL_HEADING_HEIGHT)))

    def draw_buttons(self):
        for i, button in enumerate(self.buttons):
            draw_menu_button(self.screen, button["rect"], button["text"], self.hover_states[i], style=button["style"])

    def draw_close_button(self):
        draw_close_button(self.screen, self.close_rect, self.close_hover)

    def update_hover(self, mouse_pos):
        """Cập nhật trạng thái hover"""
        for i, button in enumerate(self.buttons):
            current_hover = button["rect"].collidepoint(mouse_pos)
            if current_hover and not self.hover_states[i]:
                self.sound_manager.button_hover_sound.play()
            self.hover_states[i] = current_hover

        current_close_hover = self.close_rect.collidepoint(mouse_pos)
        if current_close_hover and not self.close_hover:
            self.sound_manager.button_hover_sound.play()
        self.close_hover = current_close_hover

    def _scroll_by(self, amount):
        self.scroll_offset = max(0, min(self.scroll_offset + amount, self.max_scroll))

    def handle_events(self):
        """Xử lý sự kiện"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.back()
                elif event.key == pygame.K_DOWN:
                    self._scroll_by(SCROLL_STEP)
                elif event.key == pygame.K_UP:
                    self._scroll_by(-SCROLL_STEP)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        self.sound_manager.button_click_sound.play()
                        button["action"]()
                        return
                if self.close_rect.collidepoint(mouse_pos):
                    self.sound_manager.button_click_sound.play()
                    self.back()
            elif event.type == pygame.MOUSEWHEEL:
                self._scroll_by(-event.y * SCROLL_STEP)

    def back(self):
        """Quay lại menu chính"""
        self.running = False

    def draw_title(self):
        center_x = self.screen.get_width() // 2
        draw_title(self.screen, TITLE, (center_x, 32), 34, self.screen.get_width() - 160)
        draw_divider(self.screen, (center_x, 62), 420)

    def draw_scroll_bar(self):
        track = pygame.Rect(self.view_rect.right - 6, self.view_rect.y + 4, 6, self.view_rect.height - 8)
        draw_scrollbar(self.screen, track, self.scroll_offset, self.max_scroll,
                       self.view_rect.height / self.content_height)

    def draw_frame(self):
        self.screen.blit(self.background, (0, 0))

        # Bảng và biểu đồ cuộn trong khung, không bao giờ chui xuống dưới tiêu đề hay các nút
        self.screen.set_clip(self.view_rect)
        self.draw_table()
        self.draw_chart()
        self.screen.set_clip(None)

        self.draw_title()
        self.draw_scroll_bar()
        self.draw_buttons()
        self.draw_close_button()

    def run(self):
        """Vòng lặp chính cho history menu"""
        while self.running:
            self.timer.tick(self.fps)
            self.handle_events()
            self.update_hover(pygame.mouse.get_pos())
            self.draw_frame()
            pygame.display.flip()

        return 'back'
