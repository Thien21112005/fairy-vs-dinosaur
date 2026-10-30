import random

# Hướng rẽ theo hướng hiện tại: direction -> (rẽ trái, rẽ phải)
TURNS = {0: (2, 3), 1: (3, 2), 2: (1, 0), 3: (0, 1)}
# Hướng ngược lại: 0 phải <-> 1 trái, 2 lên <-> 3 xuống
OPPOSITE = {0: 1, 1: 0, 2: 3, 3: 2}


class GhostMovementMixin:
    """Trạng thái di chuyển và chọn hướng của ghost."""

    def update(self, dt):
        self.time += dt  # Animation luôn chạy

        if self.hatching:
            self._update_hatching(dt)
            return
        if self.returning_home:
            self._update_returning_home(dt)
            return
        if self.eaten:
            self.eaten_animation_time += dt
            if self.eaten_animation_time >= self.eaten_animation_duration:
                self.start_returning_home()
            return
        if self.eating:
            if self.game.dying:
                self.eat_animation_time += dt
                return
            self.eating = False

        if self.game.just_reset:
            return

        if self.release_timer > 0:
            self.release_timer -= dt
            return

        if self.game.game_started:
            self._update_roaming(dt)

    def _update_hatching(self, dt):
        self.hatch_animation_time += dt
        if self.hatch_animation_time >= self.hatch_animation_duration:
            self.hatching = False
            self.row = self.start_row
            self.col = self.start_col
            self.x = self.col * self.game.num2_c + self.game.num2_c / 2.0
            self.y = self.row * self.game.num1_r + self.game.num1_r / 2.0
            self.direction = 0
            self.decided_cell = None
            self.frightened_disabled = True

    def _update_returning_home(self, dt):
        if (self.row, self.col) == self.ghost_home:
            if not self.reached_home:
                self.reached_home = True
                self.returning_home = False
                self.game.sound_manager.stop_turn_egg()
                self.start_hatching()
            return

        self.path = self.game.bfs_finder.find_full_path(self.row, self.col, *self.ghost_home, self)
        self._face_next_path_cell()

        vx, vy = self._velocity(self.get_base_multiplier() * 2)
        proposed_x = self.x + vx * (dt / 1000.0)
        proposed_y = self.y + vy * (dt / 1000.0)
        current_col = int(self.x // self.game.num2_c)
        current_row = int(self.y // self.game.num1_r)

        if self.game.level.is_tunnel_row(current_row) and self.direction in (0, 1):
            if proposed_x < 0:
                proposed_x += self.game.width
            elif proposed_x >= self.game.width:
                proposed_x -= self.game.width

        self._advance(vx, vy, proposed_x, proposed_y, current_col, current_row, turn_on_collision=False)

    def _update_roaming(self, dt):
        frightened_active = self._frightened_active()
        self.mode = self._current_mode(frightened_active)

        mult = self.get_base_multiplier()
        if frightened_active:
            mult = mult * self.frightened_speed_multiplier

        tunnel_slowdown = 1.0
        if self.tunnel_slowdown_timer > 0:
            tunnel_slowdown = 0.5
            self.tunnel_slowdown_timer -= dt / 1000.0

        vx, vy = self._velocity(mult, tunnel_slowdown)
        proposed_x = self.x + vx * (dt / 1000.0)
        proposed_y = self.y + vy * (dt / 1000.0)
        current_col = int(self.x // self.game.num2_c)
        current_row = int(self.y // self.game.num1_r)

        proposed_x = self._apply_tunnel(proposed_x, current_row)
        self._advance(vx, vy, proposed_x, proposed_y, current_col, current_row, turn_on_collision=True)
        self._decide_at_cell_center(max(abs(vx), abs(vy)) * (dt / 1000.0))

    def _decide_at_cell_center(self, step):
        """Chọn hướng đúng một lần mỗi ô, khi tới tâm ô, không phụ thuộc tốc độ hay thời gian khung hình."""
        cell = (self.row, self.col)
        if cell == self.decided_cell:
            return
        center_x = self.col * self.game.num2_c + self.game.num2_c / 2.0
        center_y = self.row * self.game.num1_r + self.game.num1_r / 2.0
        if abs(self.x - center_x) <= step and abs(self.y - center_y) <= step:
            self.x = center_x
            self.y = center_y
            self.decided_cell = cell
            self.choose_direction()

    def _frightened_active(self):
        return self.game.mode_manager.frightened_active and not self.frightened_disabled

    def _current_mode(self, frightened_active):
        manager = self.game.mode_manager
        return 'frightened' if frightened_active else manager.mode_phases[manager.current_phase][0]

    def _velocity(self, mult, slowdown=1.0):
        speed_h = self.game.speed_h * mult * slowdown
        speed_v = self.game.speed_v * mult * slowdown
        vx = speed_h if self.direction == 0 else -speed_h if self.direction == 1 else 0
        vy = speed_v if self.direction == 3 else -speed_v if self.direction == 2 else 0
        return vx, vy

    def _apply_tunnel(self, proposed_x, current_row):
        """Xuyên đường hầm rồi đi chậm lại một lúc."""
        if self.game.level.is_tunnel_row(current_row) and self.direction in (0, 1):
            if proposed_x < 0:
                proposed_x += self.game.width
                self.tunnel_slowdown_timer = self.tunnel_slowdown_duration
            elif proposed_x >= self.game.width:
                proposed_x -= self.game.width
                self.tunnel_slowdown_timer = self.tunnel_slowdown_duration
        return proposed_x

    def _advance(self, vx, vy, proposed_x, proposed_y, current_col, current_row, turn_on_collision):
        """Di chuyển tới vị trí đề xuất, chặn lại nếu đụng tường rồi bám vào tâm hàng hoặc cột."""
        num_c, num_r = self.game.num2_c, self.game.num1_r
        proposed_col = int(proposed_x // num_c)
        proposed_row = int(proposed_y // num_r)

        if (proposed_col != current_col or proposed_row != current_row) and \
                self.game.level.checktuong_for_ghost(proposed_row, proposed_col, self):
            if vx > 0:
                proposed_x = min(proposed_x, (current_col + 1) * num_c - 0.01)
            elif vx < 0:
                proposed_x = max(proposed_x, current_col * num_c + 0.01)
            if vy > 0:
                proposed_y = min(proposed_y, (current_row + 1) * num_r - 0.01)
            elif vy < 0:
                proposed_y = max(proposed_y, current_row * num_r + 0.01)
            if turn_on_collision:
                self.choose_direction()

        self.x = proposed_x
        self.y = proposed_y

        if self.direction in (0, 1):
            self.y = int(self.y // num_r) * num_r + num_r / 2.0
        else:
            self.x = int(self.x // num_c) * num_c + num_c / 2.0

        self.col = int(self.x // num_c)
        self.row = int(self.y // num_r)

    def choose_direction(self):
        self.mode = self._current_mode(self._frightened_active())

        if self.mode == 'frightened':
            self._choose_frightened_direction()
        elif self.mode == 'chase' or self.is_elroy():
            self._choose_chase_direction()
        else:
            self._choose_scatter_direction()

    def _open_directions(self):
        finder = self.game.bfs_finder
        directions = []
        for dx, dy, d in finder.directions:
            next_pos = finder.wrap_step(self.row, self.col, dx, dy)
            if next_pos is not None and not self.game.level.checktuong_for_ghost(*next_pos, self):
                directions.append(d)
        return directions

    def _choose_frightened_direction(self):
        reverse_dir = OPPOSITE[self.direction]
        preferred_dirs = [d for d in self._open_directions() if d != reverse_dir]

        # Ưu tiên rẽ trái, rẽ phải, đi thẳng; không còn cách nào mới quay đầu
        left_turn, right_turn = TURNS[self.direction]
        for candidate in (left_turn, right_turn, self.direction):
            if candidate in preferred_dirs:
                self.direction = candidate
                return
        self.direction = reverse_dir

    def _face_next_path_cell(self):
        """Quay về phía ô kế tiếp trên path. Trả về False nếu không có ô kế tiếp."""
        if not self.path or len(self.path) <= 1:
            return False
        step = self.game.bfs_finder.step_between(self.row, self.col, *self.path[1])
        if step:
            self.direction = step[2]
        return True

    def _choose_chase_direction(self):
        self._head_towards(self.game.level.nearest_open_cell(*self.get_chase_target()))

    def _choose_scatter_direction(self):
        self._head_towards(self.get_scatter_target())

    def _head_towards(self, target):
        self.path = self.game.bfs_finder.find_full_path(self.row, self.col, *target, self)

        if not self._face_next_path_cell():
            # Đã tới mục tiêu hoặc không có đường: đi ngẫu nhiên nhưng không quay đầu nếu còn lối khác
            open_dirs = self._open_directions()
            valid_dirs = [d for d in open_dirs if d != OPPOSITE[self.direction]] or open_dirs
            if valid_dirs:
                self.direction = random.choice(valid_dirs)
