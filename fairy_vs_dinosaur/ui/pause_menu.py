import pygame

from fairy_vs_dinosaur.i18n import get_translation


class PauseMenu:
    def __init__(self, game):
        self.game = game
        self.width = 420
        self.height = 400  # Tăng chiều cao để chứa thanh tiến độ
        self.x = (game.width - self.width) // 2
        self.y = (game.height - self.height) // 2
        self.visible = False

        # Fonts
        self.title_font = pygame.font.SysFont('monospace', 50, bold=True)
        self.button_font = pygame.font.SysFont('monospace', 34, bold=True)
        self.small_font = pygame.font.SysFont('monospace', 20, bold=True)
        self.progress_font = pygame.font.SysFont('monospace', 16, bold=True)

        # Button definitions
        self.buttons = [
            {"text": get_translation("resume"), "action": self.resume_game},
            {"text": get_translation("restart"), "action": self.confirm_restart},
            {"text": get_translation("main_menu"), "action": self.confirm_main_menu}
        ]
        self.button_height = 55
        self.button_width = 220
        self.button_margin = 25

        # States
        self.selected_index = 0
        self.hover_states = [False] * len(self.buttons)
        self.prev_hover_states = [False] * len(self.buttons)
        self.pause_button_hover = False
        self.prev_pause_button_hover = False
        self.background_surface = None

        # Pause button
        self.pause_button_rect = pygame.Rect(self.game.width - 50, 10, 40, 40)

        # Confirm dialog
        self.show_confirm = False
        self.confirm_selected = 0
        self.confirm_action = None
        self.confirm_hover = [False, False]
        self.prev_confirm_hover = [False, False]

        # Load hình nàng tiên cho thanh tiến độ
        try:
            fairy_raw = pygame.image.load("assets/Pac-man/blue/tile003.png").convert_alpha()
            self.fairy_icon = pygame.transform.smoothscale(fairy_raw, (30, 30))
        except:
            print("Không thể load hình nàng tiên. Sử dụng hình tròn thay thế.")
            self.fairy_icon = None

    def draw_pause_button(self, screen):
        """Vẽ nút pause nhỏ ở góc phải"""
        colors = self._get_pause_button_colors()

        # Vẽ shadow cho nút
        shadow_rect = self.pause_button_rect.copy().move(2, 2)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)

        # Tạo button surface với alpha
        button_surface = pygame.Surface((self.pause_button_rect.width, self.pause_button_rect.height), pygame.SRCALPHA)

        # Vẽ gradient line by line
        height = button_surface.get_height()
        width = button_surface.get_width()
        for y in range(height):
            ratio = y / height
            color = (
                int(colors['bg'][0] * (1 - ratio) + colors['bg_dark'][0] * ratio),
                int(colors['bg'][1] * (1 - ratio) + colors['bg_dark'][1] * ratio),
                int(colors['bg'][2] * (1 - ratio) + colors['bg_dark'][2] * ratio)
            )
            pygame.draw.line(button_surface, color, (0, y), (width, y))

        # Tạo mask bo góc
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, width, height), border_radius=10)

        # Áp mask lên button_surface
        button_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        # Blit button_surface lên screen
        screen.blit(button_surface, self.pause_button_rect.topleft)

        # Vẽ border bo góc
        pygame.draw.rect(screen, colors['border'], self.pause_button_rect, width=3, border_radius=10)

        # Vẽ biểu tượng pause
        self._draw_pause_icon(screen)

        return self.pause_button_rect

    def _get_pause_button_colors(self):
        """Lấy màu sắc cho nút pause dựa trên trạng thái hover"""
        if self.pause_button_hover:
            return {
                'bg': (255, 215, 0),
                'bg_dark': (235, 195, 0),
                'border': (255, 255, 150)
            }
        else:
            return {
                'bg': (80, 80, 140),
                'bg_dark': (60, 60, 120),
                'border': (100, 160, 200)
            }

    def _draw_pause_icon(self, screen):
        """Vẽ biểu tượng pause (hai gạch dọc)"""
        bar_width = 6
        bar_height = 22
        bar_spacing = 5

        left_bar_x = self.pause_button_rect.centerx - bar_width - bar_spacing // 2
        right_bar_x = self.pause_button_rect.centerx + bar_spacing // 2
        bar_y = self.pause_button_rect.centery - bar_height // 2

        # Shadow
        pygame.draw.rect(screen, (50, 50, 50, 100), (left_bar_x + 1, bar_y + 1, bar_width, bar_height))
        pygame.draw.rect(screen, (50, 50, 50, 100), (right_bar_x + 1, bar_y + 1, bar_width, bar_height))

        # Bars chính
        pygame.draw.rect(screen, (255, 255, 255), (left_bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (right_bar_x, bar_y, bar_width, bar_height))

    def draw(self, screen):
        """Vẽ toàn bộ menu pause"""
        if not self.visible:
            self.draw_pause_button(screen)
            return

        # Vẽ nền mờ
        self._draw_blur_background(screen)

        # Vẽ menu chính
        self._draw_main_menu(screen)

        # Vẽ confirm dialog nếu cần
        if self.show_confirm:
            self._draw_confirm_dialog(screen)

    def _draw_blur_background(self, screen):
        """Vẽ nền mờ cho menu pause"""
        if self.background_surface is None:
            self.background_surface = screen.copy()
            darken = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
            for i in range(self.game.height):
                alpha = 150 + (i / self.game.height) * 50
                pygame.draw.line(darken, (0, 0, 0, int(alpha)), (0, i), (self.game.width, i))
            self.background_surface.blit(darken, (0, 0))

        screen.blit(self.background_surface, (0, 0))

    def _draw_main_menu(self, screen):
        """Vẽ menu pause chính"""
        # Vẽ nền menu
        menu_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self._draw_menu_background(screen, menu_rect)

        # Vẽ tiêu đề
        self._draw_menu_title(screen)

        # Vẽ thanh tiến độ
        self._draw_progress_bar(screen)

        # Vẽ các nút
        self._draw_menu_buttons(screen)

    def _draw_progress_bar(self, screen):
        """Vẽ thanh tiến độ phần trăm hoàn thành trong pause menu"""
        # Tính toán phần trăm hoàn thành
        if hasattr(self.game.level, 'initial_pellets') and self.game.level.initial_pellets > 0:
            total_pellets = self.game.level.initial_pellets
            collected_pellets = total_pellets - self.game.level.remaining_pellets
            percent_complete = collected_pellets / total_pellets
        else:
            # Fallback nếu không có dữ liệu
            total_pellets = 1
            collected_pellets = 0
            percent_complete = 0

        # Vị trí và kích thước thanh tiến độ trong pause menu
        bar_width = 340
        bar_height = 25
        bar_x = self.x + (self.width - bar_width) // 2
        bar_y = self.y + 100  # Dưới tiêu đề

        # Vẽ nền thanh tiến độ - MÀU MỚI: xanh đậm
        pygame.draw.rect(screen, (30, 30, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=12)

        # Vẽ phần đã hoàn thành với bo góc
        if percent_complete > 0:
            completed_width = max(12, int(bar_width * percent_complete))  # Đảm bảo tối thiểu để bo góc

            # Tạo surface cho phần đã hoàn thành với bo góc
            completed_surface = pygame.Surface((completed_width, bar_height), pygame.SRCALPHA)

            # Gradient màu mới: từ tím nhạt đến hồng
            for i in range(completed_width):
                ratio = i / completed_width if completed_width > 0 else 0
                # Màu gradient: từ #8A2BE2 (blue violet) đến #FF69B4 (hot pink)
                color = (
                    int(138 + (255 - 138) * ratio),  # R: 138 -> 255
                    int(43 + (105 - 43) * ratio),  # G: 43 -> 105
                    int(226 + (180 - 226) * ratio)  # B: 226 -> 180
                )
                pygame.draw.rect(completed_surface, color, (i, 0, 1, bar_height))

            # Tạo mask bo góc
            mask = pygame.Surface((completed_width, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, completed_width, bar_height), border_radius=12)
            completed_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            # Vẽ phần đã hoàn thành lên màn hình
            screen.blit(completed_surface, (bar_x, bar_y))

        # Vẽ viền thanh tiến độ - MÀU MỚI: tím sáng
        pygame.draw.rect(screen, (147, 112, 219), (bar_x, bar_y, bar_width, bar_height), width=2, border_radius=12)

        # Vẽ hình nàng tiên ở đầu thanh tiến độ
        fairy_x = bar_x + int(bar_width * percent_complete) - 15
        fairy_y = bar_y - 10

        # Hiệu ứng glow cho nàng tiên - MÀU MỚI: hồng
        glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        for r in range(8, 0, -2):
            alpha = 30 - r * 3
            pygame.draw.circle(glow_surface, (255, 105, 180, alpha), (20, 20), 15 + r)
        screen.blit(glow_surface, (fairy_x - 5, fairy_y - 5))

        # Vẽ nàng tiên
        if self.fairy_icon:
            screen.blit(self.fairy_icon, (fairy_x, fairy_y))
        else:
            # Fallback: vẽ hình tròn màu vàng
            pygame.draw.circle(screen, (255, 255, 0), (fairy_x + 15, fairy_y + 15), 12)

        # Vẽ phần trăm text - MÀU MỚI: trắng sáng với viền đen để dễ đọc
        percent_text = f"{percent_complete * 100:.1f}%"
        text_surface = self.progress_font.render(percent_text, True, (255, 255, 255))  # Màu trắng
        # Vẽ viền đen cho chữ
        border_surface = self.progress_font.render(percent_text, True, (0, 0, 0))
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    screen.blit(border_surface, (bar_x + bar_width - text_surface.get_width() - 5 + dx,
                                                 bar_y + (bar_height - text_surface.get_height()) // 2 + dy))
        # Đặt text bên trong thanh, góc trên bên phải
        text_x = bar_x + bar_width - text_surface.get_width() - 5
        text_y = bar_y + (bar_height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

        # Vẽ số pellet đã thu thập - MÀU MỚI: xanh lá sáng với viền đen
        count_text = f"{collected_pellets}/{total_pellets}"
        count_surface = self.progress_font.render(count_text, True, (144, 238, 144))  # Màu xanh lá sáng
        # Vẽ viền đen cho chữ
        count_border = self.progress_font.render(count_text, True, (0, 0, 0))
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    screen.blit(count_border,
                                (bar_x + 5 + dx, bar_y + (bar_height - count_surface.get_height()) // 2 + dy))
        # Đặt text bên trong thanh, góc trên bên trái
        count_x = bar_x + 5
        count_y = bar_y + (bar_height - count_surface.get_height()) // 2
        screen.blit(count_surface, (count_x, count_y))

        # Vẽ tiêu đề cho thanh tiến độ - MÀU MỚI: vàng cam với viền đen
        progress_title = "PROGRESS"
        title_surface = self.progress_font.render(progress_title, True, (255, 165, 0))  # Màu cam
        # Vẽ viền đen cho chữ
        title_border = self.progress_font.render(progress_title, True, (0, 0, 0))
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    screen.blit(title_border, (bar_x + dx, bar_y - 25 + dy))
        title_x = bar_x
        title_y = bar_y - 25
        screen.blit(title_surface, (title_x, title_y))

    def _draw_menu_background(self, screen, menu_rect):
        """Vẽ nền cho menu"""
        gradient_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(gradient_surface, (40, 40, 80, 220), (0, 0, self.width, self.height), border_radius=25)

        for i in range(self.height):
            color = (30 + i // 10, 30 + i // 10, 60 + i // 5)
            pygame.draw.line(gradient_surface, color, (0, i), (self.width, i))

        screen.blit(gradient_surface, (self.x, self.y))

        # Vẽ border
        border_rect = menu_rect.inflate(4, 4)
        pygame.draw.rect(screen, (100, 150, 220, 150), border_rect, width=5, border_radius=25)
        pygame.draw.rect(screen, (80, 140, 200), menu_rect, width=4, border_radius=25)

    def _draw_menu_title(self, screen):
        """Vẽ tiêu đề menu"""
        title_text = self.title_font.render(get_translation("paused"), True, (255, 255, 100))
        shadow_text = self.title_font.render(get_translation("paused"), True, (100, 100, 0))
        title_rect = title_text.get_rect(center=(self.game.width // 2, self.y + 40))
        shadow_rect = shadow_text.get_rect(center=(title_rect.centerx + 2, title_rect.centery + 2))

        screen.blit(shadow_text, shadow_rect)
        screen.blit(title_text, title_rect)

    def _draw_menu_buttons(self, screen):
        """Vẽ các nút trong menu - căn giữa chính xác"""
        # Tính toán vị trí các nút
        total_buttons_height = len(self.buttons) * self.button_height + (len(self.buttons) - 1) * self.button_margin
        start_y = self.y + 150  # Bắt đầu từ dưới thanh tiến độ

        for i, button in enumerate(self.buttons):
            button_rect = pygame.Rect(
                self.game.width // 2 - self.button_width // 2,
                start_y + i * (self.button_height + self.button_margin),
                self.button_width,
                self.button_height
            )
            self._draw_menu_button(screen, button_rect, button["text"], i)

    def _draw_menu_button(self, screen, rect, text, index):
        """Vẽ một nút trong menu"""
        is_hovered = self.hover_states[index]
        is_selected = (index == self.selected_index)
        colors = self._get_button_colors(is_hovered or is_selected)

        # Hiệu ứng glow
        if is_hovered or is_selected:
            glow_rect = rect.inflate(12, 12)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 200, 100, 80), (0, 0, glow_rect.width, glow_rect.height),
                             border_radius=15)
            screen.blit(glow_surface, glow_rect.topleft)

        # Vẽ nút với gradient
        button_surface = pygame.Surface((self.button_width, self.button_height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, colors['bg'], (0, 0, self.button_width, self.button_height), border_radius=12)
        pygame.draw.rect(button_surface, colors['bg_dark'],
                         (0, self.button_height // 2, self.button_width, self.button_height // 2), border_radius=12)
        screen.blit(button_surface, rect.topleft)

        # Vẽ border
        pygame.draw.rect(screen, colors['border'], rect, width=3, border_radius=12)

        # Vẽ chữ
        text_surface = self.button_font.render(text, True, colors['text'])
        shadow_surface = self.button_font.render(text, True, colors['shadow'])
        shadow_surface.set_alpha(colors['shadow_alpha'])

        text_rect = text_surface.get_rect(center=rect.center)
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))

        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

    def _get_button_colors(self, is_highlighted):
        """Lấy màu sắc cho nút dựa trên trạng thái"""
        if is_highlighted:
            return {
                'bg': (240, 180, 60),
                'bg_dark': (210, 150, 30),
                'border': (255, 230, 120),
                'text': (20, 20, 20),
                'shadow': (0, 0, 0),
                'shadow_alpha': 100
            }
        else:
            return {
                'bg': (60, 120, 200),
                'bg_dark': (30, 90, 170),
                'border': (100, 160, 240),
                'text': (240, 240, 240),
                'shadow': (255, 255, 255),
                'shadow_alpha': 50
            }

    def _draw_confirm_dialog(self, screen):
        """Vẽ hộp thoại xác nhận"""
        dialog_bg = pygame.Rect(self.game.width // 4, self.game.height // 2 - 80, self.game.width // 2, 160)

        # Nền dialog
        for y in range(dialog_bg.height):
            ratio = y / dialog_bg.height
            color = (
                int(40 + (80 - 40) * ratio),
                int(40 + (80 - 40) * ratio),
                int(80 + (120 - 80) * ratio)
            )
            pygame.draw.line(screen, color, (dialog_bg.x, dialog_bg.y + y), (dialog_bg.right, dialog_bg.y + y))

        # Viền
        pygame.draw.rect(screen, (150, 150, 255), dialog_bg.inflate(4, 4), width=3, border_radius=20)
        pygame.draw.rect(screen, (100, 100, 200), dialog_bg, width=3, border_radius=15)

        # Câu hỏi
        question = "Restart the game? Progress will not be saved." if self.confirm_action == 1 else "Return to main menu? Progress will not be saved."
        lines = self._wrap_text(question, self.small_font, dialog_bg.width - 40)
        y = dialog_bg.y + 20
        for line in lines:
            text_surface = self.small_font.render(line, True, (255, 255, 255))
            rect = text_surface.get_rect(centerx=self.game.width // 2, top=y)
            screen.blit(text_surface, rect)
            y += text_surface.get_height() + 5

        # Các nút Yes/No
        confirm_options = [get_translation("yes"), get_translation("no")]
        button_y = dialog_bg.y + 100

        for i, option in enumerate(confirm_options):
            x_pos = self.game.width // 2 - 80 + i * 160
            button_rect = pygame.Rect(x_pos - 50, button_y, 100, 40)

            is_hovered = self.confirm_hover[i]
            is_selected = (i == self.confirm_selected)
            is_highlighted = is_hovered or is_selected
            is_yes = (i == 0)
            colors = self._get_confirm_button_colors(is_highlighted, is_yes)

            # Hiệu ứng glow với màu phù hợp
            if is_highlighted:
                glow_color = (150, 255, 150) if is_yes else (255, 150, 150)
                glow_rect = button_rect.inflate(6, 6)
                pygame.draw.rect(screen, glow_color, glow_rect, border_radius=10)

            # Vẽ nút
            pygame.draw.rect(screen, colors['bg'], button_rect, border_radius=8)
            pygame.draw.rect(screen, colors['border'], button_rect, width=2, border_radius=8)

            # Vẽ chữ
            text_surface = self.button_font.render(option, True, colors['text'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)

    def _wrap_text(self, text, font, max_width):
        """Wrap text để vừa chiều rộng"""
        lines = []
        words = text.split(' ')
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            width, _ = font.size(test_line)
            if width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _get_confirm_button_colors(self, is_highlighted, is_yes):
        """Lấy màu sắc cho nút xác nhận, tùy theo Yes/No và trạng thái highlight"""
        if is_yes:
            if is_highlighted:
                return {
                    'bg': (0, 200, 0),  # Xanh sáng hơn
                    'border': (100, 255, 100),
                    'text': (0, 0, 0)
                }
            else:
                return {
                    'bg': (0, 150, 0),  # Xanh đậm
                    'border': (50, 200, 50),
                    'text': (255, 255, 255)
                }
        else:  # No
            if is_highlighted:
                return {
                    'bg': (200, 0, 0),  # Đỏ sáng hơn
                    'border': (255, 100, 100),
                    'text': (0, 0, 0)
                }
            else:
                return {
                    'bg': (150, 0, 0),  # Đỏ đậm
                    'border': (200, 50, 50),
                    'text': (255, 255, 255)
                }

    def update_hover(self, mouse_pos):
        """Cập nhật trạng thái hover"""
        # Cập nhật nút pause nhỏ
        current_pause_hover = self.pause_button_rect.collidepoint(mouse_pos)
        if current_pause_hover and not self.prev_pause_button_hover:
            self.game.sound_manager.button_hover_sound.play()
        self.pause_button_hover = current_pause_hover
        self.prev_pause_button_hover = current_pause_hover

        if self.visible:
            if self.show_confirm:
                self._update_confirm_hover(mouse_pos)
            else:
                self._update_menu_hover(mouse_pos)

    def _update_menu_hover(self, mouse_pos):
        """Cập nhật hover cho menu chính - ĐÃ SỬA"""
        # Reset hover states
        for i in range(len(self.buttons)):
            self.hover_states[i] = False

        # Tính toán vị trí các nút (giống như trong _draw_menu_buttons)
        total_buttons_height = len(self.buttons) * self.button_height + (len(self.buttons) - 1) * self.button_margin
        start_y = self.y + 150  # Bắt đầu từ dưới thanh tiến độ

        # Cập nhật hover state cho từng nút
        for i in range(len(self.buttons)):
            button_rect = pygame.Rect(
                self.game.width // 2 - self.button_width // 2,
                start_y + i * (self.button_height + self.button_margin),
                self.button_width,
                self.button_height
            )

            current_hover = button_rect.collidepoint(mouse_pos)

            # Phát âm thanh hover khi di chuột vào nút
            if current_hover and not self.prev_hover_states[i]:
                self.game.sound_manager.button_hover_sound.play()

            self.hover_states[i] = current_hover
            self.prev_hover_states[i] = current_hover

            # Cập nhật selected_index khi hover
            if current_hover:
                self.selected_index = i

    def _update_confirm_hover(self, mouse_pos):
        """Cập nhật hover cho confirm dialog"""
        # Sử dụng cùng vị trí với _draw_confirm_dialog
        button_y = self.game.height // 2 + 20
        yes_rect = pygame.Rect(self.game.width // 2 - 130, button_y, 100, 40)
        no_rect = pygame.Rect(self.game.width // 2 + 30, button_y, 100, 40)

        new_hover = [yes_rect.collidepoint(mouse_pos), no_rect.collidepoint(mouse_pos)]

        for i in range(2):
            if new_hover[i] and not self.prev_confirm_hover[i]:
                self.game.sound_manager.button_hover_sound.play()
                self.confirm_selected = i
            self.prev_confirm_hover[i] = new_hover[i]

        self.confirm_hover = new_hover

    def handle_events(self, event):
        """Xử lý sự kiện"""
        if event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_click(event)

        return False

    def _handle_keydown(self, event):
        """Xử lý sự kiện bàn phím"""
        if event.key == pygame.K_ESCAPE:
            return self._handle_escape()

        if not self.visible:
            return False

        if self.show_confirm:
            return self._handle_confirm_keydown(event)
        else:
            return self._handle_menu_keydown(event)

    def _handle_escape(self):
        """Xử lý phím ESC"""
        if self.visible:
            if self.show_confirm:
                self.show_confirm = False
                return True
            else:
                self.resume_game()
                return True
        else:
            self.pause_game()
            return True

    def _handle_confirm_keydown(self, event):
        """Xử lý phím trong confirm dialog"""
        if event.key == pygame.K_LEFT:
            self.confirm_selected = 0
            self.game.sound_manager.button_hover_sound.play()
            return True
        elif event.key == pygame.K_RIGHT:
            self.confirm_selected = 1
            self.game.sound_manager.button_hover_sound.play()
            return True
        elif event.key == pygame.K_RETURN:
            return self._execute_confirm_action()

        return False

    def _handle_menu_keydown(self, event):
        """Xử lý phím trong menu chính"""
        if event.key in [pygame.K_UP, pygame.K_w]:
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
            self.game.sound_manager.button_hover_sound.play()
            return True
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            self.game.sound_manager.button_hover_sound.play()
            return True
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.game.sound_manager.button_click_sound.play()
            self.buttons[self.selected_index]["action"]()
            return True

        return False

    def _handle_mouse_click(self, event):
        """Xử lý click chuột"""
        mouse_pos = pygame.mouse.get_pos()

        if not self.visible:
            # Kiểm tra click nút pause nhỏ
            if self.pause_button_rect.collidepoint(mouse_pos):
                self.pause_game()
                return True
            return False

        if self.show_confirm:
            return self._handle_confirm_click(mouse_pos)
        else:
            return self._handle_menu_click(mouse_pos)

    def _handle_confirm_click(self, mouse_pos):
        """Xử lý click trong confirm dialog"""
        # Sử dụng cùng vị trí với _draw_confirm_dialog và _update_confirm_hover
        button_y = self.game.height // 2 + 20
        yes_rect = pygame.Rect(self.game.width // 2 - 130, button_y, 100, 40)
        no_rect = pygame.Rect(self.game.width // 2 + 30, button_y, 100, 40)

        if yes_rect.collidepoint(mouse_pos):
            self.game.sound_manager.button_click_sound.play()
            return self._execute_confirm_action()
        elif no_rect.collidepoint(mouse_pos):
            self.game.sound_manager.button_click_sound.play()
            self.show_confirm = False
            return True

        return False

    def _handle_menu_click(self, mouse_pos):
        """Xử lý click trong menu chính - ĐÃ SỬA"""
        # Tính toán vị trí các nút (giống như trong _draw_menu_buttons)
        total_buttons_height = len(self.buttons) * self.button_height + (len(self.buttons) - 1) * self.button_margin
        start_y = self.y + 150  # Bắt đầu từ dưới thanh tiến độ

        for i, button in enumerate(self.buttons):
            button_rect = pygame.Rect(
                self.game.width // 2 - self.button_width // 2,
                start_y + i * (self.button_height + self.button_margin),
                self.button_width,
                self.button_height
            )

            if button_rect.collidepoint(mouse_pos):
                self.game.sound_manager.button_click_sound.play()
                button["action"]()
                return True

        return False

    def _execute_confirm_action(self):
        """Thực hiện hành động xác nhận"""
        if self.confirm_selected == 0:  # Yes
            if self.confirm_action == 1:  # restart
                # Gọi restart_game trực tiếp
                self.game.restart_game()
                self.visible = False  # Đóng pause menu sau khi restart
                return True
            else:  # main_menu
                self.game.return_code = 'menu'
                self.game.running = False
        else:  # No
            self.show_confirm = False

        return True

    def pause_game(self):
        """Tạm dừng game"""
        if not self.visible and not self.game.dying and not self.game.ui.game_over_screen:
            self.visible = True
            self.background_surface = None
            self.game.sound_manager.button_click_sound.play()

            # Dừng âm thanh game
            self.game.sound_manager.stop_ghost()
            self.game.sound_manager.stop_power()
            self.game.sound_manager.pause_turn_egg()

            # CHỈ PAUSE INTRO NẾU NÓ ĐANG PHÁT
            if self.game.sound_manager.intro_channel.get_busy():
                self.game.sound_manager.pause_intro()

            self.selected_index = 0

    def resume_game(self):
        """Tiếp tục game"""
        if self.visible:
            self.visible = False
            self.game.sound_manager.button_click_sound.play()
            self.game.countdown_active = True
            self.game.countdown_timer = 3.0

    def confirm_restart(self):
        """Xác nhận restart game"""
        self.show_confirm = True
        self.confirm_action = 1
        self.confirm_selected = 0

    def confirm_main_menu(self):
        """Xác nhận về main menu"""
        self.show_confirm = True
        self.confirm_action = 2
        self.confirm_selected = 0
