import math

import pygame

from fairy_vs_dinosaur.entities.ghost import Ghost


class Clyde(Ghost):
    def __init__(self, game):
        super().__init__(game, name="clyde", start_row=15, start_col=17, color=(255, 165, 0),
                         home=(15, 17), release_delay=4000)
        # Vòng tuần tra góc dưới bên trái
        self.scatter_cycle = [
            (24, 10), (25, 10), (26, 10), (27, 10), (27, 11), (27, 12), (27, 13), (28, 13), (29, 13), (30, 13),
            (30, 12), (30, 11), (30, 10), (30, 9), (30, 8), (30, 7), (30, 6), (30, 5), (30, 4), (30, 3), (30, 2),
            (29, 2), (28, 2), (27, 2), (27, 3), (27, 4), (27, 5), (27, 6), (27, 7), (26, 7), (25, 7),
            (24, 7), (24, 8), (24, 9)
        ]

    def get_chase_target(self):
        # Xa hơn 8 ô thì lấp lối thoát còn trống, gần hơn thì quay về vòng tuần tra để né
        pac_r, pac_c = self.game.player.row, self.game.player.col
        if math.sqrt((self.row - pac_r) ** 2 + (self.col - pac_c) ** 2) > 8:
            return self.game.ghost_coordinator.target_for(self)
        return self._next_in_scatter_cycle() or self._closest_cycle_point()

    def _closest_cycle_point(self):
        return min(self.scatter_cycle, key=lambda p: math.sqrt((self.row - p[0]) ** 2 + (self.col - p[1]) ** 2))

    def draw_path(self):
        super().draw_path()
        if self.game.show_hint:
            # Vòng tròn bán kính 8 ô quanh người chơi
            center = (self.game.player.x, self.game.player.y + self.game.y_offset)
            radius = 8 * (self.game.num1_r + self.game.num2_c) / 2
            pygame.draw.circle(self.game.screen, self.color, center, radius, 2)
