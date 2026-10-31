from fairy_vs_dinosaur.entities.ghost import Ghost
from fairy_vs_dinosaur.ui import theme


class Pinky(Ghost):
    def __init__(self, game):
        super().__init__(game, name="pinky", start_row=15, start_col=14, color=theme.PATH_PINKY,
                         home=(15, 15), release_delay=1000)
        # Vòng tuần tra góc trên bên trái
        self.scatter_cycle = [
            (6, 7), (6, 6), (6, 5), (6, 4), (6, 3), (6, 2),
            (5, 2), (4, 2), (3, 2), (2, 2),
            (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
            (3, 7), (4, 7), (5, 7)
        ]

    def get_chase_target(self):
        # Chặn đầu: tới ngã rẽ phía trước hướng đi của người chơi
        return self.game.ghost_coordinator.target_for(self)
