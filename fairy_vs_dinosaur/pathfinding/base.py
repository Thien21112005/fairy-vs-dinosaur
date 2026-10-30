import time


class BasePathFinder:
    """Phần dùng chung của các thuật toán: duyệt ô kề, chi phí, heuristic và ghi metrics."""

    BASE_MEMORY_KB = 50  # KB cho các biến và cấu trúc cơ bản
    REPLAN_EACH_CELL = True  # Tìm lại đường ở mỗi ô để né ghost

    def __init__(self, game):
        self.game = game
        self.directions = [(1, 0, 0), (-1, 0, 1), (0, -1, 2), (0, 1, 3)]  # (dx, dy, dir): phải, trái, lên, xuống

    def find_path_to_nearest_pellet(self, start_row, start_col):
        raise NotImplementedError

    def wrap_step(self, row, col, dx, dy):
        """Ô đích của một bước đi, có xử lý xuyên đường hầm. None nếu ra ngoài bản đồ."""
        next_row = row + dy
        next_col = col + dx
        if dy == 0 and (next_col < 0 or next_col >= self.game.col):
            if not self.game.level.is_tunnel_row(row):
                return None
            next_col = next_col % self.game.col
        if 0 <= next_row < self.game.row and 0 <= next_col < self.game.col:
            return next_row, next_col
        return None

    def step_between(self, row, col, target_row, target_col):
        """Bước (dx, dy, dir) đưa từ một ô sang ô kề của nó. None nếu hai ô không kề nhau."""
        for step in self.directions:
            if self.wrap_step(row, col, step[0], step[1]) == (target_row, target_col):
                return step
        return None

    def _neighbors(self, row, col):
        """Các ô kề nằm trong bản đồ. Chưa kiểm tra tường."""
        for dx, dy, _ in self.directions:
            next_pos = self.wrap_step(row, col, dx, dy)
            if next_pos is not None:
                yield next_pos

    def _is_blocked(self, r, c):
        return self.game.level.checktuong_for_pacman(r, c)

    def _is_pellet(self, r, c):
        return self.game.level.level[r][c] in [1, 2]

    def _pellets(self):
        return [(r, c) for r in range(self.game.row) for c in range(self.game.col) if self._is_pellet(r, c)]

    def _heuristic(self, a, b):
        """Khoảng cách Manhattan, có tính đường đi tắt qua hầm"""
        dc = abs(a[1] - b[1])
        return abs(a[0] - b[0]) + min(dc, self.game.col - dc)

    def _distance_to_nearest(self, node, pellets):
        return min(self._heuristic(node, p) for p in pellets)

    def _get_cost(self, r, c):
        """Chi phí bước đi: pellet rẻ để ưu tiên, ô trống đắt hơn, cộng thêm phạt khi gần ghost."""
        v = self.game.level.level[r][c]
        if v == 2:  # Power pellet
            base_cost = 0.1
        elif v == 1:  # Pellet thường
            base_cost = 0.5
        else:  # Ô trống
            base_cost = 2.0
        return base_cost + self._get_ghost_penalty(r, c)

    def _get_ghost_penalty(self, r, c):
        penalty = 0
        for ghost in self.game.visible_ghosts():
            if not ghost.is_vulnerable() and not ghost.eaten and not ghost.returning_home:
                dist = abs(r - ghost.row) + abs(c - ghost.col)
                if dist <= 2:
                    penalty += 100
                elif dist <= 4:
                    penalty += 10
        return penalty

    @staticmethod
    def _reconstruct(came_from, node):
        path = []
        while node is not None:
            path.append(node)
            node = came_from[node]
        path.reverse()
        return path

    def _finish(self, start_time, expanded_nodes, path, visited_count, *extra_memory_kb):
        """Ghi metrics cho một lần tìm đường rồi trả về path (rỗng nếu thất bại)."""
        execution_time = time.time() - start_time
        memory_usage = self.BASE_MEMORY_KB + visited_count * 0.05 + len(path) * 0.03
        for kb in extra_memory_kb:
            memory_usage += kb
        self._update_metrics(execution_time, expanded_nodes, memory_usage)
        return path

    def _update_metrics(self, execution_time, expanded_nodes, memory_usage):
        """Cộng dồn metrics của cả ván để so sánh các thuật toán"""
        self.game.metrics['execution_time'] += execution_time
        self.game.metrics['expanded_nodes'] += expanded_nodes
        self.game.metrics['memory_usage'] = max(self.game.metrics['memory_usage'], memory_usage)
        self.game.metrics['calls'] += 1
