import time


class DFSPathFinder:
    def __init__(self, game):
        self.game = game
        self.directions = [(1, 0, 0), (-1, 0, 1), (0, -1, 2), (0, 1, 3)]  # (dx, dy, dir)
        # phải, trái, lên, xuống

    def find_full_path(self, start_row, start_col, target_row, target_col):
        # Đo thời gian bắt đầu
        start_time = time.time()

        start = (start_row, start_col)
        target = (target_row, target_col)
        if start == target:
            return []

        stack = [(start, [start])]
        visited = {start}
        expanded_nodes = 0
        check_func = lambda r, c: self.game.level.checktuong_for_pacman(r, c)

        while stack:
            current, path = stack.pop()
            row, col = current
            expanded_nodes += 1

            if current == target:
                # Tính toán metrics khi tìm thấy đường
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # ms
                path_length = len(path)

                # Ước lượng memory usage
                memory_usage = self._estimate_memory_usage(len(visited), path_length, len(stack))

                # Cập nhật metrics vào game
                self._update_metrics(execution_time, expanded_nodes, path_length, memory_usage, True)
                return path

            for dx, dy, d in self.directions:
                next_row = row + dy
                next_col = col + dx
                # Handle wrap-around for tunnel rows on horizontal moves
                if dy == 0 and (next_col < 0 or next_col >= self.game.col):
                    if self.game.level.is_tunnel_row(row):
                        next_col = next_col % self.game.col
                        if next_col < 0:
                            next_col += self.game.col
                    else:
                        continue  # Invalid move if not tunnel
                # Now check bounds after potential wrap
                if not (0 <= next_row < self.game.row and 0 <= next_col < self.game.col):
                    continue
                next_pos = (next_row, next_col)
                if not check_func(next_row, next_col) and next_pos not in visited:
                    visited.add(next_pos)
                    stack.append((next_pos, path + [next_pos]))

        # Không tìm thấy đường
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000

        # Ước lượng memory usage
        memory_usage = self._estimate_memory_usage(len(visited), 0, len(stack))

        self._update_metrics(execution_time, expanded_nodes, 0, memory_usage, False)
        return []  # No path found

    def find_path_to_nearest_pellet(self, start_row, start_col):
        """Tìm đường đến pellet gần nhất bằng một DFS duy nhất"""
        # Đo thời gian bắt đầu
        start_time = time.time()

        start = (start_row, start_col)
        stack = [start]
        visited = {start}
        came_from = {start: None}
        expanded_nodes = 0
        check_func = lambda r, c: self.game.level.checktuong_for_pacman(r, c)
        is_pellet = lambda r, c: self.game.level.level[r][c] in [1, 2]

        while stack:
            current = stack.pop()
            row, col = current
            expanded_nodes += 1

            # Nếu ô hiện tại là pellet (không tính start nếu start là pellet)
            if is_pellet(row, col) and current != start:
                # Reconstruct path
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()

                # Tính toán metrics khi tìm thấy đường
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # ms
                path_length = len(path)

                # Ước lượng memory usage
                memory_usage = self._estimate_memory_usage(len(visited), path_length, len(stack))

                # Cập nhật metrics vào game
                self._update_metrics(execution_time, expanded_nodes, path_length, memory_usage, True)
                return path

            for dx, dy, d in self.directions:
                next_row = row + dy
                next_col = col + dx
                # Handle wrap-around for tunnel rows on horizontal moves
                if dy == 0 and (next_col < 0 or next_col >= self.game.col):
                    if self.game.level.is_tunnel_row(row):
                        next_col = next_col % self.game.col
                        if next_col < 0:
                            next_col += self.game.col
                    else:
                        continue  # Invalid move if not tunnel
                # Now check bounds after potential wrap
                if not (0 <= next_row < self.game.row and 0 <= next_col < self.game.col):
                    continue
                next_pos = (next_row, next_col)
                if not check_func(next_row, next_col) and next_pos not in visited:
                    visited.add(next_pos)
                    stack.append(next_pos)
                    came_from[next_pos] = current

        # Không tìm thấy pellet
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000

        # Ước lượng memory usage
        memory_usage = self._estimate_memory_usage(len(visited), 0, len(stack))

        self._update_metrics(execution_time, expanded_nodes, 0, memory_usage, False)
        return []  # No pellet found

    def _estimate_memory_usage(self, visited_count, path_length, stack_size):
        """Ước lượng memory usage cho DFS dựa trên kích thước dữ liệu"""
        # Mỗi node trong visited: ước lượng 50 bytes
        # Mỗi node trong path: ước lượng 30 bytes
        # Mỗi phần tử trong stack: ước lượng 60 bytes (vì chứa cả path)
        # Các cấu trúc khác: ước lượng thêm
        base_memory = 50  # KB cho các biến và cấu trúc cơ bản
        visited_memory = visited_count * 0.05  # KB
        path_memory = path_length * 0.03  # KB
        stack_memory = stack_size * 0.06  # KB cho stack

        total_kb = base_memory + visited_memory + path_memory + stack_memory
        return total_kb

    def _update_metrics(self, execution_time, expanded_nodes, path_length, memory_usage, success):
        """Cập nhật metrics vào game"""
        self.game.metrics['execution_time'] = execution_time
        self.game.metrics['expanded_nodes'] = expanded_nodes
        self.game.metrics['path_lengths'].append(path_length)
        self.game.metrics['memory_usage'] = max(self.game.metrics['memory_usage'], memory_usage)
        self.game.metrics['success'] = 1 if success else 0
        self.game.metrics['calls'] += 1
