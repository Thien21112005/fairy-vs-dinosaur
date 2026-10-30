from fairy_vs_dinosaur.entities.ghost import Ghost


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

    def get_chase_target(self):
        # Bọc lót: tới lối thoát gần nó nhất mà Pinky chưa chặn
        return self.game.ghost_coordinator.target_for(self)
