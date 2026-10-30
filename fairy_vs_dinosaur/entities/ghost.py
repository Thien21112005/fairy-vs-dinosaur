from abc import ABC, abstractmethod

import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.entities.ghost_movement import GhostMovementMixin, OPPOSITE
from fairy_vs_dinosaur.entities.ghost_render import GhostRenderMixin


def directional(frames):
    """animations[direction][frame]: direction 0 phải, 1 trái, 2 lên, 3 xuống"""
    return [
        frames,
        [pygame.transform.flip(frame, True, False) for frame in frames],
        [pygame.transform.rotate(frame, 90) for frame in frames],
        [pygame.transform.rotate(frame, -90) for frame in frames],
    ]


class Ghost(GhostMovementMixin, GhostRenderMixin, ABC):
    GHOST_SCALE = 2.2

    def __init__(self, game, name, start_row, start_col, color, home=(15, 14), release_delay=0):
        self.game = game
        self.name = name
        self.color = color  # Màu vẽ đường đi
        self.start_row = start_row
        self.start_col = start_col
        self.row = start_row
        self.col = start_col
        self.x = self.col * self.game.num2_c + self.game.num2_c / 2.0
        self.y = self.row * self.game.num1_r + self.game.num1_r / 2.0
        self.direction = 0
        self.mode = None
        self.path = []
        self.ghost_home = home

        ghost_size = int(min(self.game.num2_c, self.game.num1_r) * self.GHOST_SCALE)
        self.ghost_w = ghost_size
        self.ghost_h = ghost_size

        self.set_speed_multipliers()
        self._load_animations()

        self.time = 0.0
        self.animation_speed = 100  # ms mỗi frame
        self.flash_interval = 150  # ms mỗi lần nhấp nháy
        self.flash_start_time = 2000  # Nhấp nháy khi frightened còn 2 giây (ms)

        self.tunnel_slowdown_timer = 0.0
        self.tunnel_slowdown_duration = 1.5  # giây
        self.decided_cell = None  # Ô đã quyết định hướng đi

        self.eating = False
        self.eat_animation_time = 0
        self.eat_animation_duration = 600  # ms
        self.eaten = False
        self.eaten_animation_time = 0
        self.eaten_animation_duration = 800  # ms
        self.returning_home = False
        self.reached_home = False
        self.hatching = False
        self.hatch_animation_time = 0
        self.hatch_animation_duration = 0  # Lấy theo độ dài âm thanh nở trứng
        self.frightened_disabled = False  # Ghost vừa nở không bị frightened nữa

        self.release_delay = release_delay  # ms chờ trước khi rời nhà
        self.release_timer = release_delay

    def _load_frames(self, folder, pattern, count):
        size = (self.ghost_w, self.ghost_h)
        paths = [asset(f"images/dinosaurs/{self.name}/{folder}/{pattern}{i}.png") for i in range(count)]
        return [pygame.transform.smoothscale(pygame.image.load(p).convert_alpha(), size) for p in paths]

    def _load_animations(self):
        self.normal_animations = directional(self._load_frames("normal", "tile00", 6))
        self.frightened_animations = directional(self._load_frames("frightened", "tile00", 4))
        self.eat_animations = directional(self._load_frames("eat", "tile00", 3))
        self.hurt_animations = directional(self._load_frames("hurt", "00", 4))
        self.turnegg_frames = self._load_frames("turn_egg", "00", 4)
        self.hatchegg_frames = self._load_frames("hatch_egg", "00", 8)
        self.relax_frames = self._load_frames("relax", "tile00", 3)

        flash = pygame.image.load(asset("images/dinosaurs/flash.png")).convert_alpha()
        flash = pygame.transform.smoothscale(flash, (self.ghost_w, self.ghost_h))
        self.flash_animations = directional([flash])

    def set_speed_multipliers(self):
        level = self.game.level_num
        if level == 1:
            self.normal_speed_multiplier = 0.75
            self.frightened_speed_multiplier = 0.8
        elif level <= 4:
            self.normal_speed_multiplier = 0.85
            self.frightened_speed_multiplier = 0.85
        else:
            self.normal_speed_multiplier = 0.95
            self.frightened_speed_multiplier = 0.9

    def reset_to_start(self):
        """Đưa ghost về vị trí xuất phát và xóa mọi trạng thái đặc biệt"""
        self.row = self.start_row
        self.col = self.start_col
        self.x = self.col * self.game.num2_c + self.game.num2_c / 2.0
        self.y = self.row * self.game.num1_r + self.game.num1_r / 2.0
        self.direction = 0
        self.path = []
        self.eating = False
        self.eat_animation_time = 0
        self.eaten = False
        self.returning_home = False
        self.reached_home = False
        self.hatching = False
        self.frightened_disabled = False
        self.tunnel_slowdown_timer = 0.0
        self.decided_cell = None
        self.release_timer = self.release_delay

    def apply_level_difficulty(self):
        self.set_speed_multipliers()

    def start_hatching(self):
        self.hatching = True
        self.hatch_animation_time = 0
        self.hatch_animation_duration = self.game.sound_manager.egg_hatch_sound.get_length() * 1000
        self.game.sound_manager.play_egg_hatch()
        self.path = []

    def start_eaten_animation(self):
        self.eaten = True
        self.eaten_animation_time = 0
        self.path = []

    def start_returning_home(self):
        self.eaten = False
        self.returning_home = True
        self.reached_home = False
        self.game.sound_manager.play_turn_egg(loops=-1)
        self.path = []

    def start_eating(self):
        self.eating = True
        self.eat_animation_time = 0

    def reverse_direction(self):
        self.direction = OPPOSITE[self.direction]

    def is_elroy(self):
        return False

    def get_base_multiplier(self):
        return self.normal_speed_multiplier

    @abstractmethod
    def get_chase_target(self):
        """Ô mục tiêu khi đuổi, riêng theo từng ghost."""

    def _next_in_scatter_cycle(self):
        """Điểm tiếp theo trong vòng tuần tra, None nếu ghost đang ở ngoài vòng."""
        position = (self.row, self.col)
        if position in self.scatter_cycle:
            return self.scatter_cycle[(self.scatter_cycle.index(position) + 1) % len(self.scatter_cycle)]
        return None

    def get_scatter_target(self):
        return self._next_in_scatter_cycle() or self.scatter_cycle[0]
