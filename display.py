import pygame
from pause_menu import *


class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont('monospace', 20, bold=True)
        lives_icon_raw = pygame.image.load("assets/Pac-man/blue/tile003.png").convert_alpha()
        self.lives_icon = pygame.transform.smoothscale(lives_icon_raw, (self.game.pac_w, self.game.pac_h))
        self.hint_hover = False  # Chỉ còn hint_hover
        self.ghost_hover = [False] * 4  # Hover cho 4 nút ghost: Blinky, Pinky, Inky, Clyde
        self.show_blinky = True
        self.show_pinky = True
        self.show_inky = True
        self.show_clyde = True

        self.game_over_screen = False
        self.game_over_selected = 0  # 0: Restart, 1: Main Menu
        self.game_over_hover = [False, False]

        # Font cho game over screen
        self.game_over_font_large = pygame.font.SysFont('monospace', 72, bold=True)
        self.game_over_font_medium = pygame.font.SysFont('monospace', 36, bold=True)
        self.game_over_font_small = pygame.font.SysFont('monospace', 24, bold=True)

        # Hiệu ứng fade
        self.game_over_fade_alpha = 0
        self.game_over_fade_speed = 3

        # Âm thanh cho hover
        self.hover_sound_played = False

        self.pause_menu = PauseMenu(game)
        self.ghost_colors = [
            (255, 0, 0),  # Blinky: red
            (255, 184, 255),  # Pinky: pink
            (0, 255, 255),  # Inky: cyan
            (255, 165, 0)  # Clyde: orange
        ]
        self.ghost_labels = ["B", "P", "I", "C"]

        # Define fixed rects with better spacing
        button_height = self.game.height - self.game.bottom_offset + 10
        button_width = 40
        spacing = 10  # Khoảng cách giữa các nút
        total_ghost_width = 4 * button_width + 3 * spacing
        hint_width = 80
        solve_width = 120
        total_width = total_ghost_width + spacing * 2 + hint_width + solve_width
        start_x = self.game.width // 2 - total_width // 2

        self.ghost_rects = []
        current_x = start_x
        for i in range(4):
            rect = pygame.Rect(current_x, button_height, button_width, 25)
            self.ghost_rects.append(rect)
            current_x += button_width + spacing

        self.hint_rect = pygame.Rect(current_x, button_height, hint_width, 25)
        current_x += hint_width + spacing
        self.solve_rect = pygame.Rect(current_x, button_height, solve_width, 25)

        self.solve_hover = False
        self.solve_menu_visible = False
        self.solve_options = ["BFS", "DFS", "UCS", "ASTAR", "GREEDY", "HILL CLIMBING", "BEAM"]  # Thêm DFS vào danh sách tùy chọn
        self.solve_option_hover = [False] * len(self.solve_options)
        self.solve_option_rects = []

        # Thêm biến để lưu lựa chọn solve
        self.selected_solve = None  # Khi chọn, sẽ set thành "BFS" hoặc tương tự

    def draw_header(self):
        # 1UP
        text_1up = self.font.render(get_translation("1up"), True, (255, 255, 255))
        self.game.screen.blit(text_1up, (self.game.width // 4 - 60, 10))

        # Player score
        score_text = self.font.render(f"{self.game.score:06d}", True, (255, 255, 255))
        self.game.screen.blit(score_text, (self.game.width // 4 - 60, 30))

        # HIGH SCORE
        text_high = self.font.render(get_translation("high_score"), True, (255, 255, 255))
        text_w = text_high.get_width()
        self.game.screen.blit(text_high, (self.game.width // 2 - text_w // 2, 10))

        # High score
        high_score_text = self.font.render(f"{self.game.high_score:06d}", True, (255, 255, 255))
        high_score_text = self.font.render(f"{self.game.high_score:06d}", True, (255, 255, 255))
        high_score_w = high_score_text.get_width()
        self.game.screen.blit(high_score_text, (self.game.width // 2 - high_score_w // 2, 30))

        # TIME
        minutes = int(self.game.play_time // 60000)
        seconds = int((self.game.play_time // 1000) % 60)
        milliseconds = int(self.game.play_time % 1000)
        time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        text_time = self.font.render(get_translation("time"), True, (255, 255, 255))
        time_text = self.font.render(time_str, True, (255, 255, 255))
        self.game.screen.blit(text_time, (3 * self.game.width // 4 - 30, 10))
        self.game.screen.blit(time_text, (3 * self.game.width // 4 - 50, 30))

        self.pause_menu.draw_pause_button(self.game.screen)

    def draw_ready(self):
        if self.game.show_ready:
            ready_text = self.font.render(get_translation("ready"), True, (255, 255, 0))
            text_w, text_h = ready_text.get_size()
            ready_x = self.game.width // 2 - text_w // 2
            ready_y = 18 * self.game.num1_r + self.game.y_offset + self.game.num1_r // 2 - text_h // 2
            self.game.screen.blit(ready_text, (ready_x, ready_y))

    def draw_lives(self):
        # Vị trí mới cho các mạng - cao hơn 20 pixel
        base_y = self.game.height - self.game.bottom_offset - 10

        # Vẽ các mạng chính (trừ mạng hiện tại)
        for i in range(self.game.lives - 1):
            self.game.screen.blit(self.lives_icon, (20 + i * (self.game.pac_w + 5), base_y + 15))

    def draw_hint_button(self):
        # Thay đổi màu sắc dựa trên trạng thái show_hint và hover
        if self.game.show_hint:
            # Khi hint được bật: hiệu ứng vàng sáng với gradient
            gradient_start = (255, 255, 150)  # Vàng sáng
            gradient_end = (255, 165, 0)  # Vàng đậm
            border_color = (255, 255, 100)  # Viền vàng sáng
            text_color = (0, 0, 0)  # Chữ màu đen

            # Vẽ gradient nền với bo góc
            self._draw_gradient_rounded_rect(self.hint_rect, gradient_start, gradient_end, border_radius=10)

            # Hiệu ứng glow nhẹ
            glow_rect = pygame.Rect(self.hint_rect.x - 2, self.hint_rect.y - 2, self.hint_rect.width + 4,
                                    self.hint_rect.height + 4)
            self._draw_rounded_rect_glow(glow_rect, (255, 255, 150, 128), border_radius=12)
        else:
            # Khi hint tắt: màu xanh với gradient
            if self.hint_hover:
                gradient_start = (120, 200, 255)  # Xanh sáng
                gradient_end = (70, 130, 180)  # Xanh đậm
                border_color = (150, 200, 255)  # Viền xanh sáng
                # Glow
                glow_rect = pygame.Rect(self.hint_rect.x - 2, self.hint_rect.y - 2, self.hint_rect.width + 4,
                                        self.hint_rect.height + 4)
                self._draw_rounded_rect_glow(glow_rect, (150, 150, 200, 128), border_radius=12)
            else:
                gradient_start = (70, 130, 180)  # Xanh đậm
                gradient_end = (50, 50, 80)  # Xanh tối
                border_color = (100, 100, 160)  # Viền xanh đậm
            text_color = (255, 255, 255)  # Chữ trắng

            # Vẽ gradient nền với bo góc
            self._draw_gradient_rounded_rect(self.hint_rect, gradient_start, gradient_end, border_radius=10)

        # Vẽ viền với hiệu ứng nổi và bo góc
        self._draw_rounded_border(self.hint_rect, border_color, width=3, border_radius=10)

        # Vẽ chữ với màu phù hợp và căn giữa
        hint_text = self.font.render("HINT", True, text_color)
        text_rect = hint_text.get_rect(center=self.hint_rect.center)
        self.game.screen.blit(hint_text, text_rect)

    def draw_ghost_toggle_buttons(self):
        for i, rect in enumerate(self.ghost_rects):
            show = [self.show_blinky, self.show_pinky, self.show_inky, self.show_clyde][i]
            hover = self.ghost_hover[i]
            color = self.ghost_colors[i]

            if show:
                gradient_start = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))  # Sáng hơn
                gradient_end = color  # Màu gốc
                border_color = (min(255, color[0] + 100), min(255, color[1] + 100), min(255, color[2] + 100))
                text_color = (0, 0, 0) if sum(color) > 400 else (255, 255, 255)
            else:
                gradient_start = (150, 150, 150)
                gradient_end = (100, 100, 100)
                border_color = (200, 200, 200)
                text_color = (255, 255, 255)

            if hover:
                # Glow
                glow_rect = pygame.Rect(rect.x - 3, rect.y - 3, rect.width + 6, rect.height + 6)
                self._draw_rounded_rect_glow(glow_rect, (255, 255, 255, 100), border_radius=10)
                # Làm sáng gradient
                gradient_start = (min(255, gradient_start[0] + 30), min(255, gradient_start[1] + 30),
                                  min(255, gradient_start[2] + 30))
                gradient_end = (min(255, gradient_end[0] + 30), min(255, gradient_end[1] + 30),
                                min(255, gradient_end[2] + 30))

            # Vẽ gradient nền với bo góc
            self._draw_gradient_rounded_rect(rect, gradient_start, gradient_end, border_radius=8)

            # Vẽ viền với bo góc
            self._draw_rounded_border(rect, border_color, width=2, border_radius=8)

            # Vẽ chữ
            label_text = self.font.render(self.ghost_labels[i], True, text_color)
            text_rect = label_text.get_rect(center=rect.center)
            self.game.screen.blit(label_text, text_rect)

    def draw_solve_button(self):
        # Thay đổi màu sắc dựa trên trạng thái menu visible và hover
        if self.solve_menu_visible:
            gradient_start = (255, 230, 100)  # Vàng sáng hơn
            gradient_end = (255, 150, 0)  # Vàng cam đậm
            border_color = (255, 255, 150)  # Viền vàng sáng
            text_color = (0, 0, 0)  # Chữ đen
            # Hiệu ứng glow mạnh hơn
            glow_rect = pygame.Rect(self.solve_rect.x - 3, self.solve_rect.y - 3,
                                    self.solve_rect.width + 6, self.solve_rect.height + 6)
            self._draw_rounded_rect_glow(glow_rect, (255, 220, 50, 180), border_radius=12)
        else:
            if self.solve_hover:
                gradient_start = (140, 210, 255)  # Xanh sáng hơn
                gradient_end = (80, 140, 200)  # Xanh đậm
                border_color = (170, 220, 255)  # Viền xanh sáng
                # Hiệu ứng glow khi hover
                glow_rect = pygame.Rect(self.solve_rect.x - 2, self.solve_rect.y - 2,
                                        self.solve_rect.width + 4, self.solve_rect.height + 4)
                self._draw_rounded_rect_glow(glow_rect, (100, 180, 255, 150), border_radius=12)
            else:
                gradient_start = (80, 140, 200)  # Xanh đậm
                gradient_end = (40, 60, 100)  # Xanh rất đậm
                border_color = (120, 160, 220)  # Viền xanh đậm
            text_color = (255, 255, 255)  # Chữ trắng

        # Vẽ gradient nền với bo góc
        self._draw_gradient_rounded_rect(self.solve_rect, gradient_start, gradient_end, border_radius=10)

        # Vẽ viền với hiệu ứng nổi
        self._draw_rounded_border(self.solve_rect, border_color, width=3, border_radius=10)

        # Vẽ chữ - xử lý chữ dài bằng cách điều chỉnh kích thước font
        text_to_display = "SOLVE"
        if self.selected_solve:
            text_to_display = self.selected_solve.upper()

        # Đảm bảo text_to_display không phải None hoặc rỗng
        if not text_to_display:
            text_to_display = "SOLVE"

        # Kiểm tra độ dài chữ và điều chỉnh font nếu cần - SỬA LỖI NULL POINTER
        try:
            text_width = self.font.size(text_to_display)[0]
            if text_width > self.solve_rect.width - 15:  # Nếu chữ quá dài
                # Sử dụng font nhỏ hơn
                small_font_size = 16
                small_font = pygame.font.SysFont('monospace', small_font_size, bold=True)

                # Kiểm tra tiếp nếu vẫn quá dài - SỬA: sử dụng vòng lặp an toàn
                while small_font_size > 10:  # Giới hạn font size tối thiểu là 10
                    text_width = small_font.size(text_to_display)[0]
                    if text_width <= self.solve_rect.width - 15:
                        break
                    small_font_size -= 1
                    small_font = pygame.font.SysFont('monospace', small_font_size, bold=True)

                solve_text = small_font.render(text_to_display, True, text_color)
            else:
                solve_text = self.font.render(text_to_display, True, text_color)
        except (pygame.error, TypeError) as e:
            # Fallback nếu có lỗi
            print(f"Lỗi khi render chữ: {e}")
            solve_text = self.font.render("SOLVE", True, text_color)

        # Căn giữa chữ
        text_rect = solve_text.get_rect(center=self.solve_rect.center)
        self.game.screen.blit(solve_text, text_rect)

        # Vẽ menu nếu visible
        if self.solve_menu_visible:
            self.solve_option_rects = []
            total_height = len(self.solve_options) * 32

            # Tạo surface cho dropdown menu
            dropdown_surface = pygame.Surface((150, total_height), pygame.SRCALPHA)

            # Vẽ nền dropdown
            self._draw_gradient_rounded_rect_surface(dropdown_surface,
                                                     (60, 80, 120, 240),
                                                     (30, 40, 70, 240),
                                                     pygame.Rect(0, 0, 150, total_height),
                                                     border_radius=8)

            # Vẽ viền dropdown
            pygame.draw.rect(dropdown_surface, (100, 140, 200, 255),
                             pygame.Rect(0, 0, 150, total_height),
                             width=2, border_radius=8)

            # Hiệu ứng shadow cho dropdown
            shadow_surface = pygame.Surface((154, total_height + 4), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 80),
                             pygame.Rect(0, 0, 154, total_height + 4),
                             border_radius=10)
            self.game.screen.blit(shadow_surface,
                                  (self.solve_rect.x - 2, self.solve_rect.y - total_height - 2))

            # Blit dropdown surface
            self.game.screen.blit(dropdown_surface,
                                  (self.solve_rect.x, self.solve_rect.y - total_height))

            for i, option in enumerate(self.solve_options):
                opt_rect = pygame.Rect(self.solve_rect.x, self.solve_rect.y - (i + 1) * 32, 150, 30)
                self.solve_option_rects.append(opt_rect)

                hover = self.solve_option_hover[i]

                # Màu sắc cho option
                if hover:
                    option_color = (100, 160, 220, 200)
                    text_color_opt = (255, 255, 255)
                else:
                    option_color = (80, 120, 180, 200)
                    text_color_opt = (255, 255, 255)

                # Vẽ option background
                option_surface = pygame.Surface((opt_rect.width, opt_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(option_surface, option_color,
                                 pygame.Rect(0, 0, opt_rect.width, opt_rect.height),
                                 border_radius=6)
                self.game.screen.blit(option_surface, opt_rect)

                # Vẽ chữ option - xử lý chữ dài (SỬA TƯƠNG TỰ)
                opt_text = option
                font_to_use = self.font

                try:
                    # Kiểm tra nếu chữ quá dài
                    text_width = font_to_use.size(opt_text)[0]
                    if text_width > opt_rect.width - 15:
                        # Sử dụng font nhỏ hơn
                        small_font_size = 14
                        small_font = pygame.font.SysFont('monospace', small_font_size, bold=True)

                        # Kiểm tra tiếp nếu vẫn quá dài
                        while small_font_size > 8:  # Giới hạn font size tối thiểu là 8
                            text_width = small_font.size(opt_text)[0]
                            if text_width <= opt_rect.width - 15:
                                break
                            small_font_size -= 1
                            small_font = pygame.font.SysFont('monospace', small_font_size, bold=True)

                        font_to_use = small_font
                except (pygame.error, TypeError) as e:
                    print(f"Lỗi khi render option text: {e}")
                    # Giữ nguyên font mặc định nếu có lỗi

                opt_text_surface = font_to_use.render(opt_text, True, text_color_opt)
                text_rect_opt = opt_text_surface.get_rect(center=opt_rect.center)
                self.game.screen.blit(opt_text_surface, text_rect_opt)

    def _draw_gradient_rounded_rect_surface(self, surface, start_color, end_color, rect, border_radius=10):
        """Vẽ gradient rounded rect lên surface có sẵn"""
        # Tạo surface tạm
        temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Vẽ gradient
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            a = int(start_color[3] + (end_color[3] - start_color[3]) * ratio) if len(start_color) > 3 else 255
            pygame.draw.line(temp_surface, (r, g, b, a), (0, y), (rect.width, y))

        # Áp dụng bo góc
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.width, rect.height),
                         border_radius=border_radius)
        temp_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Blit lên surface đích
        surface.blit(temp_surface, (rect.x, rect.y))
    def _draw_gradient_rounded_rect(self, rect, start_color, end_color, border_radius=10):
        """Vẽ hình chữ nhật bo góc với gradient màu"""
        # Tạo một surface tạm thời với kênh alpha
        temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Vẽ gradient lên surface tạm thời
        for y_offset in range(rect.height):
            ratio = y_offset / rect.height
            color = (
                int(start_color[0] + (end_color[0] - start_color[0]) * ratio),
                int(start_color[1] + (end_color[1] - start_color[1]) * ratio),
                int(start_color[2] + (end_color[2] - start_color[2]) * ratio),
                255  # Alpha
            )
            pygame.draw.line(temp_surface, color, (0, y_offset), (rect.width, y_offset))

        # Vẽ hình chữ nhật bo góc lên surface tạm thời để tạo mask
        mask_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, rect.width, rect.height),
                         border_radius=border_radius)

        # Áp dụng mask để bo góc
        temp_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Vẽ lên màn hình chính
        self.game.screen.blit(temp_surface, rect.topleft)

    def _draw_rounded_border(self, rect, color, width=2, border_radius=10):
        """Vẽ viền bo góc"""
        pygame.draw.rect(self.game.screen, color, rect, width=width, border_radius=border_radius)

    def _draw_rounded_rect_glow(self, rect, color, border_radius=10):
        """Vẽ hiệu ứng glow bo góc"""
        temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, color, (0, 0, rect.width, rect.height),
                         border_radius=border_radius)
        self.game.screen.blit(temp_surface, rect.topleft)

    def update_hover(self, mouse_pos):
        # Lưu lại trạng thái hover trước đó
        prev_hint_hover = self.hint_hover
        prev_solve_hover = self.solve_hover
        prev_ghost_hover = self.ghost_hover.copy()
        prev_option_hover = self.solve_option_hover.copy()

        # Cập nhật trạng thái hover mới
        self.hint_hover = self.hint_rect.collidepoint(mouse_pos)
        self.solve_hover = self.solve_rect.collidepoint(mouse_pos)
        self.ghost_hover = [rect.collidepoint(mouse_pos) for rect in self.ghost_rects]

        # Cập nhật hover cho solve options nếu menu visible
        self.solve_option_hover = [False] * len(self.solve_options)
        if self.solve_menu_visible:
            self.solve_option_hover = [rect.collidepoint(mouse_pos) for rect in self.solve_option_rects]

        # Phát âm thanh hover khi trạng thái thay đổi từ không hover sang hover
        if (not prev_hint_hover and self.hint_hover) or \
           (not prev_solve_hover and self.solve_hover):
            self.game.sound_manager.button_hover_sound.play()

        for i in range(4):
            if self.ghost_hover[i] and not prev_ghost_hover[i]:
                self.game.sound_manager.button_hover_sound.play()

        if self.solve_menu_visible:
            for i in range(len(self.solve_options)):
                if self.solve_option_hover[i] and not prev_option_hover[i]:
                    self.game.sound_manager.button_hover_sound.play()

        self.pause_menu.update_hover(mouse_pos)

    def draw_game_over_screen(self):
        """Vẽ màn hình Game Over với thiết kế đẹp hơn"""
        # Gradient overlay thay vì đen thuần (từ đen đến đỏ nhạt)
        overlay = pygame.Surface((self.game.width, self.game.height))
        for y in range(self.game.height):
            color = (int(50 * (y / self.game.height)), 0, 0)  # Gradient từ đen (0,0,0) đến đỏ đậm (50,0,0)
            pygame.draw.line(overlay, color, (0, y), (self.game.width, y))
        overlay.set_alpha(self.game_over_fade_alpha)  # Sử dụng alpha để fade in
        self.game.screen.blit(overlay, (0, 0))

        # Vẽ chữ GAME OVER với glow và shadow
        game_over_text = self.game_over_font_large.render(get_translation("game_over"), True,
                                                          (255, 50, 50))  # Màu đỏ sáng
        text_rect = game_over_text.get_rect(center=(self.game.width // 2, self.game.height // 3 - 20))

        # Shadow đậm hơn
        shadow_text = self.game_over_font_large.render(get_translation("game_over"), True, (100, 0, 0))
        self.game.screen.blit(shadow_text, (text_rect.x + 4, text_rect.y + 4))

        # Glow nhẹ (vẽ nhiều lớp mờ)
        glow_color = (255, 150, 150, 100)  # Đỏ nhạt mờ
        glow_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 20), pygame.SRCALPHA)
        glow_surface.blit(game_over_text, (10, 10))
        glow_surface = pygame.transform.smoothscale(glow_surface, (text_rect.width + 40, text_rect.height + 40))
        glow_surface.set_alpha(50)
        self.game.screen.blit(glow_surface, (text_rect.x - 20, text_rect.y - 20))
        self.game.screen.blit(game_over_text, text_rect)

        # Thêm hiển thị score cuối cùng
        score_text = self.game_over_font_small.render(f"{get_translation('final_score')}: {self.game.score:06d}", True,
                                                      (255, 255, 100))
        score_rect = score_text.get_rect(center=(self.game.width // 2, text_rect.bottom + 20))
        self.game.screen.blit(score_text, score_rect)

        # Vẽ các tùy chọn chính với nút đẹp hơn
        options = [get_translation("restart"), get_translation("main_menu")]
        for i, option in enumerate(options):
            text = self.game_over_font_medium.render(option, True, (255, 255, 255))
            button_rect = pygame.Rect(self.game.width // 2 - 120, self.game.height // 2 + i * 70 - 20, 240, 50)

            # Kiểm tra hover cho các nút game over
            is_hover = self.game_over_hover[i]

            # Nền nút với gradient
            if i == self.game_over_selected or is_hover:
                gradient_start = (255, 200, 0)  # Vàng sáng
                gradient_end = (200, 100, 0)  # Vàng đậm
                border_color = (255, 255, 100)  # Viền vàng

                # Hiệu ứng glow khi hover
                if is_hover:
                    glow_rect = pygame.Rect(button_rect.x - 4, button_rect.y - 4, button_rect.width + 8,
                                            button_rect.height + 8)
                    self._draw_rounded_rect_glow(glow_rect, (255, 255, 150, 100), border_radius=12)
            else:
                gradient_start = (100, 100, 100)  # Xám sáng
                gradient_end = (50, 50, 50)  # Xám đậm
                border_color = (150, 150, 150)  # Viền xám

            # Vẽ gradient nền với bo góc
            self._draw_gradient_rounded_rect(button_rect, gradient_start, gradient_end, border_radius=10)

            # Vẽ viền với shadow
            shadow_rect = pygame.Rect(button_rect.x + 2, button_rect.y + 2, button_rect.width, button_rect.height)
            self._draw_rounded_border(shadow_rect, (0, 0, 0, 100), width=3, border_radius=10)  # Shadow
            self._draw_rounded_border(button_rect, border_color, width=3, border_radius=10)

            # Chữ căn giữa
            text_rect = text.get_rect(center=button_rect.center)
            self.game.screen.blit(text, text_rect)

            # Mũi tên cho selected
            if i == self.game_over_selected:
                arrow_text = self.game_over_font_medium.render(">", True, (255, 255, 0))
                self.game.screen.blit(arrow_text, (button_rect.x - 40, text_rect.y))
                self.game.screen.blit(arrow_text, (button_rect.right + 10, text_rect.y))

    def update_game_over_hover(self, mouse_pos):
        options_rects = [
            pygame.Rect(self.game.width // 2 - 120, self.game.height // 2 - 20, 240, 50),  # RESTART
            pygame.Rect(self.game.width // 2 - 120, self.game.height // 2 + 50, 240, 50)  # MAIN MENU
        ]
        prev_hover = self.game_over_hover.copy()
        self.game_over_hover = [rect.collidepoint(mouse_pos) for rect in options_rects]
        for i in range(2):
            if self.game_over_hover[i] and not prev_hover[i]:
                self.game.sound_manager.button_hover_sound.play()
            if self.game_over_hover[i]:
                self.game_over_selected = i

    def handle_game_over_events(self, event):
        """Xử lý sự kiện cho màn hình Game Over"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s]:
                # Xử lý điều hướng bằng phím mũi tên hoặc WASD
                prev_selected = self.game_over_selected
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.game_over_selected = (self.game_over_selected - 1) % 2
                else:  # DOWN hoặc S
                    self.game_over_selected = (self.game_over_selected + 1) % 2

                # Phát âm thanh hover khi thay đổi lựa chọn
                if prev_selected != self.game_over_selected:
                    self.game.sound_manager.button_hover_sound.play()

            elif event.key == pygame.K_RETURN:
                self.game.sound_manager.button_click_sound.play()
                if self.game_over_selected == 0:  # Restart
                    self.game.sound_manager.game_over_channel.stop()
                    self.game.restart_game()
                else:  # Main Menu
                    # SỬA: Chỉ thiết lập return_code, không gọi return_to_main_menu trực tiếp
                    self.game.sound_manager.game_over_channel.stop()
                    self.game.return_code = 'menu'
                    self.game.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            options_rects = [
                pygame.Rect(self.game.width // 2 - 120, self.game.height // 2 - 20, 240, 50),  # RESTART
                pygame.Rect(self.game.width // 2 - 120, self.game.height // 2 + 50, 240, 50)  # MAIN MENU
            ]
            for i, rect in enumerate(options_rects):
                if rect.collidepoint(mouse_pos):
                    self.game.sound_manager.button_click_sound.play()
                    if i == 0:  # Restart
                        self.game.sound_manager.game_over_channel.stop()
                        self.game.restart_game()
                    else:  # Main Menu
                        # SỬA: Chỉ thiết lập return_code, không gọi return_to_main_menu trực tiếp
                        self.game.sound_manager.game_over_channel.stop()
                        self.game.return_code = 'menu'
                        self.game.running = False
                    break

    def update_game_over_fade(self, dt):
        if self.game_over_screen and self.game_over_fade_alpha < 200:  # Fade in đến 200 để không quá tối
            self.game_over_fade_alpha = min(200,
                                            self.game_over_fade_alpha + self.game_over_fade_speed * 2)  # Tăng tốc fade in