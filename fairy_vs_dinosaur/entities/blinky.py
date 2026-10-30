import pygame

from fairy_vs_dinosaur.entities.ghost import Ghost


class Blinky(Ghost):
    def __init__(self, game):
        super().__init__(game, name="blinky", start_row=12, start_col=15, color=(255, 0, 0))
        self.set_elroy_thresholds()
        # Scatter target cho Blinky: top-right
        self.scatter_target_r = 0
        self.scatter_target_c = self.game.col - 1
        # Scatter cycle cho Blinky (top-right circuit theo code gốc)
        self.scatter_cycle = [
            (6, 22), (6, 23), (6, 24), (6, 25), (6, 26), (6, 27),
            (5, 27), (4, 27), (3, 27), (2, 27),
            (2, 26), (2, 25), (2, 24), (2, 23), (2, 22),
            (3, 22), (4, 22), (5, 22)
        ]
        self.current_cycle_index = -1  # Theo dõi vị trí trong cycle

        # Load animation frames cho ghost elroy (chế độ Elroy)
        try:
            self.elroy_frames = [pygame.image.load(f"assets/Ghost/{self.name}/dien/00{i}.png").convert_alpha() for i in range(0, 6)]
            # Scale các frame elroy
            self.elroy_frames = [pygame.transform.smoothscale(img, (self.ghost_w, self.ghost_h)) for img in self.elroy_frames]
            self.elroy_frame_count = len(self.elroy_frames)
        except:
            print(f"Không thể load elroy animation cho {self.name}. Sử dụng fallback normal frames.")
            self.elroy_frames = self.normal_frames
            self.elroy_frame_count = self.normal_frame_count

        # Tạo animation cho các hướng từ các frame elroy
        self.elroy_animations = {
            'right': self.elroy_frames,
            'left': [pygame.transform.flip(frame, True, False) for frame in self.elroy_frames],
            'up': [pygame.transform.rotate(frame, 90) for frame in self.elroy_frames],
            'down': [pygame.transform.rotate(frame, -90) for frame in self.elroy_frames]
        }
        # Không delay cho Blinky
        self.release_delay = 0
        self.release_timer = self.release_delay

    def set_speed_multipliers(self):
        super().set_speed_multipliers()
        level = self.game.level_num
        # Elroy multipliers increase slightly with levels for more challenge
        if level == 1:
            self.elroy1_multiplier = 1.0
            self.elroy2_multiplier = 1.05
        elif 2 <= level <= 4:
            self.elroy1_multiplier = 1.05
            self.elroy2_multiplier = 1.1
        else:
            self.elroy1_multiplier = 1.1
            self.elroy2_multiplier = 1.15

    def set_elroy_thresholds(self):
        level = self.game.level_num
        if level == 1:
            self.elroy1_threshold = 20
        elif level == 2:
            self.elroy1_threshold = 30
        elif 3 <= level <= 5:
            self.elroy1_threshold = 40
        elif 6 <= level <= 8:
            self.elroy1_threshold = 50
        elif 9 <= level <= 11:
            self.elroy1_threshold = 60
        elif 12 <= level <= 14:
            self.elroy1_threshold = 80
        elif 15 <= level <= 18:
            self.elroy1_threshold = 100
        else:  # 19+
            self.elroy1_threshold = 120
        self.elroy2_threshold = self.elroy1_threshold // 2

    def is_elroy(self):
        return self.game.level.remaining_pellets <= self.elroy1_threshold

    def get_base_multiplier(self):
        if self.game.level.remaining_pellets <= self.elroy2_threshold:
            return self.elroy2_multiplier
        elif self.game.level.remaining_pellets <= self.elroy1_threshold:
            return self.elroy1_multiplier
        else:
            return self.normal_speed_multiplier

    def get_chase_target(self):
        # Blinky chase trực tiếp vị trí Pac-Man (theo chuẩn 1980)
        return self.game.player.row, self.game.player.col

    def get_scatter_target(self):
        # Scatter cho Blinky: di chuyển theo circuit quanh top-right
        # Tìm vị trí hiện tại trong cycle
        current_index = -1
        for i, (r, c) in enumerate(self.scatter_cycle):
            if self.row == r and self.col == c:
                current_index = i
                break

        # Nếu đang ở một điểm trong cycle, chọn điểm tiếp theo
        if current_index != -1:
            next_index = (current_index + 1) % len(self.scatter_cycle)
            return self.scatter_cycle[next_index]
        else:
            # Nếu không ở trong cycle, đi đến điểm đầu tiên
            return self.scatter_cycle[0]

    def draw(self):
        # Tính frame hiện tại dựa trên thời gian
        if self.hatching:
            # Hiển thị animation hatchegg
            frame_index = int((self.hatch_animation_time / self.hatch_animation_duration) * len(self.hatchegg_frames))
            frame_index = min(frame_index, len(self.hatchegg_frames) - 1)  # Đảm bảo không vượt quá số frame
            image = self.hatchegg_frames[frame_index]
            # Vẽ ghost với animation hatchegg
            px = self.x - self.ghost_w / 2.0
            py = self.y + self.game.y_offset - self.ghost_h / 2.0
            self.game.screen.blit(image, (px, py))
            return
        if self.returning_home:
            # Hiển thị animation turnegg
            frame_index = int(self.time / self.animation_speed) % len(self.turnegg_frames)
            image = self.turnegg_frames[frame_index]
            # Vẽ ghost với animation turnegg
            px = self.x - self.ghost_w / 2.0
            py = self.y + self.game.y_offset - self.ghost_h / 2.0
            self.game.screen.blit(image, (px, py))
            return
        if self.eaten:
            # Tính frame index cho animation hurt
            frame_index = int((self.eaten_animation_time / self.eaten_animation_duration) * len(self.hurt_frames))
            frame_index = min(frame_index, len(self.hurt_frames) - 1)  # Đảm bảo không vượt quá số frame

            # Chọn hình ảnh từ bộ hurt animation theo hướng
            if self.direction == 0:  # right
                image = self.hurt_animations['right'][frame_index]
            elif self.direction == 1:  # left
                image = self.hurt_animations['left'][frame_index]
            elif self.direction == 2:  # up
                image = self.hurt_animations['up'][frame_index]
            else:  # down
                image = self.hurt_animations['down'][frame_index]

            # Vẽ ghost với animation hurt
            px = self.x - self.ghost_w / 2.0
            py = self.y + self.game.y_offset - self.ghost_h / 2.0
            self.game.screen.blit(image, (px, py))
            return
        if self.eating and self.game.dying:  # CHỈ hiển thị animation eat khi đang trong death sequence
            # Tính frame index - lặp liên tục cho đến khi kết thúc death sequence
            frame_index = int((self.eat_animation_time / self.eat_animation_duration) * len(self.eat_frames) * 3) % len(
                self.eat_frames)
            # Chọn hình ảnh từ bộ eat animation
            if self.direction == 0:  # right
                image = self.eat_animations['right'][frame_index]
            elif self.direction == 1:  # left
                image = self.eat_animations['left'][frame_index]
            elif self.direction == 2:  # up
                image = self.eat_animations['up'][frame_index]
            else:  # down
                image = self.eat_animations['down'][frame_index]
        elif self.game.show_ready or self.release_timer > 0:
            # Sử dụng animation relax khi đang ở trạng thái READY! hoặc đang delay release
            frame_index = int(self.time / self.animation_speed) % len(self.relax_frames)
            image = self.relax_frames[frame_index]
        else:
            frame_index = int(self.time / self.animation_speed)
            # Chọn hình ảnh dựa trên trạng thái và hướng
            frightened_active = self.game.mode_manager.frightened_active and not self.frightened_disabled
            if frightened_active:
                # Kiểm tra nếu sắp hết frightened để nhấp nháy
                if self.game.mode_manager.frightened_timer * 1000 < self.flash_start_time:  # Chuyển sang ms để so sánh
                    # Nhấp nháy luân phiên
                    if (int(self.time / self.flash_interval) % 2) == 0:
                        # Dùng frightened animation (luân phiên frame, thường là blue)
                        frame_index = frame_index % self.frightened_frame_count
                        if self.direction == 0:  # right
                            image = self.frightened_animations['right'][frame_index]
                        elif self.direction == 1:  # left
                            image = self.frightened_animations['left'][frame_index]
                        elif self.direction == 2:  # up
                            image = self.frightened_animations['up'][frame_index]
                        else:  # down
                            image = self.frightened_animations['down'][frame_index]
                    else:
                        # Dùng frame flash (white) theo hướng
                        if self.direction == 0:  # right
                            image = self.flash_animations['right'][0]
                        elif self.direction == 1:  # left
                            image = self.flash_animations['left'][0]
                        elif self.direction == 2:  # up
                            image = self.flash_animations['up'][0]
                        else:  # down
                            image = self.flash_animations['down'][0]
                else:
                    # Bình thường frightened animation (thường là blue)
                    frame_index = frame_index % self.frightened_frame_count
                    if self.direction == 0:  # right
                        image = self.frightened_animations['right'][frame_index]
                    elif self.direction == 1:  # left
                        image = self.frightened_animations['left'][frame_index]
                    elif self.direction == 2:  # up
                        image = self.frightened_animations['up'][frame_index]
                    else:  # down
                        image = self.frightened_animations['down'][frame_index]
            elif self.is_elroy():
                # Chọn animation frame dựa trên hướng (elroy mode)
                frame_index = frame_index % self.elroy_frame_count
                if self.direction == 0:  # right
                    image = self.elroy_animations['right'][frame_index]
                elif self.direction == 1:  # left
                    image = self.elroy_animations['left'][frame_index]
                elif self.direction == 2:  # up
                    image = self.elroy_animations['up'][frame_index]
                else:  # down
                    image = self.elroy_animations['down'][frame_index]
            else:
                # Chọn animation frame dựa trên hướng (bình thường)
                frame_index = frame_index % self.normal_frame_count
                if self.direction == 0:  # right
                    image = self.normal_animations['right'][frame_index]
                elif self.direction == 1:  # left
                    image = self.normal_animations['left'][frame_index]
                elif self.direction == 2:  # up
                    image = self.normal_animations['up'][frame_index]
                else:  # down
                    image = self.normal_animations['down'][frame_index]

        # Sử dụng ghost_w và ghost_h thay vì game.pac_w và game.pac_h
        px = self.x - self.ghost_w / 2.0
        py = self.y + self.game.y_offset - self.ghost_h / 2.0
        self.game.screen.blit(image, (px, py))
