import io
import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import pygame


class HistoryMenu:
    def __init__(self, screen, sound_manager, background, back_callback):
        self.screen = screen
        self.sound_manager = sound_manager
        self.background = background
        self.back_callback = back_callback
        self.running = True
        self.timer = pygame.time.Clock()
        self.fps = 60

        self.history_file = "history.json"
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
        """Generate beautiful and clear comparison chart for algorithms"""
        if self.df.empty:
            return

        try:
            plt.style.use('dark_background')
            # Create a simpler, cleaner chart layout
            fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor='#1a1a2e')
            fig.suptitle('Algorithm Performance', color='white', fontsize=16, fontweight='bold', y=0.95)

            # Group by algorithm and calculate averages
            metrics = ['execution_time', 'expanded_nodes', 'path_length', 'success_rate']
            metric_names = ['Execution Time (s)', 'Expanded Nodes', 'Path Length', 'Success Rate (%)']

            grouped = self.df.groupby('algorithm')[metrics].mean().reset_index()
            algorithms = grouped['algorithm'].tolist()

            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54a0ff']

            for i, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
                ax = axes[i // 2, i % 2]
                bars = ax.bar(algorithms, grouped[metric], color=colors[:len(algorithms)], alpha=0.8)

                ax.set_title(metric_name, color='white', fontweight='bold', fontsize=12)
                ax.set_ylabel(metric_name, color='white', fontsize=10)
                ax.tick_params(axis='x', rotation=45, colors='white', labelsize=9)
                ax.tick_params(axis='y', colors='white', labelsize=9)
                ax.grid(True, alpha=0.3, color='gray')

                # Set background color
                ax.set_facecolor('#2a2a4a')

                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:  # Only label if height is significant
                        if metric == 'success_rate':
                            label = f'{height:.1f}%'
                        elif metric == 'execution_time':
                            label = f'{height:.3f}'
                        else:
                            label = f'{height:.0f}'

                        ax.text(bar.get_x() + bar.get_width() / 2., height,
                                label, ha='center', va='bottom',
                                fontsize=8, color='white', fontweight='bold')

            plt.tight_layout(rect=[0, 0, 1, 0.93])

            # Convert to pygame surface with higher quality
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                        facecolor='#1a1a2e', edgecolor='none')
            buf.seek(0)
            self.chart_image = pygame.image.load(buf)
            plt.close()
        except Exception as e:
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

        try:
            # Vẽ panel cho bảng với chiều cao lớn hơn
            table_panel = self.draw_panel(50, actual_y, self.screen.get_width() - 100, self.table_panel_height,
                                          "Algorithm Performance Summary")

            # Tính toán averages
            metrics = ['execution_time', 'expanded_nodes', 'path_length', 'memory_usage', 'success_rate', 'total_time']
            grouped = self.df.groupby('algorithm')[metrics].mean().reset_index()

            # Vị trí và kích thước bảng - tăng chiều cao
            start_x = table_panel.x + 15
            start_y = table_panel.y + 70
            row_height = 36  # Increased row height
            # Tính toán col_width động dựa trên số cột và chiều rộng màn hình
            num_columns = 7  # ALGORITHM + 6 metrics
            col_width = (table_panel.width - 30) // num_columns

            # Headers với màu gradient
            headers = ['ALGORITHM', 'TIME(s)', 'NODES', 'PATH', 'MEMORY', 'SUCCESS%', 'TOTAL(s)']

            for i, header in enumerate(headers):
                header_bg = pygame.Rect(start_x + i * col_width, start_y, col_width, row_height)

                # Gradient background cho header
                for y_pos in range(row_height):
                    ratio = y_pos / row_height
                    r = int(70 + (40 - 70) * ratio)
                    g = int(130 + (60 - 130) * ratio)
                    b = int(255 + (80 - 255) * ratio)
                    pygame.draw.line(self.screen, (r, g, b),
                                     (header_bg.x, header_bg.y + y_pos),
                                     (header_bg.right, header_bg.y + y_pos))

                pygame.draw.rect(self.screen, self.colors['border'], header_bg, 1)

                header_text = self.table_font.render(header, True, self.colors['text_primary'])
                text_rect = header_text.get_rect(center=header_bg.center)
                self.screen.blit(header_text, text_rect)

            # Dữ liệu với màu xen kẽ
            for row_idx, (_, row) in enumerate(grouped.iterrows()):
                y_pos = start_y + (row_idx + 1) * row_height

                # Màu nền xen kẽ
                row_color = self.colors['row_even'] if row_idx % 2 == 0 else self.colors['row_odd']
                row_rect = pygame.Rect(start_x, y_pos, col_width * len(headers), row_height)
                pygame.draw.rect(self.screen, row_color, row_rect)

                for col_idx, col_name in enumerate(['algorithm'] + metrics):
                    cell_rect = pygame.Rect(start_x + col_idx * col_width, y_pos, col_width, row_height)
                    pygame.draw.rect(self.screen, self.colors['border'], cell_rect, 1)

                    # Định dạng giá trị
                    if col_name == 'algorithm':
                        value = str(row[col_name])
                        color = self.colors['accent_light']
                    elif col_name == 'success_rate':
                        value = f"{row[col_name]:.1f}%"
                        # Màu dựa trên tỷ lệ thành công
                        if row[col_name] >= 80:
                            color = self.colors['success']
                        elif row[col_name] >= 50:
                            color = self.colors['warning']
                        else:
                            color = self.colors['error']
                    elif col_name in ['execution_time', 'total_time']:
                        value = f"{row[col_name]:.3f}"  # More decimal places for time
                        color = self.colors['text_primary']
                    else:
                        value = f"{row[col_name]:.0f}"
                        color = self.colors['text_primary']

                    cell_text = self.table_font.render(value, True, color)
                    text_rect = cell_text.get_rect(center=cell_rect.center)
                    self.screen.blit(cell_text, text_rect)

            # Thống kê tổng quan
            stats_y = table_panel.bottom - 45
            total_games = len(self.df)
            algorithms_used = self.df['algorithm'].nunique()
            best_algorithm = grouped.loc[grouped['success_rate'].idxmax(), 'algorithm']
            best_success = grouped['success_rate'].max()

            stats_texts = [
                f"Games: {total_games}",
                f"Algorithms: {algorithms_used}",
                f"Best: {best_algorithm} ({best_success:.1f}%)"
            ]

            for i, text in enumerate(stats_texts):
                stats_surface = self.stats_font.render(text, True, self.colors['accent_light'])
                self.screen.blit(stats_surface, (start_x + i * 220, stats_y))

        except Exception as e:
            print(f"Error drawing table: {e}")

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
        self.back_callback()

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
