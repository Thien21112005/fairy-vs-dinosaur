import pygame
import random
from abc import ABC, abstractmethod

class Ghost(ABC):
    def __init__(self, game, name, start_row, start_col, color):
        self.mode = None
        self.game = game
        self.name = name
        self.start_row = start_row  # THÊM DÒNG NÀY
        self.start_col = start_col  # THÊM DÒNG NÀY
        self.row = start_row
        self.col = start_col
        self.x = self.col * self.game.num2_c + self.game.num2_c / 2.0
        self.y = self.row * self.game.num1_r + self.game.num1_r / 2.0
        self.direction = 0  # Start right

        # Thêm thuộc tính scale cho ghost
        self.ghost_scale = 2.2  # Có thể điều chỉnh giá trị này để to hơn pacman
        ghost_size = int(min(self.game.num2_c, self.game.num1_r) * self.ghost_scale)
        self.ghost_w = ghost_size
        self.ghost_h = ghost_size

        self.set_speed_multipliers()

        # Load animation frames cho ghost bình thường
        self.normal_frames = [pygame.image.load(f"assets/Ghost/{name}/thuong/tile00{i}.png").convert_alpha() for i in range(0, 6)]
        # Scale các frame với kích thước mới
        self.normal_frames = [pygame.transform.smoothscale(img, (self.ghost_w, self.ghost_h)) for img in self.normal_frames]

        # Load animation frames cho ghost frightened
        self.frightened_frames = [pygame.image.load(f"assets/Ghost/{name}/ghost/tile00{i}.png").convert_alpha() for i in range(0, 4)]
        # Scale các frame frightened
        self.frightened_frames = [pygame.transform.smoothscale(img, (self.ghost_w, self.ghost_h)) for img in self.frightened_frames]
        # Load frame flash (white) - chung cho tất cả ghost
        try:
            self.flash_frame = pygame.image.load("assets/Ghost/flash.png").convert_alpha()
            self.flash_frame = pygame.transform.smoothscale(self.flash_frame, (self.ghost_w, self.ghost_h))
            # Tạo animations cho flash theo hướng (chỉ 1 frame)
            self.flash_animations = {
                'right': [self.flash_frame],
                'left': [pygame.transform.flip(self.flash_frame, True, False)],
                'up': [pygame.transform.rotate(self.flash_frame, 90)],
                'down': [pygame.transform.rotate(self.flash_frame, -90)]
            }
        except:
            print("Không thể load flash.png - fallback dùng frightened frame[2] nếu có")
            # Fallback: dùng frightened_frames[2] giả sử là white
            if len(self.frightened_frames) > 2:
                fallback_flash = self.frightened_frames[2]
            else:
                fallback_flash = self.frightened_frames[0]  # Hoặc blue nếu không có
            self.flash_animations = {
                'right': [fallback_flash],
                'left': [pygame.transform.flip(fallback_flash, True, False)],
                'up': [pygame.transform.rotate(fallback_flash, 90)],
                'down': [pygame.transform.rotate(fallback_flash, -90)]
            }
        # Tạo animation sets cho các hướng
        self.setup_animation_sets()

        # Biến thời gian cho animation
        self.time = 0.0
        self.normal_frame_count = len(self.normal_frames)
        self.frightened_frame_count = len(self.frightened_frames)
        self.animation_speed = 100  # ms per frame

        self.path = []
        self.color = color  # For path drawing

        # Thêm thuộc tính mới để theo dõi trạng thái tunnel
        self.tunnel_slowdown_timer = 0.0
        self.tunnel_slowdown_duration = 1.5  # 1.5 giây
        self.just_teleported = False

        # Load animation frames cho ghost eat
        self.eat_frames = [pygame.image.load(f"assets/Ghost/{name}/eat/tile00{i}.png").convert_alpha() for i in range(0, 3)]
        # Scale các frame eat
        self.eat_frames = [pygame.transform.smoothscale(img, (self.ghost_w, self.ghost_h)) for img in self.eat_frames]

        # Tạo animation cho trạng thái eat
        self.eat_animations = {
            'right': self.eat_frames,
            'left': [pygame.transform.flip(frame, True, False) for frame in self.eat_frames],
            'up': [pygame.transform.rotate(frame, 90) for frame in self.eat_frames],
            'down': [pygame.transform.rotate(frame, -90) for frame in self.eat_frames]
        }
        self.eating = False
        self.eat_animation_time = 0
        self.eat_animation_duration = 600  # 0.6 giây cho animation eat


        #BỊ ĂN
        # Thêm thuộc tính cho trạng thái bị ăn và animation hurt
        self.eaten = False
        self.eaten_animation_time = 0
        self.eaten_animation_duration = 800  # 0.8 giây cho animation bị ăn

        # Load animation frames cho ghost bị ăn (hurt)
        self.hurt_frames = [pygame.image.load(f"assets/Ghost/{name}/hurt/00{i}.png").convert_alpha() for i in range(0, 4)]
        # Scale các frame hurt
        self.hurt_frames = [pygame.transform.smoothscale(img, (self.ghost_w, self.ghost_h)) for img in self.hurt_frames]

        # Tạo animation cho trạng thái bị ăn
        self.hurt_animations = {
            'right': self.hurt_frames,
            'left': [pygame.transform.flip(frame, True, False) for frame in self.hurt_frames],
            'up': [pygame.transform.rotate(frame, 90) for frame in self.hurt_frames],
            'down': [pygame.transform.rotate(frame, -90) for frame in self.hurt_frames]
        }

        # Thêm thuộc tính để theo dõi trạng thái bị ăn
        self.just_eaten = False

        # THÊM THUỘC TÍNH CHO TRẠNG THÁI VỀ NHÀ
        self.returning_home = False
        self.reached_home = False

        # Load animation frames cho ghost turnegg
        try:
            self.turnegg_frames = [pygame.image.load(f"assets/Ghost/{name}/turnegg/00{i}.png").convert_alpha() for i in
                                   range(0, 4)]
            # Scale các frame turnegg
            self.turnegg_frames = [pygame.transform.smoothscale(img, (self.ghost_w, self.ghost_h)) for img in
                                   self.turnegg_frames]

        except:
            print(f"Không thể load turnegg animation cho {name}")
            self.turnegg_frames = []
            self.turnegg_animations = {}

        # Vị trí nhà ma
        self.ghost_home = (15, 14)

        # THÊM THUỘC TÍNH CHO TRẠNG THÁI NỞ TRỨNG
        self.hatching = False
        self.hatch_animation_time = 0
        self.hatch_animation_duration = 0  # Sẽ được set dựa trên độ dài âm thanh

        # Load animation frames cho hatchegg
        try:
            self.hatchegg_frames = [pygame.image.load(f"assets/Ghost/{name}/hatchegg/00{i}.png").convert_alpha() for i
                                    in range(0, 8)]
            # Scale các frame hatchegg
            self.hatchegg_frames = [pygame.transform.smoothscale(img, (self.ghost_w, self.ghost_h)) for img in
                                    self.hatchegg_frames]
        except:
            print(f"Không thể load hatchegg animation cho {name}")
            self.hatchegg_frames = []



        self.flash_interval = 150  # ms cho mỗi lần nhấp nháy (có thể điều chỉnh)
        self.flash_start_time = 2000  # Bắt đầu nhấp nháy khi còn 2 giây (ms, điều chỉnh dựa trên level)

        # Thêm flag để vô hiệu hóa frightened cho ghost này sau khi bị ăn
        self.frightened_disabled = False

        # Load animation frames cho ghost relax
        try:
            self.relax_frames = [pygame.image.load(f"assets/Ghost/{name}/relax/tile00{i}.png").convert_alpha() for i in range(3)]
            # Scale các frame relax
            self.relax_frames = [pygame.transform.smoothscale(img, (self.ghost_w, self.ghost_h)) for img in self.relax_frames]
        except:
            print(f"Không thể load relax animation cho {name}")
            self.relax_frames = self.normal_frames  # Fallback to normal frames

        # Thêm thuộc tính cho delay release khỏi nhà ma
        self.release_delay = 0  # Mặc định 0, sẽ override ở subclass
        self.release_timer = self.release_delay

    def start_hatching(self):
        """Bắt đầu quá trình nở trứng"""
        self.hatching = True
        self.hatch_animation_time = 0
        # Lấy độ dài âm thanh egg_hatch để set thời lượng animation
        self.hatch_animation_duration = self.game.sound_manager.egg_hatch_sound.get_length() * 1000  # chuyển sang ms
        # Phát âm thanh egg_hatch
        self.game.sound_manager.play_egg_hatch()
        self.path = []  # Xóa path để không vẽ

    def start_eaten_animation(self):
        """Bắt đầu animation khi ghost bị ăn"""
        self.eaten = True
        self.eaten_animation_time = 0
        self.just_eaten = True
        self.path = []  # Xóa path để không vẽ


    def start_returning_home(self):
        """Bắt đầu quá trình trở về nhà"""
        self.eaten = False
        self.returning_home = True
        self.reached_home = False
        # Bắt đầu phát âm thanh turn_egg
        self.game.sound_manager.play_turn_egg(loops=-1)  # Lặp vô hạn
        self.path = []  # Xóa path để không vẽ

    def set_speed_multipliers(self):
        level = self.game.level_num
        # Normal speed multiplier
        if level == 1:
            self.normal_speed_multiplier = 0.75
        elif 2 <= level <= 4:
            self.normal_speed_multiplier = 0.85
        else:
            self.normal_speed_multiplier = 0.95

        # TĂNG frightened speed lên
        if level == 1:
            self.frightened_speed_multiplier = 0.8  # Tăng từ 0.5 lên 0.8
        elif 2 <= level <= 4:
            self.frightened_speed_multiplier = 0.85  # Tăng từ 0.55 lên 0.85
        else:
            self.frightened_speed_multiplier = 0.9  # Tăng từ 0.6 lên 0.9

    def start_eating(self):
        """Bắt đầu animation ăn pacman"""
        self.eating = True
        self.eat_animation_time = 0

    def setup_animation_sets(self):
        """Khởi tạo các bộ animation cho ghost theo các hướng"""
        # Tạo animation cho các hướng từ các frame bình thường
        self.normal_animations = {
            'right': self.normal_frames,
            'left': [pygame.transform.flip(frame, True, False) for frame in self.normal_frames],
            'up': [pygame.transform.rotate(frame, 90) for frame in self.normal_frames],
            'down': [pygame.transform.rotate(frame, -90) for frame in self.normal_frames]
        }

        # Tạo animation cho các hướng từ các frame frightened
        self.frightened_animations = {
            'right': self.frightened_frames,
            'left': [pygame.transform.flip(frame, True, False) for frame in self.frightened_frames],
            'up': [pygame.transform.rotate(frame, 90) for frame in self.frightened_frames],
            'down': [pygame.transform.rotate(frame, -90) for frame in self.frightened_frames]
        }

    def reverse_direction(self):
        self.direction = (self.direction + 2) % 4

    def is_elroy(self):
        return False

    def get_base_multiplier(self):
        return self.normal_speed_multiplier

    def update(self, dt):
        self.time += dt  # Cập nhật thời gian animation trước mọi thứ để animation luôn chạy

        if self.hatching:
            self.hatch_animation_time += dt
            if self.hatch_animation_time >= self.hatch_animation_duration:
                self.hatching = False
                # Reset ghost về vị trí ban đầu và trạng thái bình thường
                self.row = self.start_row
                self.col = self.start_col
                self.x = self.col * self.game.num2_c + self.game.num2_c / 2.0
                self.y = self.row * self.game.num1_r + self.game.num1_r / 2.0
                self.direction = 0
                self.frightened_disabled = True  # Vô hiệu hóa frightened cho ghost này sau khi hatch
            return
        if self.returning_home:
            # Kiểm tra nếu đã đến nhà
            if self.row == self.ghost_home[0] and self.col == self.ghost_home[1]:
                if not self.reached_home:
                    self.reached_home = True
                    self.returning_home = False
                    # Dừng âm thanh turn_egg
                    self.game.sound_manager.stop_turn_egg()
                    # Bắt đầu quá trình nở trứng
                    self.start_hatching()
                return

            # Di chuyển về nhà ma bằng BFS - TRUYỀN self vào để kiểm tra điều kiện
            target_r, target_c = self.ghost_home
            self.path = self.game.bfs_finder.find_full_path(self.row, self.col, target_r, target_c, self)

            if self.path and len(self.path) > 1:
                next_r, next_c = self.path[1]
                for dx, dy, d in self.game.bfs_finder.directions:
                    exp_r = self.row + dy
                    exp_c = self.col + dx
                    if dy == 0 and (exp_c < 0 or exp_c >= self.game.col):
                        if self.game.level.is_tunnel_row(self.row):
                            exp_c = exp_c % self.game.col
                            if exp_c < 0:
                                exp_c += self.game.col
                    if exp_r == next_r and exp_c == next_c:
                        self.direction = d
                        break

            # Di chuyển theo hướng đã chọn
            base_mult = self.get_base_multiplier()
            mult = base_mult * 2  # Tăng tốc độ khi về nhà

            current_speed_h = self.game.speed_h * mult
            current_speed_v = self.game.speed_v * mult

            vx = current_speed_h if self.direction == 0 else -current_speed_h if self.direction == 1 else 0
            vy = current_speed_v if self.direction == 3 else -current_speed_v if self.direction == 2 else 0

            proposed_x = self.x + vx * (dt / 1000.0)
            proposed_y = self.y + vy * (dt / 1000.0)

            current_col = int(self.x // self.game.num2_c)
            current_row = int(self.y // self.game.num1_r)
            is_tunnel = self.game.level.is_tunnel_row(current_row)

            if is_tunnel and (self.direction == 0 or self.direction == 1):
                if proposed_x < 0:
                    proposed_x += self.game.width
                elif proposed_x >= self.game.width:
                    proposed_x -= self.game.width

            proposed_col = int(proposed_x // self.game.num2_c)
            proposed_row = int(proposed_y // self.game.num1_r)

            collided = False
            if proposed_col != current_col or proposed_row != current_row:
                # SỬA: Sử dụng hàm kiểm tra tường mới với điều kiện ghost
                if self.game.level.checktuong_for_ghost(proposed_row, proposed_col, self):
                    collided = True

            if collided:
                if vx > 0:
                    proposed_x = min(proposed_x, (current_col + 1) * self.game.num2_c - 0.01)
                elif vx < 0:
                    proposed_x = max(proposed_x, current_col * self.game.num2_c + 0.01)
                if vy > 0:
                    proposed_y = min(proposed_y, (current_row + 1) * self.game.num1_r - 0.01)
                elif vy < 0:
                    proposed_y = max(proposed_y, current_row * self.game.num1_r + 0.01)

            self.x = proposed_x
            self.y = proposed_y

            # Snap to center
            if self.direction in (0, 1):  # horizontal
                self.y = int(self.y // self.game.num1_r) * self.game.num1_r + self.game.num1_r / 2.0
            else:  # vertical
                self.x = int(self.x // self.game.num2_c) * self.game.num2_c + self.game.num2_c / 2.0

            self.col = int(self.x // self.game.num2_c)
            self.row = int(self.y // self.game.num1_r)
            return
        if self.eaten:
            self.eaten_animation_time += dt
            # Khi animation hurt kết thúc, chuyển sang trạng thái về nhà
            if self.eaten_animation_time >= self.eaten_animation_duration:
                self.start_returning_home()
            return # Không di chuyển khi đang bị ăn
        if self.eating and self.game.dying:
            self.eat_animation_time += dt
            return  # Không di chuyển khi đang ăn trong death sequence
        # Nếu đang ăn nhưng game không trong death sequence, thoát trạng thái eating
        if self.eating and not self.game.dying:
            self.eating = False

        # Nếu game vừa reset xong, đợi một chút trước khi tính toán path mới
        if self.game.just_reset:
            return

        # Xử lý delay release khỏi nhà ma
        if self.release_timer > 0:
            self.release_timer -= dt
            return  # Không di chuyển trong lúc delay, chỉ relax animation

        if not self.game.game_started:
            return

        # Determine mode - thêm check frightened_disabled
        frightened_active = self.game.mode_manager.frightened_active and not self.frightened_disabled
        self.mode = 'frightened' if frightened_active else self.game.mode_manager.mode_phases[self.game.mode_manager.current_phase][0]

        # Determine speed multiplier - dựa vào frightened_active
        base_mult = self.get_base_multiplier()

        if frightened_active:
            mult = base_mult * self.frightened_speed_multiplier
        else:
            mult = base_mult

        # Áp dụng hiệu ứng giảm tốc nếu đang trong thời gian sau khi qua tunnel
        tunnel_slowdown = 1.0
        if self.tunnel_slowdown_timer > 0:
            tunnel_slowdown = 0.5  # Giảm 50% tốc độ
            self.tunnel_slowdown_timer -= dt / 1000.0  # Giảm thời gian

        current_speed_h = self.game.speed_h * mult * tunnel_slowdown
        current_speed_v = self.game.speed_v * mult * tunnel_slowdown

        # Get velocity
        vx = current_speed_h if self.direction == 0 else -current_speed_h if self.direction == 1 else 0
        vy = current_speed_v if self.direction == 3 else -current_speed_v if self.direction == 2 else 0

        proposed_x = self.x + vx * (dt / 1000.0)
        proposed_y = self.y + vy * (dt / 1000.0)

        current_col = int(self.x // self.game.num2_c)
        current_row = int(self.y // self.game.num1_r)

        is_tunnel = self.game.level.is_tunnel_row(current_row)
        self.just_teleported = False

        # Xử lý tunnel cho ghost - làm chậm quá trình teleport
        if is_tunnel and (self.direction == 0 or self.direction == 1):
            if proposed_x < 0:
                # Ghost đi ra khỏi biên trái
                if self.tunnel_slowdown_timer <= 0:
                    proposed_x += self.game.width
                    self.just_teleported = True
                else:
                    # Nếu đang trong thời gian giảm tốc, không cho teleport ngay
                    proposed_x = 0
            elif proposed_x >= self.game.width:
                # Ghost đi ra khỏi biên phải
                if self.tunnel_slowdown_timer <= 0:
                    proposed_x -= self.game.width
                    self.just_teleported = True
                else:
                    # Nếu đang trong thời gian giảm tốc, không cho teleport ngay
                    proposed_x = self.game.width - 1

        # Kích hoạt hiệu ứng giảm tốc khi ghost vừa teleport
        if self.just_teleported:
            self.tunnel_slowdown_timer = self.tunnel_slowdown_duration

        proposed_col = int(proposed_x // self.game.num2_c)
        proposed_row = int(proposed_y // self.game.num1_r)

        collided = False
        if proposed_col != current_col or proposed_row != current_row:
            if self.game.level.checktuong_for_ghost(proposed_row, proposed_col, self):
                collided = True

        if collided:
            if vx > 0:
                proposed_x = min(proposed_x, (current_col + 1) * self.game.num2_c - 0.01)
            elif vx < 0:
                proposed_x = max(proposed_x, current_col * self.game.num2_c + 0.01)
            if vy > 0:
                proposed_y = min(proposed_y, (current_row + 1) * self.game.num1_r - 0.01)
            elif vy < 0:
                proposed_y = max(proposed_y, current_row * self.game.num1_r + 0.01)
            self.choose_direction()

        self.x = proposed_x
        self.y = proposed_y

        # Snap to center
        if self.direction in (0, 1):  # horizontal
            self.y = int(self.y // self.game.num1_r) * self.game.num1_r + self.game.num1_r / 2.0
        else:  # vertical
            self.x = int(self.x // self.game.num2_c) * self.game.num2_c + self.game.num2_c / 2.0

        self.col = int(self.x // self.game.num2_c)
        self.row = int(self.y // self.game.num1_r)

        # Choose new direction at center
        center_x = self.col * self.game.num2_c + self.game.num2_c / 2.0
        center_y = self.row * self.game.num1_r + self.game.num1_r / 2.0
        if abs(self.x - center_x) < 1.0 and abs(self.y - center_y) < 1.0:
            self.x = center_x
            self.y = center_y
            self.choose_direction()

    def choose_direction(self):
        # Determine mode lại (để chắc chắn) - thêm check frightened_disabled
        frightened_active = self.game.mode_manager.frightened_active and not self.frightened_disabled
        self.mode = 'frightened' if frightened_active else self.game.mode_manager.mode_phases[self.game.mode_manager.current_phase][0]

        if self.mode == 'frightened':
            self._choose_frightened_direction()
        elif self.mode == 'chase' or self.is_elroy():
            self._choose_chase_direction()
        else:
            self._choose_scatter_direction()

    def _choose_frightened_direction(self):
        valid_dirs = []

        for dx, dy, d in self.game.bfs_finder.directions:
            next_row = self.row + dy
            next_col = self.col + dx

            # Xử lý tunnel - cho phép đi vào tunnel trong frightened mode
            if dy == 0 and (next_col < 0 or next_col >= self.game.col):
                if self.game.level.is_tunnel_row(self.row):
                    next_col = next_col % self.game.col
                    if next_col < 0:
                        next_col += self.game.col
                else:
                    continue

            # Kiểm tra ô hợp lệ - CHỈ kiểm tra tường, không cấm tunnel
            if (0 <= next_row < self.game.row and 0 <= next_col < self.game.col and
                    not self.game.level.checktuong_for_ghost(next_row, next_col, self)):
                valid_dirs.append(d)

        if valid_dirs:
            # Ưu tiên các hướng không phải là quay đầu
            reverse_dir = (self.direction + 2) % 4
            preferred_dirs = [d for d in valid_dirs if d != reverse_dir]

            # Nếu có hướng ưu tiên (không quay đầu), sắp xếp theo thứ tự ưu tiên: trái > phải > thẳng
            if preferred_dirs:
                # Xác định các hướng rẽ trái, rẽ phải, đi thẳng
                left_turn = None
                right_turn = None
                straight = self.direction

                if self.direction == 0:  # right
                    left_turn = 2  # up
                    right_turn = 3  # down
                elif self.direction == 1:  # left
                    left_turn = 3  # down
                    right_turn = 2  # up
                elif self.direction == 2:  # up
                    left_turn = 1  # left
                    right_turn = 0  # right
                elif self.direction == 3:  # down
                    left_turn = 0  # right
                    right_turn = 1  # left

                # Ưu tiên: rẽ trái -> rẽ phải -> đi thẳng -> các hướng khác
                if left_turn in preferred_dirs:
                    self.direction = left_turn
                elif right_turn in preferred_dirs:
                    self.direction = right_turn
                elif straight in preferred_dirs:
                    self.direction = straight
                else:
                    # Chọn ngẫu nhiên trong preferred_dirs
                    self.direction = random.choice(preferred_dirs)
            else:
                # Nếu không có hướng nào khác ngoài quay đầu, thì quay đầu
                self.direction = reverse_dir
        else:
            # Fallback: nếu không có hướng nào, quay ngược lại
            self.direction = (self.direction + 2) % 4

    @abstractmethod
    def get_chase_target(self):
        """Abstract method to get the chase target tile based on ghost-specific behavior."""
        pass

    @abstractmethod
    def get_scatter_target(self):
        """Abstract method to get the scatter target tile or cycle."""
        pass

    def _choose_chase_direction(self):
        # Dùng BFS để đuổi đến target cụ thể của ghost
        target_r, target_c = self.get_chase_target()
        self.path = self.game.bfs_finder.find_full_path(self.row, self.col, target_r, target_c, self)

        if self.path and len(self.path) > 1:
            next_r, next_c = self.path[1]
            found_direction = None
            for dx, dy, d in self.game.bfs_finder.directions:
                exp_r = self.row + dy
                exp_c = self.col + dx
                if dy == 0 and (exp_c < 0 or exp_c >= self.game.col):
                    if self.game.level.is_tunnel_row(self.row):
                        exp_c = exp_c % self.game.col
                        if exp_c < 0:
                            exp_c += self.game.col
                if exp_r == next_r and exp_c == next_c:
                    found_direction = d
                    break
            # Chỉ đổi hướng nếu hướng hiện tại không dẫn đến ô tiếp theo
            if found_direction is not None:
                current_dir_leads_to_next = False
                for dx, dy, d in self.game.bfs_finder.directions:
                    if d == self.direction:
                        exp_r = self.row + dy
                        exp_c = self.col + dx
                        if dy == 0 and (exp_c < 0 or exp_c >= self.game.col):
                            if self.game.level.is_tunnel_row(self.row):
                                exp_c = exp_c % self.game.col
                                if exp_c < 0:
                                    exp_c += self.game.col
                        if exp_r == next_r and exp_c == next_c:
                            current_dir_leads_to_next = True
                            break

                if not current_dir_leads_to_next:
                    self.direction = found_direction

    def _choose_scatter_direction(self):
        # Lấy target scatter cụ thể của ghost
        target_r, target_c = self.get_scatter_target()

        # Dùng BFS để đi đến điểm mục tiêu scatter
        self.path = self.game.bfs_finder.find_full_path(self.row, self.col, target_r, target_c, self)

        if self.path and len(self.path) > 1:
            next_r, next_c = self.path[1]
            for dx, dy, d in self.game.bfs_finder.directions:
                exp_r = self.row + dy
                exp_c = self.col + dx
                if dy == 0 and (exp_c < 0 or exp_c >= self.game.col):
                    if self.game.level.is_tunnel_row(self.row):
                        exp_c = exp_c % self.game.col
                        if exp_c < 0:
                            exp_c += self.game.col
                if exp_r == next_r and exp_c == next_c:
                    self.direction = d
                    break
        else:
            # Fallback: nếu không tìm được đường, di chuyển ngẫu nhiên
            valid_dirs = []
            for dx, dy, d in self.game.bfs_finder.directions:
                # Không quay ngược lại
                if d == (self.direction + 2) % 4:
                    continue

                next_row = self.row + dy
                next_col = self.col + dx
                if dy == 0 and (next_col < 0 or next_col >= self.game.col):
                    if self.game.level.is_tunnel_row(self.row):
                        next_col = next_col % self.game.col
                        if next_col < 0:
                            next_col += self.game.col
                    else:
                        continue
                if 0 <= next_row < self.game.row and 0 <= next_col < self.game.col and not self.game.level.checktuong_for_ghost(
                        next_row, next_col, self):
                    valid_dirs.append(d)

            if valid_dirs:
                self.direction = random.choice(valid_dirs)

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

    def draw_path(self):
        if (not self.path or self.game.mode_manager.frightened_active or
                self.game.dying or self.game.just_reset or
                self.eaten or self.returning_home or self.hatching):  # Thêm điều kiện để không vẽ path khi ở trạng thái đặc biệt
            return
        prev_x = self.x
        prev_y = self.y + self.game.y_offset
        prev_r, prev_c = self.row, self.col
        line_width = 2
        for r, c in self.path[1:]:
            x = c * self.game.num2_c + self.game.num2_c / 2.0
            y = r * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset
            dc = c - prev_c
            dr = r - prev_r
            if abs(dc) > 1 and dr == 0:  # horizontal wrap
                if dc > 0:
                    pygame.draw.line(self.game.screen, self.color, (prev_x, prev_y), (0, prev_y), line_width)
                    pygame.draw.line(self.game.screen, self.color, (self.game.width, y), (x, y), line_width)
                else:
                    pygame.draw.line(self.game.screen, self.color, (prev_x, prev_y), (self.game.width, prev_y),
                                     line_width)
                    pygame.draw.line(self.game.screen, self.color, (0, y), (x, y), line_width)
            else:
                pygame.draw.line(self.game.screen, self.color, (prev_x, prev_y), (x, y), line_width)
            prev_x = x
            prev_y = y
            prev_r, prev_c = r, c

        # Draw arrow at end
        if len(self.path) >= 2:
            prev_r, prev_c = self.path[-2]
            last_r, last_c = self.path[-1]
            last_x = last_c * self.game.num2_c + self.game.num2_c / 2.0
            last_y = last_r * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset
            for dx, dy, d in self.game.bfs_finder.directions:
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
            pygame.draw.line(self.game.screen, self.color, tip, base1, line_width)
            pygame.draw.line(self.game.screen, self.color, tip, base2, line_width)