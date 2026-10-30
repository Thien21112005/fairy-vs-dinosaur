from collections import deque
import time


class BFSPathFinder:
    def __init__(self, game):
        self.game = game
        self.directions = [(1, 0, 0), (-1, 0, 1), (0, -1, 2), (0, 1, 3)]

    def find_full_path(self, start_row, start_col, target_row, target_col, ghost=None):
        # Đo thời gian bắt đầu
        start_time = time.time()

        start = (start_row, start_col)
        target = (target_row, target_col)
        if start == target:
            return []

        queue = deque([(start, [start])])
        visited = {start}
        expanded_nodes = 0

        if ghost:
            check_func = lambda r, c: self.game.level.checktuong_for_ghost(r, c, ghost)
        else:
            check_func = lambda r, c: self.game.level.checktuong_for_pacman(r, c)

        while queue:
            current, path = queue.popleft()
            row, col = current
            expanded_nodes += 1

            if current == target:
                # Tính toán metrics khi tìm thấy đường
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # ms
                path_length = len(path)

                # Ước lượng memory usage dựa trên số node đã visited
                memory_usage = self._estimate_memory_usage(len(visited), path_length)

                # Cập nhật metrics vào game
                self._update_metrics(execution_time, expanded_nodes, path_length, memory_usage, True)
                return path

            for dx, dy, d in self.directions:
                next_row = row + dy
                next_col = col + dx
                # Handle wrap-around...
                if dy == 0 and (next_col < 0 or next_col >= self.game.col):
                    if self.game.level.is_tunnel_row(row):
                        next_col = next_col % self.game.col
                        if next_col < 0:
                            next_col += self.game.col
                    else:
                        continue

                if not (0 <= next_row < self.game.row and 0 <= next_col < self.game.col):
                    continue

                next_pos = (next_row, next_col)
                if not check_func(next_row, next_col) and next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))

        # Không tìm thấy đường
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000

        # Ước lượng memory usage
        memory_usage = self._estimate_memory_usage(len(visited), 0)

        self._update_metrics(execution_time, expanded_nodes, 0, memory_usage, False)
        return []

    def find_path_to_nearest_pellet(self, start_row, start_col):
        # Đo thời gian bắt đầu
        start_time = time.time()

        start = (start_row, start_col)
        queue = deque([start])
        visited = {start}
        came_from = {start: None}
        expanded_nodes = 0

        check_func = lambda r, c: self.game.level.checktuong_for_pacman(r, c)
        is_pellet = lambda r, c: self.game.level.level[r][c] in [1, 2]

        while queue:
            current = queue.popleft()
            row, col = current
            expanded_nodes += 1

            if is_pellet(row, col) and current != start:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()

                end_time = time.time()
                execution_time = (end_time - start_time) * 1000
                path_length = len(path)

                # Ước lượng memory usage
                memory_usage = self._estimate_memory_usage(len(visited), path_length)

                self._update_metrics(execution_time, expanded_nodes, path_length, memory_usage, True)
                return path

            for dx, dy, d in self.directions:
                next_row = row + dy
                next_col = col + dx
                if dy == 0 and (next_col < 0 or next_col >= self.game.col):
                    if self.game.level.is_tunnel_row(row):
                        next_col = next_col % self.game.col
                        if next_col < 0:
                            next_col += self.game.col
                    else:
                        continue

                if not (0 <= next_row < self.game.row and 0 <= next_col < self.game.col):
                    continue

                next_pos = (next_row, next_col)
                if not check_func(next_row, next_col) and next_pos not in visited:
                    visited.add(next_pos)
                    queue.append(next_pos)
                    came_from[next_pos] = current

        end_time = time.time()
        execution_time = (end_time - start_time) * 1000

        # Ước lượng memory usage
        memory_usage = self._estimate_memory_usage(len(visited), 0)

        self._update_metrics(execution_time, expanded_nodes, 0, memory_usage, False)
        return []

    def _estimate_memory_usage(self, visited_count, path_length):
        """Ước lượng memory usage dựa trên kích thước dữ liệu"""
        # Mỗi node trong visited: ước lượng 50 bytes
        # Mỗi node trong path: ước lượng 30 bytes
        # Queue và các cấu trúc khác: ước lượng thêm
        base_memory = 100  # KB cho các biến và cấu trúc cơ bản
        visited_memory = visited_count * 0.05  # KB
        path_memory = path_length * 0.03  # KB

        total_kb = base_memory + visited_memory + path_memory
        return total_kb

    def _update_metrics(self, execution_time, expanded_nodes, path_length, memory_usage, success):
        """Cập nhật metrics vào game"""
        self.game.metrics['execution_time'] = execution_time
        self.game.metrics['expanded_nodes'] = expanded_nodes
        self.game.metrics['path_lengths'].append(path_length)
        self.game.metrics['memory_usage'] = max(self.game.metrics['memory_usage'], memory_usage)
        self.game.metrics['success'] = 1 if success else 0
        self.game.metrics['calls'] += 1