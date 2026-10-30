import pygame
import random
from abc import ABC, abstractmethod

class Ghost(ABC):
    def __init__(self, game, name, start_row, start_col, color):
        self.game = game
        self.name = name
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



