from fairy_vs_dinosaur.entities.ghost import Ghost


class Pinky(Ghost):
    def __init__(self, game):
        super().__init__(game, name="pinky", start_row=15, start_col=14, color=(255, 184, 255))
        # Override vị trí nhà ma cho Pinky
        self.ghost_home = (15, 15)
        # Scatter target cho Pinky: top-left
        self.scatter_target_r = 0
        self.scatter_target_c = 0
        # Scatter cycle cho Pinky (top-left circuit)
        self.scatter_cycle = [
            (6, 7), (6, 6), (6, 5), (6, 4), (6, 3), (6, 2),
            (5, 2), (4, 2), (3, 2), (2, 2),
            (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
            (3, 7), (4, 7), (5, 7)
        ]
        self.current_cycle_index = -1  # Theo dõi vị trí trong cycle
        # Delay release 1s sau Blinky
        self.release_delay = 1000  # 1 giây
        self.release_timer = self.release_delay


    def get_chase_target(self):
        # Pinky chase: nhắm đến 4 ô phía trước Pac-Man (theo hướng di chuyển)
        # Bao gồm bug gốc khi Pac-Man đi lên: nhắm 4 up và 4 left
        pac_r, pac_c = self.game.player.row, self.game.player.col
        pac_dir = self.game.player.direction
        offset_r, offset_c = 0, 0
        if pac_dir == 0:  # right
            offset_c = 4
        elif pac_dir == 1:  # left
            offset_c = -4
        elif pac_dir == 2:  # up
            offset_r = -4
            offset_c = -4  # Bug gốc
        elif pac_dir == 3:  # down
            offset_r = 4
        target_r = pac_r + offset_r
        target_c = pac_c + offset_c
        # Giới hạn trong map nếu cần, nhưng BFS sẽ xử lý
        return target_r, target_c

    def get_scatter_target(self):
        # Scatter cho Pinky: di chuyển theo circuit quanh top-left
        # Tìm vị trí hiện tại trong cycle
        current_index = -1
        for i, (r, c) in enumerate(self.scatter_cycle):
            if self.row == r and self.col == c:
                current_index = i
                break

        # Nếu đang ở một điểm trong cycle, chọn điểm tiếp theo
        if current_index != -1:
            next_index = (current_index + 1) % len(self.scatter_cycle)
            return self.scatter_cycle[next_index]
        else:
            # Nếu không ở trong cycle, đi đến điểm đầu tiên
            return self.scatter_cycle[0]
