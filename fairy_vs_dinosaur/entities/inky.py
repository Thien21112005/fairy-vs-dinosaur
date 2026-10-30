import pygame

from fairy_vs_dinosaur.entities.ghost import Ghost
from fairy_vs_dinosaur.entities.path_drawing import draw_arrow_head, LINE_WIDTH


class Inky(Ghost):
    def __init__(self, game):
        super().__init__(game, name="inky", start_row=15, start_col=12, color=(0, 255, 255),
                         home=(15, 12), release_delay=2500)
        # Vòng tuần tra góc dưới bên phải
        self.scatter_cycle = [
            (24, 19), (24, 20), (24, 21), (24, 22), (25, 22), (26, 22), (27, 22),
            (27, 23), (27, 24), (27, 25), (27, 26), (27, 27), (28, 27), (29, 27),
            (30, 27), (30, 26), (30, 25), (30, 24), (30, 23), (30, 22), (30, 21),
            (30, 20), (30, 19), (30, 18), (30, 17), (30, 16), (29, 16), (28, 16),
            (27, 16), (27, 17), (27, 18), (27, 19), (26, 19), (25, 19)
        ]

    def _pivot_cell(self):
        """Ô cách người chơi 2 bước theo hướng đang đi"""
        pac_r, pac_c = self.game.player.row, self.game.player.col
        pac_dir = self.game.player.direction
        if pac_dir == 0:
            return pac_r, pac_c + 2
        if pac_dir == 1:
            return pac_r, pac_c - 2
        if pac_dir == 2:
            return pac_r - 2, pac_c
        if pac_dir == 3:
            return pac_r + 2, pac_c
        return pac_r, pac_c

    def get_chase_target(self):
        # Nhân đôi vector từ Blinky tới ô trước mặt người chơi
        offset_r, offset_c = self._pivot_cell()
        blinky_r, blinky_c = self.game.blinky.row, self.game.blinky.col
        return blinky_r + 2 * (offset_r - blinky_r), blinky_c + 2 * (offset_c - blinky_c)

    def draw_path(self):
        super().draw_path()
        if self.mode == 'chase' and self.game.game_started and not self._in_special_state():
            self._draw_chase_vector()

    def _draw_chase_vector(self):
        """Minh họa cách Inky chọn mục tiêu: Blinky -> ô trước người chơi -> mục tiêu."""
        blinky = self.game.blinky.row, self.game.blinky.col
        offset = self._pivot_cell()
        target = self.get_chase_target()

        offset_point = self._cell_center(*offset)
        pygame.draw.line(self.game.screen, self.color, self._cell_center(*blinky), offset_point, LINE_WIDTH)
        self._draw_vector_arrow(blinky, offset)

        pygame.draw.line(self.game.screen, self.color, offset_point, self._cell_center(*target), LINE_WIDTH)
        self._draw_vector_arrow(offset, target)

    def _draw_vector_arrow(self, source, tip):
        vector_dx = tip[1] - source[1]
        vector_dy = tip[0] - source[0]
        if vector_dx != 0 or vector_dy != 0:
            longest = max(abs(vector_dx), abs(vector_dy), 1)
            size = min(self.game.num1_r, self.game.num2_c) / 2
            draw_arrow_head(self.game.screen, self.color, self._cell_center(*tip),
                            vector_dx / longest, vector_dy / longest, size)
