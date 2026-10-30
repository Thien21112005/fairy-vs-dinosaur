import random

import pygame


class Player:
    def __init__(self, game):
        self.game = game
        self.row = 24
        self.col = 15
        self.x = self.col * self.game.num2_c + self.game.num2_c / 2.0
        self.y = self.row * self.game.num1_r + self.game.num1_r / 2.0
        self.direction = 0
        self.requested_direction = -1

        # Load cả hai bộ asset: blue và red
        self.p_raw_blue = [pygame.image.load(f"assets/Pac-man/blue/tile00{i}.png").convert_alpha() for i in range(0, 8)]
        self.p_raw_red = [pygame.image.load(f"assets/Pac-man/red/tile00{i}.png").convert_alpha() for i in range(0, 8)]

        p_scale = 2
        pac_size = int(min(self.game.num2_c, self.game.num1_r) * p_scale)
        self.pac_w = pac_size
        self.pac_h = pac_size

        # Tạo animation sets cho cả blue và red
        self.setup_animation_sets()

        self.frame = len(self.p_raw_blue)
        self.time = 0.0
        self.moved = False
        self.dead = False
        self.death_frame = None

        # Thêm cho AI mode
        self.ai_path = []

    def setup_animation_sets(self):
        """Khởi tạo các bộ animation cho cả blue và red"""
        # Blue animation set
        self.p_phai_blue = [pygame.transform.smoothscale(img, (self.pac_w, self.pac_h)) for img in self.p_raw_blue]
        self.p_trai_blue = [pygame.transform.flip(img, True, False) for img in self.p_phai_blue]
        self.p_len_blue = [pygame.transform.smoothscale(pygame.transform.rotate(img, 90), (self.pac_w, self.pac_h)) for
                           img in self.p_phai_blue]
        self.p_xuong_blue = [pygame.transform.smoothscale(pygame.transform.rotate(img, -90), (self.pac_w, self.pac_h))
                             for img in self.p_phai_blue]

        # Red animation set
        self.p_phai_red = [pygame.transform.smoothscale(img, (self.pac_w, self.pac_h)) for img in self.p_raw_red]
        self.p_trai_red = [pygame.transform.flip(img, True, False) for img in self.p_phai_red]
        self.p_len_red = [pygame.transform.smoothscale(pygame.transform.rotate(img, 90), (self.pac_w, self.pac_h)) for
                          img in self.p_phai_red]
        self.p_xuong_red = [pygame.transform.smoothscale(pygame.transform.rotate(img, -90), (self.pac_w, self.pac_h))
                            for img in self.p_phai_red]

    def get_current_animation_set(self):
        """Trả về bộ animation hiện tại dựa trên trạng thái frightened"""
        if self.game.mode_manager.frightened_active:
            return {
                'right': self.p_phai_red,
                'left': self.p_trai_red,
                'up': self.p_len_red,
                'down': self.p_xuong_red
            }
        else:
            return {
                'right': self.p_phai_blue,
                'left': self.p_trai_blue,
                'up': self.p_len_blue,
                'down': self.p_xuong_blue
            }

    def find_next_pellet_target(self):
        """Tìm pellet chưa ăn gần nhất (theo độ dài path BFS), không ưu tiên power pellet hay normal pellet"""
        # Sử dụng method mới trong path_finder để tìm path đến pellet gần nhất bằng một BFS duy nhất
        path = self.game.path_finder.find_path_to_nearest_pellet(self.row, self.col)

        if path:
            self.ai_path = path
        else:
            self.ai_path = []

    def update(self, dt):
        if self.dead or not self.game.game_started:
            return
        self.time += dt
        if self.time >= self.game.frame_ms * self.frame:
            self.time %= self.game.frame_ms * self.frame

        if not self.game.game_started:
            return

        center_x = self.col * self.game.num2_c + self.game.num2_c / 2.0
        center_y = self.row * self.game.num1_r + self.game.num1_r / 2.0

        # Xử lý AI mode - SỬA: Thêm điều kiện dễ hơn để tránh bị kẹt
        if self.game.ai_mode:
            # SỬA: Dùng ngưỡng lớn hơn để tránh bị kẹt không về được trung tâm
            if abs(self.x - center_x) < 2.0 and abs(self.y - center_y) < 2.0:
                # Đảm bảo về đúng trung tâm
                self.x = center_x
                self.y = center_y

                # Tại trung tâm ô, quyết định hướng
                if not self.ai_path or (self.row, self.col) != self.ai_path[0]:
                    self.find_next_pellet_target()
                    if not self.ai_path:
                        # THÊM: Nếu không tìm được đường, thử tìm lại sau 1 khoảng thời gian
                        # hoặc chọn hướng ngẫu nhiên để thoát khỏi vị trí kẹt
                        valid_directions = []
                        for dx, dy, d in self.game.path_finder.directions:
                            next_row = self.row + dy
                            next_col = self.col + dx
                            if not self.game.level.checktuong_for_pacman(next_row, next_col):
                                valid_directions.append(d)

                        if valid_directions:
                            # Chọn hướng ngẫu nhiên hợp lệ để thoát khỏi vị trí kẹt
                            self.requested_direction = random.choice(valid_directions)
                            # print(f"Không tìm được đường, chọn hướng ngẫu nhiên: {self.requested_direction}")
                        return

                if len(self.ai_path) > 1:
                    next_r, next_c = self.ai_path[1]
                    found_direction = False
                    for dx, dy, d in self.game.path_finder.directions:
                        exp_r = self.row + dy
                        exp_c = self.col + dx
                        if dy == 0 and (exp_c < 0 or exp_c >= self.game.col):
                            if self.game.level.is_tunnel_row(self.row):
                                exp_c = exp_c % self.game.col
                                if exp_c < 0:
                                    exp_c += self.game.col
                        if exp_r == next_r and exp_c == next_c:
                            self.requested_direction = d
                            found_direction = True
                            break

                    # THÊM: Nếu không tìm được hướng từ path, tìm đường mới
                    if not found_direction:
                        # print("Không tìm được hướng từ path, tìm đường mới")
                        self.find_next_pellet_target()

        # Handle direction change
        if self.requested_direction != -1 and self.requested_direction != self.direction:
            dy = 1 if self.requested_direction == 3 else -1 if self.requested_direction == 2 else 0
            dx = 1 if self.requested_direction == 0 else -1 if self.requested_direction == 1 else 0
            next_row = self.row + dy
            next_col = self.col + dx
            if not self.game.level.checktuong_for_pacman(next_row, next_col):
                self.direction = self.requested_direction
                self.requested_direction = -1

        # Get velocity
        vx = self.game.speed_h if self.direction == 0 else -self.game.speed_h if self.direction == 1 else 0
        vy = self.game.speed_v if self.direction == 3 else -self.game.speed_v if self.direction == 2 else 0

        proposed_x = self.x + vx * (dt / 1000.0)
        proposed_y = self.y + vy * (dt / 1000.0)

        current_col = int(self.x // self.game.num2_c)
        current_row = int(self.y // self.game.num1_r)

        is_tunnel = self.game.level.is_tunnel_row(current_row)
        if is_tunnel and (self.direction == 0 or self.direction == 1):
            if proposed_x < 0:
                proposed_x += self.game.width
            elif proposed_x > self.game.width:
                proposed_x -= self.game.width

        proposed_col = int(proposed_x // self.game.num2_c)
        proposed_row = int(proposed_y // self.game.num1_r)

        if proposed_col != current_col or proposed_row != current_row:
            if self.game.level.checktuong_for_pacman(proposed_row, proposed_col):
                if vx > 0:
                    proposed_x = min(proposed_x, (current_col + 1) * self.game.num2_c - 0.01)
                elif vx < 0:
                    proposed_x = max(proposed_x, current_col * self.game.num2_c + 0.01)
                if vy > 0:
                    proposed_y = min(proposed_y, (current_row + 1) * self.game.num1_r - 0.01)
                elif vy < 0:
                    proposed_y = max(proposed_y, current_row * self.game.num1_r + 0.01)

        old_x, old_y = self.x, self.y
        self.x = proposed_x
        self.y = proposed_y

        # Snap to center
        if self.direction in (0, 1):  # horizontal
            self.y = int(self.y // self.game.num1_r) * self.game.num1_r + self.game.num1_r / 2.0
        else:  # vertical
            self.x = int(self.x // self.game.num2_c) * self.game.num2_c + self.game.num2_c / 2.0

        self.col = int(self.x // self.game.num2_c)
        self.row = int(self.y // self.game.num1_r)
        self.moved = abs(self.x - old_x) > 0.001 or abs(self.y - old_y) > 0.001
        cell = self.game.level.level[self.row][self.col]
        if cell == 1:
            self.game.score += 10
            self.game.level.level[self.row][self.col] = 0
            self.game.level.remaining_pellets -= 1
            if self.game.sound_manager.pellet_toggle == 0:
                self.game.sound_manager.pellet_sound1.play()
            else:
                self.game.sound_manager.pellet_sound2.play()
            self.game.sound_manager.pellet_toggle = 1 - self.game.sound_manager.pellet_toggle
        elif cell == 2:
            self.game.score += 50
            self.game.level.level[self.row][self.col] = 0
            self.game.level.remaining_pellets -= 1
            self.game.mode_manager.activate_frightened()

        # Cập nhật ai_path nếu đã đến ô mới
        if self.game.ai_mode and self.ai_path and (self.row, self.col) == self.ai_path[0]:
            self.ai_path = self.ai_path[1:]

    def die(self):
        """Kích hoạt khi pacman bị ghost ăn"""
        self.dead = True
        # Lưu frame hiện tại làm frame chết
        anim_set = self.get_current_animation_set()
        if self.direction == 0:
            self.death_frame = anim_set['right'][3]  # Frame mở miệng lớn
        elif self.direction == 1:
            self.death_frame = anim_set['left'][3]
        elif self.direction == 2:
            self.death_frame = anim_set['up'][3]
        else:
            self.death_frame = anim_set['down'][3]

    def draw(self):
        if self.dead:
            # Hiển thị frame chết
            px = self.x - self.pac_w / 2.0
            py = self.y + self.game.y_offset - self.pac_h / 2.0
            self.game.screen.blit(self.death_frame, (px, py))
        else:
            # Lấy bộ animation hiện tại
            anim_set = self.get_current_animation_set()

            if self.moved:
                frame_i = int(self.time / self.game.frame_ms) % self.frame
            else:
                frame_i = 3  # Mouth open max

            # Chọn hình ảnh từ bộ animation phù hợp
            if self.direction == 0:
                img = anim_set['right'][frame_i]
            elif self.direction == 1:
                img = anim_set['left'][frame_i]
            elif self.direction == 2:
                img = anim_set['up'][frame_i]
            else:
                img = anim_set['down'][frame_i]
            px = self.x - self.pac_w / 2.0
            py = self.y + self.game.y_offset - self.pac_h / 2.0
            self.game.screen.blit(img, (px, py))

    def draw_path(self):
        if not self.ai_path:
            return

        # Bắt đầu vẽ từ vị trí thực tế của Pacman
        prev_x = self.x
        prev_y = self.y + self.game.y_offset
        prev_r, prev_c = self.row, self.col
        color = (255, 255, 0)  # yellow
        line_width = 2

        for r, c in self.ai_path:
            x = c * self.game.num2_c + self.game.num2_c / 2.0
            y = r * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset

            # Kiểm tra nếu đây là điểm đầu tiên trong path
            if (r, c) == (self.row, self.col):
                # Nếu là ô hiện tại, bỏ qua và chờ điểm tiếp theo
                prev_x = x
                prev_y = y
                prev_r, prev_c = r, c
                continue

            dc = c - prev_c
            dr = r - prev_r
            if abs(dc) > 1 and dr == 0:  # horizontal wrap - không vẽ line cho segment wrap
                # Chỉ update prev mà không vẽ
                prev_x = x
                prev_y = y
                prev_r, prev_c = r, c
                continue
            else:
                pygame.draw.line(self.game.screen, color, (prev_x, prev_y), (x, y), line_width)
            prev_x = x
            prev_y = y
            prev_r, prev_c = r, c

        # Draw arrow at end
        if len(self.ai_path) >= 2:
            # Tìm điểm cuối cùng không phải là vị trí hiện tại
            valid_path = [pos for pos in self.ai_path if pos != (self.row, self.col)]
            if len(valid_path) < 2:
                return

            prev_r, prev_c = valid_path[-2]
            last_r, last_c = valid_path[-1]
            last_x = last_c * self.game.num2_c + self.game.num2_c / 2.0
            last_y = last_r * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset

            for dx, dy, d in self.game.path_finder.directions:
                exp_r = prev_r + dy
                exp_c = prev_c + dx
                if dy == 0 and (exp_c < 0 or exp_c >= self.game.col):
                    if self.game.level.is_tunnel_row(prev_r):
                        exp_c = exp_c % self.game.col
                        if exp_c < 0:
                            exp_c += self.game.col
                if exp_r == last_r and exp_c == last_c:
                    udx = dx
                    udy = dy
                    break
            else:
                return

            arrow_size = min(self.game.num1_r, self.game.num2_c) / 2
            perp_x = -udy
            perp_y = udx
            tip = (last_x, last_y)
            base1 = (last_x - arrow_size * udx + (arrow_size / 2) * perp_x,
                     last_y - arrow_size * udy + (arrow_size / 2) * perp_y)
            base2 = (last_x - arrow_size * udx - (arrow_size / 2) * perp_x,
                     last_y - arrow_size * udy - (arrow_size / 2) * perp_y)
            pygame.draw.line(self.game.screen, color, tip, base1, line_width)
            pygame.draw.line(self.game.screen, color, tip, base2, line_width)

    def clear_path(self):
        self.ai_path = []

    def reset(self):
        """Reset player trạng thái về ban đầu"""
        self.visible = True
        self.row = 24
        self.col = 15
        self.x = self.col * self.game.num2_c + self.game.num2_c / 2.0
        self.y = self.row * self.game.num1_r + self.game.num1_r / 2.0
        self.direction = 0
        self.requested_direction = -1
        self.time = 0.0
        self.moved = False
        self.dead = False
        self.death_frame = None
        self.ai_path = []
