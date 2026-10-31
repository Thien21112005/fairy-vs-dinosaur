import math

import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.core.board import boards
from fairy_vs_dinosaur.core.board_art import build_board_surface, build_glow_frames, scale_tiles
from fairy_vs_dinosaur.ui import theme

WALLS = {3, 4, 5, 6, 7, 8, 9}  # 9 là cổng nhà ma
GHOST_GATE = 9
GHOST_HOUSE_ROWS = range(14, 17)
GHOST_HOUSE_COLS = range(12, 18)
PELLET = 1
POWER_PELLET = 2
GLOW_PERIOD_MS = 900


class Level:
    def __init__(self, game):
        self.game = game
        item_raw = [pygame.image.load(asset(f"images/tiles/{i}.png")).convert_alpha() for i in range(1, 10)]
        self.item = scale_tiles(item_raw, (self.game.num2_c, self.game.num1_r))
        self.power_glow = build_glow_frames((self.game.num2_c * 3, self.game.num1_r * 3), theme.EMBER)
        self.load_board(boards)

    def render_static_board(self, brick):
        """Sàn và tường không đổi trong suốt màn chơi nên chỉ dựng một lần."""
        size = (self.game.num2_c * self.game.col, self.game.num1_r * self.game.row)
        return build_board_surface(brick, boards, self.item, size, self.game.num2_c, self.game.num1_r)

    def load_board(self, board_data):
        self.level = [row[:] for row in board_data]
        self.initial_pellets = sum(1 for row in self.level for cell in row if cell in [1, 2])
        self.remaining_pellets = self.initial_pellets

    def draw_board(self):
        screen = self.game.screen
        cell_w, cell_h = self.game.num2_c, self.game.num1_r
        pulse = (math.sin(pygame.time.get_ticks() * 2 * math.pi / GLOW_PERIOD_MS) + 1) / 2
        glow = self.power_glow[int(pulse * (len(self.power_glow) - 1))]
        for i, row in enumerate(self.level):
            for j, v in enumerate(row):
                if v == PELLET or v == POWER_PELLET:
                    x, y = j * cell_w, i * cell_h + self.game.y_offset
                    if v == POWER_PELLET:
                        screen.blit(glow, (x - cell_w, y - cell_h), special_flags=pygame.BLEND_RGB_ADD)
                    screen.blit(self.item[v - 1], (x, y))

    def _in_bounds(self, r, c):
        return 0 <= r < self.game.row and 0 <= c < self.game.col

    def checktuong_for_ghost(self, r, c, ghost=None):
        if not self._in_bounds(r, c):
            return True
        cell_value = self.level[r][c]
        if cell_value == GHOST_GATE:
            return not (ghost and (ghost.returning_home or ghost.mode != 'frightened'))
        return cell_value in WALLS

    def checktuong_for_pacman(self, r, c):
        if not self._in_bounds(r, c) or self.level[r][c] in WALLS:
            return True

        for ghost in self.game.visible_ghosts():
            if not ghost.is_vulnerable() and not ghost.eaten and not ghost.returning_home \
                    and ghost.row == r and ghost.col == c:
                return True
        return False

    def _is_open_outside_house(self, r, c):
        in_house = r in GHOST_HOUSE_ROWS and c in GHOST_HOUSE_COLS
        return self._in_bounds(r, c) and self.level[r][c] not in WALLS and not in_house

    def nearest_open_cell(self, r, c):
        """Ô đi được gần nhất, cho các mục tiêu rơi vào tường, nhà ma hoặc ngoài bản đồ."""
        r = max(0, min(r, self.game.row - 1))
        c = max(0, min(c, self.game.col - 1))
        for radius in range(self.game.row + self.game.col):
            for dr in range(-radius, radius + 1):
                dc = radius - abs(dr)
                for candidate in ((r + dr, c - dc), (r + dr, c + dc)):
                    if self._is_open_outside_house(*candidate):
                        return candidate
        return r, c

    def is_tunnel_row(self, row):
        return self.level[row][0] not in WALLS and self.level[row][29] not in WALLS
