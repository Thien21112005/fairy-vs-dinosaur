import pygame
from level1 import *
class Level:
    def __init__(self, game):
        self.game = game
        self.level = [row[:] for row in boards]
        self.tuong = {3, 4, 5, 6, 7, 8, 9}  # 9 là cổng ma
        item_raw = [pygame.image.load(f"assets/Photos/{i}.png").convert_alpha() for i in range(1, 10)]
        self.item = [pygame.transform.smoothscale(img, (self.game.num2_c, self.game.num1_r)) for img in item_raw]
        # TÍNH TOÁN TỔNG SỐ PELLETS BAN ĐẦU
        self.initial_pellets = sum(sum(1 for c in row if c in [1, 2]) for row in self.level)
        self.remaining_pellets = self.initial_pellets

    def draw_board(self):
        for i in range(len(self.level)):
            for j in range(len(self.level[i])):
                v = self.level[i][j]
                if 1 <= v <= 9:
                    self.game.screen.blit(self.item[v - 1],
                                          (j * self.game.num2_c, i * self.game.num1_r + self.game.y_offset))

    def checktuong(self, r, c):
        if not (0 <= r < self.game.row and 0 <= c < self.game.col):
            return True
        return self.level[r][c] in self.tuong

    def checktuong_for_ghost(self, r, c, ghost=None):
        """Kiểm tra tường với điều kiện đặc biệt cho ghost"""
        if not (0 <= r < self.game.row and 0 <= c < self.game.col):
            return True

        cell_value = self.level[r][c]
        is_wall = cell_value in self.tuong

        if cell_value == 9:  # Là cổng ma
            if ghost and (ghost.returning_home or ghost.mode != 'frightened'):
                return False  # Cho phép đi qua
            else:
                return True  # Không cho qua

        return is_wall  # Đối với các tường khác

    def checktuong_for_pacman(self, r, c):
        if not (0 <= r < self.game.row and 0 <= c < self.game.col):
            return True

        if self.level[r][c] in self.tuong:
            return True

        if not self.game.mode_manager.frightened_active:
            for i, ghost in enumerate(self.game.ghosts):
                if [self.game.ui.show_blinky, self.game.ui.show_pinky, self.game.ui.show_inky, self.game.ui.show_clyde][i]:
                    if not ghost.eaten and not ghost.returning_home and ghost.row == r and ghost.col == c:
                        return True

        return False

    def is_tunnel_row(self, row):
        return (self.level[row][0] not in self.tuong) and (self.level[row][29] not in self.tuong)

    def load_board(self, board_data):
        """Load board từ dữ liệu cung cấp và tính toán pellets"""
        self.level = [row[:] for row in board_data]
        self.initial_pellets = sum(1 for row in self.level for cell in row if cell in [1, 2])
        self.remaining_pellets = self.initial_pellets