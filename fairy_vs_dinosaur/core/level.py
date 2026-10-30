import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.core.board import boards

WALLS = {3, 4, 5, 6, 7, 8, 9}  # 9 là cổng nhà ma
GHOST_GATE = 9


class Level:
    def __init__(self, game):
        self.game = game
        item_raw = [pygame.image.load(asset(f"images/tiles/{i}.png")).convert_alpha() for i in range(1, 10)]
        self.item = [pygame.transform.smoothscale(img, (self.game.num2_c, self.game.num1_r)) for img in item_raw]
        self.load_board(boards)

    def load_board(self, board_data):
        self.level = [row[:] for row in board_data]
        self.initial_pellets = sum(1 for row in self.level for cell in row if cell in [1, 2])
        self.remaining_pellets = self.initial_pellets

    def draw_board(self):
        for i, row in enumerate(self.level):
            for j, v in enumerate(row):
                if 1 <= v <= 9:
                    self.game.screen.blit(self.item[v - 1],
                                          (j * self.game.num2_c, i * self.game.num1_r + self.game.y_offset))

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

        if not self.game.mode_manager.frightened_active:
            for ghost in self.game.visible_ghosts():
                if not ghost.eaten and not ghost.returning_home and ghost.row == r and ghost.col == c:
                    return True
        return False

    def is_tunnel_row(self, row):
        return self.level[row][0] not in WALLS and self.level[row][29] not in WALLS
