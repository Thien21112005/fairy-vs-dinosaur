from fairy_vs_dinosaur.entities.ghost import Ghost


class Pinky(Ghost):
    def __init__(self, game):
        super().__init__(game, name="pinky", start_row=15, start_col=14, color=(255, 184, 255),
                         home=(15, 15), release_delay=1000)
        # Vòng tuần tra góc trên bên trái
        self.scatter_cycle = [
            (6, 7), (6, 6), (6, 5), (6, 4), (6, 3), (6, 2),
            (5, 2), (4, 2), (3, 2), (2, 2),
            (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
            (3, 7), (4, 7), (5, 7)
        ]

    def get_chase_target(self):
        # Nhắm 4 ô phía trước người chơi; khi người chơi đi lên thì lệch thêm 4 ô sang trái như bản gốc
        pac_r, pac_c = self.game.player.row, self.game.player.col
        pac_dir = self.game.player.direction
        if pac_dir == 0:
            return pac_r, pac_c + 4
        if pac_dir == 1:
            return pac_r, pac_c - 4
        if pac_dir == 2:
            return pac_r - 4, pac_c - 4
        return pac_r + 4, pac_c
