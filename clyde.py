from ghost import Ghost
import pygame
import math  # Thêm import math để tính sqrt

class Clyde(Ghost):
    def __init__(self, game):
        super().__init__(game, name="clyde", start_row=15, start_col=17, color=(255, 165, 0))
        # Override vị trí nhà ma cho Clyde
        self.ghost_home = (15, 17)
        # Scatter target cho Clyde: bottom-left (dùng cho chase khi gần, nhưng scatter dùng cycle)
        self.scatter_target_r = 30
        self.scatter_target_c = 2
        # Scatter cycle cho Clyde (bottom-left circuit)
        self.scatter_cycle = [
            (24, 10), (25, 10), (26, 10), (27, 10), (27, 11), (27, 12), (27, 13), (28, 13), (29, 13), (30, 13),
            (30, 12), (30, 11), (30, 10), (30, 9), (30,8), (30, 7), (30, 6), (30, 5), (30, 4), (30, 3), (30, 2),
            (29, 2), (28, 2), (27, 2), (27, 3), (27, 4), (27, 5), (27, 6), (27, 7), (26, 7), (25, 7),
            (24, 7), (24, 8), (24, 9)
        ]
        self.current_cycle_index = -1  # Theo dõi vị trí trong cycle
        # Delay release 4s sau
        self.release_delay = 4000  # 4 giây
        self.release_timer = self.release_delay

    def get_chase_target(self):
        # Clyde chase: Nếu cách Pac-Man >8 ô, nhắm trực tiếp như Blinky; nếu <=8 ô, nhắm đến điểm tiếp theo trong scatter cycle để "tránh né"
        pac_r = self.game.player.row
        pac_c = self.game.player.col
        # Sử dụng khoảng cách Euclidean để khớp với vòng tròn
        dist = math.sqrt((self.row - pac_r)**2 + (self.col - pac_c)**2)
        if dist > 8:
            return (pac_r, pac_c)
        else:
            return self.get_scatter_target(is_avoid=True)  # Nhắm đến điểm tiếp theo trong cycle để chạy theo chu trình scatter

    def get_scatter_target(self, is_avoid=False):
        # Scatter cho Clyde: di chuyển theo circuit quanh bottom-left
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
            if is_avoid:
                # Tìm điểm gần nhất trong cycle
                min_dist = float('inf')
                closest_index = 0
                for i, (r, c) in enumerate(self.scatter_cycle):
                    dist = math.sqrt((self.row - r)**2 + (self.col - c)**2)
                    if dist < min_dist:
                        min_dist = dist
                        closest_index = i
                return self.scatter_cycle[closest_index]
            else:
                # Nếu không ở trong cycle, đi đến điểm đầu tiên
                return self.scatter_cycle[0]

    def draw_path(self):
        super().draw_path()
        if self.game.show_hint:
            # Vẽ vòng tròn bán kính 8 ô tâm Pacman
            pac_x = self.game.player.x
            pac_y = self.game.player.y + self.game.y_offset
            cell_size_avg = (self.game.num1_r + self.game.num2_c) / 2
            radius = 8 * cell_size_avg
            pygame.draw.circle(self.game.screen, self.color, (pac_x, pac_y), radius, 2)  # Độ dày đường viền = 2