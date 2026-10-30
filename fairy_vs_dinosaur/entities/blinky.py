from fairy_vs_dinosaur.entities.ghost import directional, Ghost


class Blinky(Ghost):
    def __init__(self, game):
        super().__init__(game, name="blinky", start_row=12, start_col=15, color=(255, 0, 0))
        self.set_elroy_thresholds()
        # Vòng tuần tra góc trên bên phải
        self.scatter_cycle = [
            (6, 22), (6, 23), (6, 24), (6, 25), (6, 26), (6, 27),
            (5, 27), (4, 27), (3, 27), (2, 27),
            (2, 26), (2, 25), (2, 24), (2, 23), (2, 22),
            (3, 22), (4, 22), (5, 22)
        ]
        self.elroy_animations = directional(self._load_frames("elroy", "00", 6))

    def set_speed_multipliers(self):
        super().set_speed_multipliers()
        level = self.game.level_num
        if level == 1:
            self.elroy1_multiplier = 1.0
            self.elroy2_multiplier = 1.05
        elif level <= 4:
            self.elroy1_multiplier = 1.05
            self.elroy2_multiplier = 1.1
        else:
            self.elroy1_multiplier = 1.1
            self.elroy2_multiplier = 1.15

    def apply_level_difficulty(self):
        super().apply_level_difficulty()
        self.set_elroy_thresholds()

    def set_elroy_thresholds(self):
        level = self.game.level_num
        for max_level, threshold in [(1, 20), (2, 30), (5, 40), (8, 50), (11, 60), (14, 80), (18, 100)]:
            if level <= max_level:
                self.elroy1_threshold = threshold
                break
        else:
            self.elroy1_threshold = 120
        self.elroy2_threshold = self.elroy1_threshold // 2

    def is_elroy(self):
        return self.game.level.remaining_pellets <= self.elroy1_threshold

    def get_base_multiplier(self):
        if self.game.level.remaining_pellets <= self.elroy2_threshold:
            return self.elroy2_multiplier
        if self.game.level.remaining_pellets <= self.elroy1_threshold:
            return self.elroy1_multiplier
        return self.normal_speed_multiplier

    def get_chase_target(self):
        # Đuổi thẳng vào vị trí người chơi
        return self.game.player.row, self.game.player.col

    def _base_animations(self):
        return self.elroy_animations if self.is_elroy() else self.normal_animations
