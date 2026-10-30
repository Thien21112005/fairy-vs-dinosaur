import pygame

from fairy_vs_dinosaur.entities.ghost import Ghost


class Inky(Ghost):
    def __init__(self, game):
        super().__init__(game, name="inky", start_row=15, start_col=12, color=(0, 255, 255))
        # Override vị trí nhà ma cho Inky
        self.ghost_home = (15, 12)
        # Scatter target cho Inky: bottom-left circuit (dựa trên danh sách cung cấp)
        self.scatter_cycle = [
            (24, 19), (24, 20), (24, 21), (24, 22), (25, 22), (26, 22), (27, 22),
            (27, 23), (27, 24), (27, 25), (27, 26), (27, 27), (28, 27), (29, 27),
            (30, 27), (30, 26), (30, 25), (30, 24), (30, 23), (30, 22), (30, 21),
            (30, 20), (30, 19), (30, 18), (30, 17), (30, 16), (29, 16), (28, 16),
            (27, 16), (27, 17), (27, 18), (27, 19), (26, 19), (25, 19)
        ]
        self.current_cycle_index = -1  # Theo dõi vị trí trong cycle
        # Delay release 2.5s sau Blinky
        self.release_delay = 2500  # 2.5 giây
        self.release_timer = self.release_delay

    def get_chase_target(self):
        # Inky chase: phức tạp, lấy offset 2 ô phía trước Pac-Man, sau đó từ Blinky qua offset, nhân đôi vector
        # Bug tương tự Pinky khi đi lên
        pac_r, pac_c = self.game.player.row, self.game.player.col
        pac_dir = self.game.player.direction
        offset_r, offset_c = 0, 0
        if pac_dir == 0:  # right
            offset_c = 2
        elif pac_dir == 1:  # left
            offset_c = -2
        elif pac_dir == 2:  # up
            offset_r = -2
            offset_c = 0  # Sửa bug gốc: loại bỏ offset_c = -2
        elif pac_dir == 3:  # down
            offset_r = 2
        offset_r = pac_r + offset_r
        offset_c = pac_c + offset_c

        # Vị trí Blinky
        blinky_r, blinky_c = self.game.blinky.row, self.game.blinky.col

        # Vector từ Blinky đến offset
        vector_r = offset_r - blinky_r
        vector_c = offset_c - blinky_c

        # Nhân đôi vector và thêm vào vị trí Blinky
        target_r = blinky_r + 2 * vector_r
        target_c = blinky_c + 2 * vector_c

        return target_r, target_c

    def get_scatter_target(self):
        # Scatter cho Inky: di chuyển theo circuit bottom-left dựa trên cycle
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

    def draw_path(self):
        # Gọi super để vẽ đường BFS bình thường của Inky
        super().draw_path()

        # Chỉ vẽ extra visualization nếu đang ở mode chase (và mode đã được set), và không ở trạng thái đặc biệt
        # THÊM KIỂM TRA self.mode is not None ĐỂ TRÁNH LỖI KHI CHƯA READY
        if self.mode is not None and self.mode == 'chase' and not (self.game.dying or self.game.just_reset or self.eaten or self.returning_home or self.hatching or not self.game.game_started):
            # Tính các vị trí cần vẽ
            blinky_r, blinky_c = self.game.blinky.row, self.game.blinky.col
            pac_r, pac_c = self.game.player.row, self.game.player.col
            pac_dir = self.game.player.direction
            offset_r, offset_c = 0, 0
            if pac_dir == 0:  # right
                offset_c = 2
            elif pac_dir == 1:  # left
                offset_c = -2
            elif pac_dir == 2:  # up
                offset_r = -2
                offset_c = 0  # Sửa bug gốc: loại bỏ offset_c = -2
            elif pac_dir == 3:  # down
                offset_r = 2
            offset_r = pac_r + offset_r
            offset_c = pac_c + offset_c

            # Target đã tính
            target_r, target_c = self.get_chase_target()

            # Chuyển sang screen coordinates
            blinky_x = blinky_c * self.game.num2_c + self.game.num2_c / 2.0
            blinky_y = blinky_r * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset

            offset_x = offset_c * self.game.num2_c + self.game.num2_c / 2.0
            offset_y = offset_r * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset

            target_x = target_c * self.game.num2_c + self.game.num2_c / 2.0
            target_y = target_r * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset

            # Vẽ line từ Blinky đến offset (vector đầu tiên)
            line_width = 2
            pygame.draw.line(self.game.screen, self.color, (blinky_x, blinky_y), (offset_x, offset_y), line_width)

            # Vẽ arrow tại offset
            vector_dx = offset_c - blinky_c
            vector_dy = offset_r - blinky_r
            if vector_dx != 0 or vector_dy != 0:  # Tránh zero vector
                udx = vector_dx / max(abs(vector_dx), abs(vector_dy), 1)  # Normalize direction
                udy = vector_dy / max(abs(vector_dx), abs(vector_dy), 1)
                arrow_size = min(self.game.num1_r, self.game.num2_c) / 2
                perp_x = -udy
                perp_y = udx
                tip = (offset_x, offset_y)
                base1 = (offset_x - arrow_size * udx + (arrow_size / 2) * perp_x,
                         offset_y - arrow_size * udy + (arrow_size / 2) * perp_y)
                base2 = (offset_x - arrow_size * udx - (arrow_size / 2) * perp_x,
                         offset_y - arrow_size * udy - (arrow_size / 2) * perp_y)
                pygame.draw.line(self.game.screen, self.color, tip, base1, line_width)
                pygame.draw.line(self.game.screen, self.color, tip, base2, line_width)

            # Vẽ line từ offset đến target (vector nhân đôi)
            pygame.draw.line(self.game.screen, self.color, (offset_x, offset_y), (target_x, target_y), line_width)

            # Vẽ arrow tại target
            vector_dx2 = target_c - offset_c
            vector_dy2 = target_r - offset_r
            if vector_dx2 != 0 or vector_dy2 != 0:
                udx2 = vector_dx2 / max(abs(vector_dx2), abs(vector_dy2), 1)
                udy2 = vector_dy2 / max(abs(vector_dx2), abs(vector_dy2), 1)
                arrow_size = min(self.game.num1_r, self.game.num2_c) / 2
                perp_x2 = -udy2
                perp_y2 = udx2
                tip2 = (target_x, target_y)
                base1_2 = (target_x - arrow_size * udx2 + (arrow_size / 2) * perp_x2,
                           target_y - arrow_size * udy2 + (arrow_size / 2) * perp_y2)
                base2_2 = (target_x - arrow_size * udx2 - (arrow_size / 2) * perp_x2,
                           target_y - arrow_size * udy2 - (arrow_size / 2) * perp_y2)
                pygame.draw.line(self.game.screen, self.color, tip2, base1_2, line_width)
                pygame.draw.line(self.game.screen, self.color, tip2, base2_2, line_width)
