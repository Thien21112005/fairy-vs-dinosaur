import pygame
from pygame.mixer import Sound

from dich import get_translation
from sounds import *
class LevelCompleteAnimation:
    def __init__(self, game):
        self.sound = SoundManager()

        self.game = game
        self.active = False  # Flag để biết animation đang chạy không

        # Load animation images (chuyển từ PacmanGame)
        try:
            self.gong_img = pygame.image.load("assets/End/gong.png").convert_alpha()
            self.throw_img = pygame.image.load("assets/End/throw.png").convert_alpha()
            self.fireball_imgs = [
                pygame.image.load("assets/End/fireball1.png").convert_alpha(),
                pygame.image.load("assets/End/fireball2.png").convert_alpha()
            ]
        except pygame.error as e:
            print(f"Không thể load animation images: {e}")
            self.gong_img = self.throw_img = pygame.Surface((self.game.pac_w, self.game.pac_h))  # Fallback
            self.fireball_imgs = [pygame.Surface((20, 20)), pygame.Surface((20, 20))]

        # Biến cho animation (chuyển từ PacmanGame)
        self.state = 'none'  # States: 'none', 'gong', 'blink_fireball', 'grow_fireball', 'hold_fireball', 'throw', 'fly_fireball', 'done'
        self.timer = 0
        self.fireball_x = 0
        self.fireball_y = 0
        self.fireball_scale = 1
        self.fireball_frame = 0
        self.fireball_speed = 200  # Pixel/giây bay
        self.fireball_vx = 0
        self.fireball_vy = 0
        self.fireball_initial_dist = 0  # Để tính dist ban đầu cho scale
        self.fireball_target_x = 15 * self.game.num2_c + self.game.num2_c / 2.0  # Col 15 (trung tâm ghost)
        self.fireball_target_y = 15 * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset  # Row 13 (gate)
        self.gong_duration = 2000  # ms
        self.blink_duration = 200  # ms per on/off phase
        self.blink_phase = 0
        self.blink_visible = True
        self.grow_duration = 1000  # ms
        self.hold_duration = 900  # ms (giữ 0.5 giây sau khi phình to)
        self.throw_duration = 500  # ms
        self.direction = 'right'  # Hướng mặc định: 'right' hoặc 'left'

        # Fonts for level complete menu (giống pause menu)
        self.title_font = pygame.font.SysFont('monospace', 50, bold=True)
        self.button_font = pygame.font.SysFont('monospace', 34, bold=True)
        self.small_font = pygame.font.SysFont('monospace', 20, bold=True)
        self.progress_font = pygame.font.SysFont('monospace', 16, bold=True)

        # Button definitions for level complete
        self.buttons = [
            {"text": get_translation("continue"), "action": self.continue_game},
            {"text": get_translation("main_menu"), "action": self.confirm_main_menu}
        ]
        self.button_height = 55
        self.button_width = 220
        self.button_margin = 25

        # States
        self.selected_index = 0
        self.hover_states = [False] * len(self.buttons)
        self.prev_hover_states = [False] * len(self.buttons)
        self.background_surface = None

        # Confirm dialog
        self.confirm_visible = False
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

    def start(self):
        """Bắt đầu animation"""
        self.active = True
        self.state = 'gong'
        self.timer = 0
        self.game.player.visible = False  # Ẩn Pacman gốc
        self.game.game_started = False  # Dừng update player/ghost
        self.sound.stop_all_sounds()

        # Xác định hướng dựa trên vị trí player so với target
        if self.game.player.x > self.fireball_target_x:
            self.direction = 'left'
        else:
            self.direction = 'right'

        # Đặt fireball ngay trên đầu Pacman
        self.fireball_x = self.game.player.x  # Giữ x trung tâm Pacman
        self.fireball_y = self.game.player.y + self.game.y_offset - (self.game.pac_h / 2 + 70)  # Trên đầu cao hơn (tăng padding từ 10 lên 20)

        self.fireball_scale = 0.5

        # Tính dist ban đầu đến target
        dx = self.fireball_target_x - self.fireball_x
        dy = self.fireball_target_y - self.fireball_y
        self.fireball_initial_dist = (dx ** 2 + dy ** 2) ** 0.5

        # Dừng sounds
        self.game.sound_manager.stop_ghost()
        self.game.sound_manager.stop_power()

        # Phát sound nếu có (comment out nếu chưa có)
        # self.game.sound_manager.play_level_complete()

        # Tăng level
        self.game.level_num += 1

    def update(self, dt):
        """Cập nhật timer và state (gọi từ game loop nếu active)"""
        print("LevelCompleteAnimation state:", self.state)
        if not self.active:
            return

        self.timer += dt

        if self.state == 'gong':
            if self.timer >= self.gong_duration:
                self.state = 'blink_fireball'
                self.timer = 0
                self.blink_phase = 0
                self.blink_visible = True
                self.game.sound_manager.play_flick()  # Phát sound flick khi vào blink

        elif self.state == 'blink_fireball':
            if self.timer >= self.blink_duration:
                self.blink_phase += 1
                self.timer = 0
                self.blink_visible = (self.blink_phase % 2 == 0)
                if self.blink_phase >= 4:  # Sau 2 lần chớp tắt (on-off-on-off)
                    self.state = 'grow_fireball'
                    self.timer = 0
                    self.game.sound_manager.stop_flick()  # Dừng flick khi ra khỏi blink
                    self.game.sound_manager.play_hold()  # Phát hold khi vào grow
            if self.blink_visible:
                self.fireball_frame = (self.fireball_frame + 1) % 2  # Alternate frames nếu visible

        elif self.state == 'grow_fireball':
            progress = min(1, self.timer / self.grow_duration)
            self.fireball_scale = 0.5 + 6.0 * progress  # Từ 0.5 đến 5.0
            self.fireball_frame = (self.fireball_frame + 1) % 2  # Alternate frames
            if self.timer >= self.grow_duration:
                self.state = 'hold_fireball'
                self.timer = 0

        elif self.state == 'hold_fireball':
            self.fireball_scale = 6.0
            self.fireball_frame = (self.fireball_frame + 1) % 2  # Alternate frames
            if self.timer >= self.hold_duration:
                self.state = 'throw'
                self.timer = 0
                self.game.sound_manager.stop_hold()  # Dừng hold khi ra khỏi hold
                self.game.sound_manager.play_throw()  # Phát throw khi vào throw


        elif self.state == 'throw':

            if self.timer >= self.throw_duration:
                self.state = 'fly_fireball'
                self.timer = 0
                # Tính velocity
                dx = self.fireball_target_x - self.fireball_x
                dy = self.fireball_target_y - self.fireball_y
                dist = (dx ** 2 + dy ** 2) ** 0.5
                self.fireball_vx = dx / dist * self.fireball_speed if dist > 0 else 0
                self.fireball_vy = dy / dist * self.fireball_speed if dist > 0 else 0
                self.fireball_initial_dist = dist


        elif self.state == 'fly_fireball':
            self.fireball_x += self.fireball_vx * (dt / 1000.0)  # dt là ms, chuyển sang seconds
            self.fireball_y += self.fireball_vy * (dt / 1000.0)
            self.fireball_frame = (self.fireball_frame + 1) % 2  # Alternate

            # Bé dần dựa trên dist còn lại
            dx_remaining = self.fireball_target_x - self.fireball_x
            dy_remaining = self.fireball_target_y - self.fireball_y
            remaining_dist = (dx_remaining ** 2 + dy_remaining ** 2) ** 0.5
            if self.fireball_initial_dist > 0:
                scale_ratio = remaining_dist / self.fireball_initial_dist
                self.fireball_scale = 5.0 * scale_ratio + 3 * (1 - scale_ratio)  # Từ 5.0 bé dần về 0.5

            if remaining_dist < 20:  # dễ đạt hơn, 20 pixel
                print("🔥 Animation complete -> DONE")
                self.state = 'done'
                self.game.sound_manager.stop_throw()  # Dừng throw nếu còn phát khi animation done

        if self.state == 'done':
            self.game.show_level_complete = True  # Set flag to show menu instead of resetting
            self.active = False
            self.state = 'none'

    def draw(self):
        """Vẽ animation (gọi từ game loop nếu active)"""
        if not self.active:
            return

        if self.state in ['gong', 'blink_fireball', 'grow_fireball', 'hold_fireball']:
            pac_img = self.gong_img
        elif self.state in ['throw', 'fly_fireball']:
            pac_img = self.throw_img
        else:
            return

        # Flip hình ảnh nếu hướng là left
        if self.direction == 'left':
            pac_img = pygame.transform.flip(pac_img, True, False)  # Flip ngang, không flip dọc

        scaled_pac = pygame.transform.scale(pac_img, (int(self.game.pac_w), int(self.game.pac_h)))
        self.game.screen.blit(scaled_pac, (int(self.game.player.x - self.game.pac_w / 2), int(self.game.player.y + self.game.y_offset - self.game.pac_h / 2)))

        if self.state in ['blink_fireball', 'grow_fireball', 'hold_fireball', 'throw', 'fly_fireball']:
            if self.state == 'blink_fireball' and not self.blink_visible:
                return  # Không vẽ fireball nếu không visible trong blink
            fb_img = self.fireball_imgs[self.fireball_frame]
            fb_size = (int(20 * self.fireball_scale), int(20 * self.fireball_scale))  # Base size 20x20
            scaled_fb = pygame.transform.scale(fb_img, fb_size)
            scaled_fb_rect = scaled_fb.get_rect(center=(int(self.fireball_x), int(self.fireball_y)))
            self.game.screen.blit(scaled_fb, scaled_fb_rect.topleft)

    def update_level_complete_hover(self, mouse_pos):
        """Cập nhật trạng thái hover cho level complete menu - Giống pause menu"""
        # Cập nhật hover cho menu chính - ĐÃ SỬA
        # Reset hover states
        for i in range(len(self.buttons)):
            self.hover_states[i] = False

        # Tính toán vị trí các nút (giống như trong _draw_menu_buttons)
        total_buttons_height = len(self.buttons) * self.button_height + (len(self.buttons) - 1) * self.button_margin
        start_y = (self.game.height - total_buttons_height) // 2 + 80  # Bắt đầu từ dưới thanh tiến độ

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

        if self.confirm_visible:
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

    def handle_level_complete_events(self, event):
        """Xử lý sự kiện cho level complete menu - Giống pause menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.confirm_visible:
                    self.confirm_visible = False
                    return True
                else:
                    self.continue_game()
                    return True

            if self.confirm_visible:
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

            else:
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

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            # print("CLICK!", self.active, self.game.show_level_complete, self.confirm_visible)
            print("Mouse clicked at:", event.pos)

            if self.confirm_visible:
                # Sử dụng cùng vị trí với _draw_confirm_dialog và _update_confirm_hover
                button_y = self.game.height // 2 + 20
                yes_rect = pygame.Rect(self.game.width // 2 - 130, button_y, 100, 40)
                no_rect = pygame.Rect(self.game.width // 2 + 30, button_y, 100, 40)

                if yes_rect.collidepoint(mouse_pos):
                    self.game.sound_manager.button_click_sound.play()
                    return self._execute_confirm_action()
                elif no_rect.collidepoint(mouse_pos):
                    self.game.sound_manager.button_click_sound.play()
                    self.confirm_visible = False
                    return True

            else:
                # Tính toán vị trí các nút (giống như trong _draw_menu_buttons)
                total_buttons_height = len(self.buttons) * self.button_height + (len(self.buttons) - 1) * self.button_margin
                start_y = (self.game.height - total_buttons_height) // 2 + 80  # Bắt đầu từ dưới thanh tiến độ

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
            self.game.return_code = 'menu'
            self.game.running = False
        else:  # No
            self.confirm_visible = False

        return True

    def continue_game(self):
        """Tiếp tục game"""
        print("Continuing game...")
        self.game.show_level_complete = False
        self.game.reset_for_next_level()

    def confirm_main_menu(self):
        """Xác nhận về main menu"""
        print("Showing confirm dialog...")
        self.confirm_visible = True
        self.confirm_action = 2
        self.confirm_selected = 0

    def draw_level_complete_menu(self):
        """Vẽ level complete menu với lớp phủ mờ - Giống pause menu"""
        if not self.game.show_level_complete:
            return

        # Vẽ nền mờ
        self._draw_blur_background(self.game.screen)

        # Vẽ menu chính
        self._draw_main_menu(self.game.screen)

        # Vẽ confirm dialog nếu cần
        if self.confirm_visible:
            self._draw_confirm_dialog(self.game.screen)

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
        menu_rect = pygame.Rect((self.game.width - 420) // 2, (self.game.height - 400) // 2, 420, 400)
        self._draw_menu_background(screen, menu_rect)

        # Vẽ tiêu đề
        self._draw_menu_title(screen)

        # Vẽ thanh tiến độ
        self._draw_progress_bar(screen)

        # Vẽ high score và time dưới progress bar
        self._draw_high_score_and_time(screen)

        # Vẽ các nút
        self._draw_menu_buttons(screen)

    def _draw_menu_background(self, screen, menu_rect):
        """Vẽ nền cho menu"""
        gradient_surface = pygame.Surface((420, 400), pygame.SRCALPHA)
        pygame.draw.rect(gradient_surface, (40, 40, 80, 220), (0, 0, 420, 400), border_radius=25)

        for i in range(400):
            color = (30 + i // 10, 30 + i // 10, 60 + i // 5)
            pygame.draw.line(gradient_surface, color, (0, i), (420, i))

        screen.blit(gradient_surface, menu_rect.topleft)

        # Vẽ border
        border_rect = menu_rect.inflate(4, 4)
        pygame.draw.rect(screen, (100, 150, 220, 150), border_rect, width=5, border_radius=25)
        pygame.draw.rect(screen, (80, 140, 200), menu_rect, width=4, border_radius=25)

    def _draw_menu_title(self, screen):
        """Vẽ tiêu đề menu"""
        title_text = self.title_font.render(get_translation("level complete"), True, (255, 255, 100))
        shadow_text = self.title_font.render(get_translation("level complete"), True, (100, 100, 0))
        title_rect = title_text.get_rect(center=(self.game.width // 2, (self.game.height - 400) // 2 + 40))
        shadow_rect = shadow_text.get_rect(center=(title_rect.centerx + 2, title_rect.centery + 2))

        screen.blit(shadow_text, shadow_rect)
        screen.blit(title_text, title_rect)

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
        bar_x = self.game.width // 2 - bar_width // 2
        bar_y = (self.game.height - 400) // 2 + 100  # Dưới tiêu đề

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

    def _draw_menu_buttons(self, screen):
        """Vẽ các nút trong menu - căn giữa chính xác"""
        # Tính toán vị trí các nút
        total_buttons_height = len(self.buttons) * self.button_height + (len(self.buttons) - 1) * self.button_margin
        start_y = (self.game.height - total_buttons_height) // 2 + 80  # Bắt đầu từ dưới thanh tiến độ

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
        question = "Return to main menu? Progress will not be saved."
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

    def _handle_level_complete_click(self, event):
        """Xử lý click chuột trong màn hình Level Complete"""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False  # Chỉ xử lý lick chuột trái

        mouse_pos = pygame.mouse.get_pos()

        # Danh sách nút — đảm bảo trùng với draw_level_complete_menu()
        buttons = [
            {"label": "Main Menu", "action": self._on_main_menu_click},
            {"label": "Continue", "action": self._on_continue_click},
        ]

        # Layout nút tương tự phần vẽ
        button_width = 200
        button_height = 50
        button_margin = 20
        start_y = self.game.height // 2 + 100

        for i, button in enumerate(buttons):
            button_rect = pygame.Rect(
                self.game.width // 2 - button_width // 2,
                start_y + i * (button_height + button_margin),
                button_width,
                button_height
            )

            if button_rect.collidepoint(mouse_pos):
                print(f"CLICKED {button['label']}")  # Debug
                self.game.sound_manager.button_click_sound.play()
                button["action"]()
                return True

        return False

    def _on_main_menu_click(self):
        """Quay lại main menu"""
        print("Returning to Main Menu")
        self.game.sound_manager.button_click_sound.play()
        self.game.show_level_complete = False
        self.active = False
        self.state = "none"
        # Gọi đến main menu của game
        self.game.return_to_main_menu()

    def _on_continue_click(self):
        """Tiếp tục level mới"""
        print("Continuing to next level")
        self.game.sound_manager.button_click_sound.play()
        self.game.show_level_complete = False
        self.active = False
        self.state = "none"
        self.game.load_next_level()

    def _draw_high_score_and_time(self, screen):
        """Vẽ high score và thời gian hoàn thành dưới tiêu đề"""
        menu_top = (self.game.height - 400) // 2
        y_pos = menu_top + 160  # Dưới progress bar (progress tại +100, height 25, +5 khoảng cách)

        # High Score với shadow
        hs_text = f"Score: {self.game.score}"
        hs_surface = self.small_font.render(hs_text, True, (255, 255, 100))  # Màu vàng sáng
        hs_shadow = self.small_font.render(hs_text, True, (100, 100, 0))
        hs_rect = hs_surface.get_rect(center=(self.game.width // 2, y_pos))
        hs_shadow_rect = hs_shadow.get_rect(center=(hs_rect.centerx + 1, hs_rect.centery + 1))
        screen.blit(hs_shadow, hs_shadow_rect)
        screen.blit(hs_surface, hs_rect)

        # Time hoàn thành với shadow
        seconds = int(self.game.play_time // 1000)
        minutes = int(seconds // 60)
        microseconds = int(self.game.play_time % 1000)
        time_text = f"Time: {minutes:02d}:{seconds:02d}.{microseconds:03d}"
        time_surface = self.small_font.render(time_text, True, (255, 255, 100))
        time_shadow = self.small_font.render(time_text, True, (100, 100, 0))
        time_rect = time_surface.get_rect(center=(self.game.width // 2, y_pos + 25))
        time_shadow_rect = time_shadow.get_rect(center=(time_rect.centerx + 1, time_rect.centery + 1))
        screen.blit(time_shadow, time_shadow_rect)
        screen.blit(time_surface, time_rect)