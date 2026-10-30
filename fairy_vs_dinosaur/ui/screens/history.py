import json
import os

import pandas as pd
import pygame

from fairy_vs_dinosaur.config import HISTORY_FILE
from fairy_vs_dinosaur.ui.screens.history_chart import render_comparison_chart
from fairy_vs_dinosaur.ui.screens.history_table import draw_summary_table


class HistoryMenu:
    def __init__(self, screen, sound_manager, background):
        self.screen = screen
        self.sound_manager = sound_manager
        self.background = background
        self.running = True
        self.timer = pygame.time.Clock()
        self.fps = 60

        self.history_file = HISTORY_FILE
        self.data = self.load_history()
        self.df = pd.DataFrame(self.data) if self.data else pd.DataFrame()
        self.chart_image = None
        if not self.df.empty:
            self.generate_chart()

        # Fonts - Adjusted sizes for better readability
        self.title_font = pygame.font.SysFont('segoeui', 42, bold=True)  # Smaller title
        self.header_font = pygame.font.SysFont('segoeui', 28, bold=True)
        self.table_font = pygame.font.SysFont('consolas', 16)  # Smaller for better fit
        self.button_font = pygame.font.SysFont('segoeui', 26, bold=True)
        self.small_font = pygame.font.SysFont('segoeui', 16)
        self.stats_font = pygame.font.SysFont('segoeui', 20, bold=True)

        # Improved colors - better title color
        self.colors = {
            'background': (25, 25, 40, 200),
            'panel': (40, 40, 60, 220),
            'accent': (0, 150, 255),
            'accent_light': (100, 200, 255),
            'text_primary': (255, 255, 255),
            'text_secondary': (200, 200, 220),
            'success': (100, 255, 100),
            'warning': (255, 200, 100),
            'error': (255, 100, 100),
            'header': (60, 60, 80),
            'row_even': (50, 50, 70, 180),
            'row_odd': (45, 45, 65, 180),
            'border': (80, 80, 120),
            'title': (220, 220, 255)  # New color for title - light blue/white
        }

        # Buttons
        button_width = 280
        button_height = 65
        self.buttons = [
            {
                "text": "Clear History",
                "rect": pygame.Rect(self.screen.get_width() // 2 - button_width - 30,
                                    self.screen.get_height() - 90, button_width, button_height),
                "action": self.clear_history,
                "color": (220, 80, 80)
            },
            {
                "text": "Back to Menu",
                "rect": pygame.Rect(self.screen.get_width() // 2 + 30,
                                    self.screen.get_height() - 90, button_width, button_height),
                "action": self.back,
                "color": (80, 160, 255)
            }
        ]

        # Close button
        self.close_rect = pygame.Rect(self.screen.get_width() - 60, 25, 40, 40)
        self.close_hover = False

        # Hover states
        self.hover_states = [False] * len(self.buttons)

        # Scroll for content - fixed title won't be affected
        self.scroll_offset = 0
        self.max_scroll = 0
        self.content_height = 0
        self.table_panel_height = 0
        self.chart_start_y = 0
        self.calculate_content_height()

    def calculate_content_height(self):
        """Calculate content height for scrolling - fixed table height"""
        row_height = 36
        if self.df.empty:
            self.table_panel_height = 200
            self.chart_start_y = 0  # no chart
            self.content_height = 150 + 200 + 100
        else:
            num_algorithms = self.df['algorithm'].nunique()
            table_content_height = (1 + num_algorithms) * row_height
            self.table_panel_height = 70 + table_content_height + 60
            self.chart_start_y = 150 + self.table_panel_height + 20
            self.content_height = self.chart_start_y + 600 if not self.df.empty else 150 + self.table_panel_height + 100
        # Calculate max_scroll based on screen height
        visible_height = self.screen.get_height() - 150  # Adjusted for fixed title
        self.max_scroll = max(0, self.content_height - visible_height)

    def load_history(self):
        """Load history data from JSON file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []

    def clear_history(self):
        """Clear all history data"""
        self.data = []
        self.df = pd.DataFrame()
        self.chart_image = None
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
        except:
            pass
        self.sound_manager.button_click_sound.play()
        self.calculate_content_height()

    def generate_chart(self):
        if self.df.empty:
            return
        try:
            self.chart_image = render_comparison_chart(self.df)
        except (ValueError, KeyError, TypeError, pygame.error) as e:
            print(f"Error generating chart: {e}")

    def draw_panel(self, x, y, width, height, title=None):
        """Vẽ panel với viền và bóng"""
        # Vẽ bóng
        shadow_rect = pygame.Rect(x + 4, y + 4, width, height)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=15)

        # Vẽ nền panel
        panel_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.colors['panel'], panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.colors['border'], panel_rect, width=2, border_radius=12)

        # Vẽ tiêu đề nếu có
        if title:
            title_surface = self.header_font.render(title, True, self.colors['accent_light'])
            title_rect = title_surface.get_rect(midtop=(x + width // 2, y + 15))
            self.screen.blit(title_surface, title_rect)

            # Vẽ đường gạch dưới tiêu đề
            pygame.draw.line(self.screen, self.colors['accent'],
                             (x + 20, y + 55), (x + width - 20, y + 55), 2)

        return panel_rect

    def draw_table(self, y_offset=0):
        """Vẽ bảng dữ liệu với kích thước được cải thiện"""
        actual_y = 150 - y_offset  # Increased starting position for better spacing

        if self.df.empty:
            # Hiển thị thông báo không có dữ liệu
            no_data_panel = self.draw_panel(50, actual_y, self.screen.get_width() - 100, self.table_panel_height, "Performance Data")
            no_data_text = self.header_font.render("No Algorithm History Available", True,
                                                   self.colors['text_secondary'])
            no_data_rect = no_data_text.get_rect(center=no_data_panel.center)
            self.screen.blit(no_data_text, no_data_rect)

            hint_text = self.small_font.render("Complete levels using AI algorithms to see performance data here",
                                               True, self.colors['text_secondary'])
            hint_rect = hint_text.get_rect(center=(no_data_panel.centerx, no_data_panel.centery + 40))
            self.screen.blit(hint_text, hint_rect)
            return

        table_panel = self.draw_panel(50, actual_y, self.screen.get_width() - 100, self.table_panel_height,
                                      "Algorithm Performance Summary")
        draw_summary_table(self.screen, table_panel, self.df, self.table_font, self.stats_font, self.colors)

    def draw_chart(self, y_offset=0):
        """Vẽ biểu đồ với kích thước được cải thiện"""
        if self.chart_image:
            actual_y = self.chart_start_y - y_offset  # Increased spacing from table

            # Panel cho biểu đồ với chiều cao lớn hơn
            chart_panel = self.draw_panel(50, actual_y, self.screen.get_width() - 100, 600, "Performance Visualization")

            # Scale biểu đồ để vừa với panel - giữ tỷ lệ
            chart_width = chart_panel.width - 20
            chart_height = chart_panel.height - 40

            # Calculate aspect ratio to maintain proportions
            aspect_ratio = self.chart_image.get_width() / self.chart_image.get_height()
            if chart_width / aspect_ratio > chart_height:
                chart_width = int(chart_height * aspect_ratio)
            else:
                chart_height = int(chart_width / aspect_ratio)

            scaled_chart = pygame.transform.smoothscale(self.chart_image, (chart_width, chart_height))

            chart_x = chart_panel.x + (chart_panel.width - chart_width) // 2
            chart_y = chart_panel.y + (chart_panel.height - chart_height) // 2

            self.screen.blit(scaled_chart, (chart_x, chart_y))

    def draw_buttons(self):
        """Vẽ các nút với hiệu ứng đẹp"""
        for i, button in enumerate(self.buttons):
            rect = button["rect"]
            hover = self.hover_states[i]
            base_color = button["color"]

            # Màu khi hover
            if hover:
                color = (min(base_color[0] + 30, 255),
                         min(base_color[1] + 30, 255),
                         min(base_color[2] + 30, 255))
                glow_color = (*base_color, 80)
            else:
                color = base_color
                glow_color = (*base_color, 40)

            # Hiệu ứng glow
            if hover:
                glow_rect = rect.inflate(20, 20)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_rect.width, glow_rect.height),
                                 border_radius=15)
                self.screen.blit(glow_surface, glow_rect.topleft)

            # Vẽ nút với gradient
            button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            for y in range(rect.height):
                ratio = y / rect.height
                r = int(color[0] * (0.8 + 0.2 * ratio))
                g = int(color[1] * (0.8 + 0.2 * ratio))
                b = int(color[2] * (0.8 + 0.2 * ratio))
                pygame.draw.line(button_surface, (r, g, b), (0, y), (rect.width, y))

            # Áp dụng border radius
            mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.width, rect.height), border_radius=12)
            button_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            self.screen.blit(button_surface, rect.topleft)

            # Viền nút
            border_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))
            pygame.draw.rect(self.screen, border_color, rect, width=3, border_radius=12)

            # Text với shadow
            text = self.button_font.render(button["text"], True, self.colors['text_primary'])
            shadow_text = self.button_font.render(button["text"], True, (0, 0, 0, 150))

            text_rect = text.get_rect(center=rect.center)
            shadow_rect = shadow_text.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))

            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(text, text_rect)

    def draw_close_button(self):
        """Vẽ nút close đẹp"""
        hover = self.close_hover
        color = (220, 80, 80) if hover else (180, 60, 60)
        glow_color = (220, 80, 80, 80) if hover else (180, 60, 60, 40)

        # Glow effect
        if hover:
            glow_rect = self.close_rect.inflate(10, 10)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_rect.width, glow_rect.height), border_radius=8)
            self.screen.blit(glow_surface, glow_rect.topleft)

        # Button với gradient
        button_surface = pygame.Surface((self.close_rect.width, self.close_rect.height), pygame.SRCALPHA)
        for y in range(self.close_rect.height):
            ratio = y / self.close_rect.height
            r = int(color[0] * (0.7 + 0.3 * ratio))
            g = int(color[1] * (0.7 + 0.3 * ratio))
            b = int(color[2] * (0.7 + 0.3 * ratio))
            pygame.draw.line(button_surface, (r, g, b), (0, y), (self.close_rect.width, y))

        # Border radius
        mask = pygame.Surface((self.close_rect.width, self.close_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, self.close_rect.width, self.close_rect.height),
                         border_radius=8)
        button_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        self.screen.blit(button_surface, self.close_rect.topleft)

        # Viền
        pygame.draw.rect(self.screen, (255, 150, 150), self.close_rect, width=2, border_radius=8)

        # Icon X
        close_font = pygame.font.SysFont('arial', 24, bold=True)
        close_text = close_font.render("×", True, (255, 255, 255))
        text_rect = close_text.get_rect(center=self.close_rect.center)
        self.screen.blit(close_text, text_rect)

    def update_hover(self, mouse_pos):
        """Cập nhật trạng thái hover"""
        # Cập nhật nút
        for i, button in enumerate(self.buttons):
            current_hover = button["rect"].collidepoint(mouse_pos)
            if current_hover and not self.hover_states[i]:
                self.sound_manager.button_hover_sound.play()
            self.hover_states[i] = current_hover

        # Cập nhật nút close
        current_close_hover = self.close_rect.collidepoint(mouse_pos)
        if current_close_hover and not self.close_hover:
            self.sound_manager.button_hover_sound.play()
        self.close_hover = current_close_hover

    def handle_events(self):
        """Xử lý sự kiện"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Kiểm tra click nút
                for i, button in enumerate(self.buttons):
                    if button["rect"].collidepoint(mouse_pos):
                        self.sound_manager.button_click_sound.play()
                        button["action"]()
                        return
                # Kiểm tra nút close
                if self.close_rect.collidepoint(mouse_pos):
                    self.sound_manager.button_click_sound.play()
                    self.back()
            elif event.type == pygame.MOUSEWHEEL:
                # Xử lý scroll cho nội dung - title không bị ảnh hưởng
                if self.max_scroll > 0:
                    self.scroll_offset = max(0, min(self.scroll_offset - event.y * 30, self.max_scroll))

    def back(self):
        """Quay lại menu chính"""
        self.running = False

    def draw_title(self, y_offset=0):
        title_text = self.title_font.render("ALGORITHM PERFORMANCE HISTORY", True,
                                            self.colors['title'])  # New color
        shadow_text = self.title_font.render("ALGORITHM PERFORMANCE HISTORY", True, (0, 0, 0, 100))

        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 60 - y_offset))
        shadow_rect = shadow_text.get_rect(center=(self.screen.get_width() // 2 + 2, 62 - y_offset))

        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)

        # Vẽ đường gạch dưới tiêu đề CỐ ĐỊNH
        pygame.draw.line(self.screen, self.colors['accent'],
                         (self.screen.get_width() // 2 - 200, 95 - y_offset),
                         (self.screen.get_width() // 2 + 200, 95 - y_offset), 3)

    def run(self):
        """Vòng lặp chính cho history menu với title cố định"""
        while self.running:
            self.timer.tick(self.fps)
            self.handle_events()

            # Cập nhật hover
            mouse_pos = pygame.mouse.get_pos()
            self.update_hover(mouse_pos)

            # Vẽ background với overlay tối
            self.screen.blit(self.background, (0, 0))
            overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            # Vẽ các thành phần với scroll offset (chỉ bảng và biểu đồ)
            self.draw_title(self.scroll_offset)
            self.draw_table(self.scroll_offset)
            if not self.df.empty:
                self.draw_chart(self.scroll_offset)

            # Vẽ scroll bar nếu cần
            if self.max_scroll > 0:
                self.draw_scroll_bar()

            # Vẽ nút CỐ ĐỊNH (không bị ảnh hưởng bởi scroll)
            self.draw_buttons()
            self.draw_close_button()

            pygame.display.flip()

        return 'back'

    def draw_scroll_bar(self):
        """Vẽ thanh cuộn"""
        if self.max_scroll == 0:
            return

        bar_width = 10
        bar_x = self.screen.get_width() - 20
        bar_height = 200
        bar_y = 150 + (self.screen.get_height() - 270 - bar_height) * (self.scroll_offset / self.max_scroll)

        # Vẽ track
        track_rect = pygame.Rect(bar_x, 150, bar_width, self.screen.get_height() - 270)
        pygame.draw.rect(self.screen, (60, 60, 80), track_rect, border_radius=5)

        # Vẽ thumb
        thumb_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, self.colors['accent'], thumb_rect, border_radius=5)
