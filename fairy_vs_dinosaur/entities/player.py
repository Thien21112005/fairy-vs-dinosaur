import random

import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.entities.path_drawing import blit_wrapped, draw_arrow_head, LINE_WIDTH
from fairy_vs_dinosaur.ui.theme import PATH_FAIRY
from fairy_vs_dinosaur.ui.widgets import scale_pixel_art

START_ROW = 24
START_COL = 15


class Player:
    def __init__(self, game):
        self.game = game
        self.pac_w = int(min(self.game.num2_c, self.game.num1_r) * 2)
        self.pac_h = self.pac_w

        # animations[direction][frame]: direction 0 phải, 1 trái, 2 lên, 3 xuống
        self.normal_animations = self._load_animations("blue")
        self.powered_animations = self._load_animations("red")
        self.frame = len(self.normal_animations[0])

        self.time = 0.0
        self.moved = False
        self.dead = False
        self.death_frame = None
        self.ai_path = []
        self.place_at_start()

    def _load_animations(self, color):
        raw = [pygame.image.load(asset(f"images/fairy/{color}/tile00{i}.png")).convert_alpha() for i in range(8)]
        size = (self.pac_w, self.pac_h)
        right = [scale_pixel_art(img, size) for img in raw]
        return [
            right,
            [pygame.transform.flip(img, True, False) for img in right],
            [pygame.transform.rotate(img, 90) for img in right],
            [pygame.transform.rotate(img, -90) for img in right],
        ]

    def place_at_start(self):
        self.row = START_ROW
        self.col = START_COL
        self.x = self.col * self.game.num2_c + self.game.num2_c / 2.0
        self.y = self.row * self.game.num1_r + self.game.num1_r / 2.0
        self.direction = 0
        self.requested_direction = -1
        self.decided_cell = None  # Ô mà AI đã quyết định hướng đi

    def _current_animations(self):
        return self.powered_animations if self.game.mode_manager.frightened_active else self.normal_animations

    def find_next_pellet_target(self):
        self.ai_path = self.game.path_finder.find_path_to_nearest_pellet(self.row, self.col) or []

    def update(self, dt):
        if self.dead or not self.game.game_started:
            return
        self.time += dt
        if self.time >= self.game.frame_ms * self.frame:
            self.time %= self.game.frame_ms * self.frame

        if self.game.ai_mode:
            self._update_ai_direction(dt)

        self._apply_requested_direction()
        self._move(dt)
        self._collect_pellet()

        # Sang ô kế tiếp của path thì ô đó thành điểm đầu mới
        if self.game.ai_mode and len(self.ai_path) > 1 and (self.row, self.col) == self.ai_path[1]:
            self.ai_path = self.ai_path[1:]

    def _update_ai_direction(self, dt):
        """Quyết định hướng đi đúng một lần mỗi ô, khi tới tâm ô, không phụ thuộc thời gian khung hình."""
        cell = (self.row, self.col)
        if self.moved and cell == self.decided_cell:
            return

        center_x = self.col * self.game.num2_c + self.game.num2_c / 2.0
        center_y = self.row * self.game.num1_r + self.game.num1_r / 2.0
        reach = max(self.game.speed_h, self.game.speed_v) * (dt / 1000.0)
        if self.moved and (abs(self.x - center_x) > reach or abs(self.y - center_y) > reach):
            return

        self.x = center_x
        self.y = center_y
        self.decided_cell = cell

        if self.game.path_finder.REPLAN_EACH_CELL or not self._is_following_path():
            self.find_next_pellet_target()

        if len(self.ai_path) > 1:
            step = self.game.path_finder.step_between(self.row, self.col, *self.ai_path[1])
            if step:
                self.requested_direction = step[2]
        elif not self.ai_path:
            self._choose_random_direction()

    def _is_following_path(self):
        if len(self.ai_path) < 2 or self.ai_path[0] != (self.row, self.col):
            return False
        return not self.game.level.checktuong_for_pacman(*self.ai_path[1])

    def _choose_random_direction(self):
        """Không tìm được đường: chọn ngẫu nhiên một hướng đi được để thoát kẹt."""
        valid_directions = [d for dx, dy, d in self.game.path_finder.directions
                            if not self.game.level.checktuong_for_pacman(self.row + dy, self.col + dx)]
        if valid_directions:
            self.requested_direction = random.choice(valid_directions)

    def _apply_requested_direction(self):
        if self.requested_direction != -1 and self.requested_direction != self.direction:
            dy = 1 if self.requested_direction == 3 else -1 if self.requested_direction == 2 else 0
            dx = 1 if self.requested_direction == 0 else -1 if self.requested_direction == 1 else 0
            if not self.game.level.checktuong_for_pacman(self.row + dy, self.col + dx):
                self.direction = self.requested_direction
                self.requested_direction = -1

    def _move(self, dt):
        num_c, num_r = self.game.num2_c, self.game.num1_r
        vx = self.game.speed_h if self.direction == 0 else -self.game.speed_h if self.direction == 1 else 0
        vy = self.game.speed_v if self.direction == 3 else -self.game.speed_v if self.direction == 2 else 0

        proposed_x = self.x + vx * (dt / 1000.0)
        proposed_y = self.y + vy * (dt / 1000.0)

        current_col = int(self.x // num_c)
        current_row = int(self.y // num_r)

        if self.game.level.is_tunnel_row(current_row) and self.direction in (0, 1):
            if proposed_x < 0:
                proposed_x += self.game.width
            elif proposed_x >= self.game.width:
                proposed_x -= self.game.width

        proposed_col = int(proposed_x // num_c)
        proposed_row = int(proposed_y // num_r)

        if proposed_col != current_col or proposed_row != current_row:
            if self.game.level.checktuong_for_pacman(proposed_row, proposed_col):
                if vx > 0:
                    proposed_x = min(proposed_x, (current_col + 1) * num_c - 0.01)
                elif vx < 0:
                    proposed_x = max(proposed_x, current_col * num_c + 0.01)
                if vy > 0:
                    proposed_y = min(proposed_y, (current_row + 1) * num_r - 0.01)
                elif vy < 0:
                    proposed_y = max(proposed_y, current_row * num_r + 0.01)

        old_x, old_y = self.x, self.y
        self.x = proposed_x
        self.y = proposed_y

        # Bám vào tâm hàng hoặc cột theo hướng đang đi
        if self.direction in (0, 1):
            self.y = int(self.y // num_r) * num_r + num_r / 2.0
        else:
            self.x = int(self.x // num_c) * num_c + num_c / 2.0

        old_cell = (self.row, self.col)
        self.col = int(self.x // num_c)
        self.row = int(self.y // num_r)
        if self.game.ai_mode and (self.row, self.col) != old_cell:
            self.game.metrics['path_length'] += 1
        self.moved = abs(self.x - old_x) > 0.001 or abs(self.y - old_y) > 0.001

    def _collect_pellet(self):
        level = self.game.level
        cell = level.level[self.row][self.col]
        if cell == 1:
            self.game.score += 10
            level.level[self.row][self.col] = 0
            level.remaining_pellets -= 1
            sounds = self.game.sound_manager
            (sounds.pellet_sound1 if sounds.pellet_toggle == 0 else sounds.pellet_sound2).play()
            sounds.pellet_toggle = 1 - sounds.pellet_toggle
        elif cell == 2:
            self.game.score += 50
            level.level[self.row][self.col] = 0
            level.remaining_pellets -= 1
            self.game.mode_manager.activate_frightened()

    def die(self):
        self.dead = True
        self.death_frame = self._current_animations()[self.direction][3]  # Frame mở miệng lớn

    def draw(self):
        if self.dead:
            img = self.death_frame
        else:
            frame_i = int(self.time / self.game.frame_ms) % self.frame if self.moved else 3
            img = self._current_animations()[self.direction][frame_i]
        blit_wrapped(self.game.screen, img, self.x - self.pac_w / 2.0, self.y + self.game.y_offset - self.pac_h / 2.0)

    def _cell_center(self, r, c):
        return (c * self.game.num2_c + self.game.num2_c / 2.0,
                r * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset)

    def draw_path(self):
        if not self.ai_path:
            return

        prev = (self.x, self.y + self.game.y_offset)
        prev_r, prev_c = self.row, self.col
        for r, c in self.ai_path:
            point = self._cell_center(r, c)
            # Bỏ qua ô hiện tại và đoạn xuyên đường hầm
            is_wrap = abs(c - prev_c) > 1 and r == prev_r
            if (r, c) != (self.row, self.col) and not is_wrap:
                pygame.draw.line(self.game.screen, PATH_FAIRY, prev, point, LINE_WIDTH)
            prev = point
            prev_r, prev_c = r, c

        valid_path = [pos for pos in self.ai_path if pos != (self.row, self.col)]
        if len(self.ai_path) >= 2 and len(valid_path) >= 2:
            step = self.game.path_finder.step_between(*valid_path[-2], *valid_path[-1])
            if step:
                size = min(self.game.num1_r, self.game.num2_c) / 2
                draw_arrow_head(self.game.screen, PATH_FAIRY, self._cell_center(*valid_path[-1]), step[0], step[1], size)

    def clear_path(self):
        self.ai_path = []

    def reset(self):
        """Đưa player về trạng thái ban đầu của màn chơi"""
        self.place_at_start()
        self.time = 0.0
        self.moved = False
        self.dead = False
        self.death_frame = None
        self.ai_path = []
