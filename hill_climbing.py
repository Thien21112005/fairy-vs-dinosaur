import random
import time



class HillClimbingPathFinder:
    def __init__(self, game):
        self.game = game
        self.directions = [(1, 0, 0), (-1, 0, 1), (0, -1, 2), (0, 1, 3)]  # (dx, dy, dir)
        self.max_steps = 200  # Ngăn loop

    def _heuristic(self, a, b):
        """Manhattan distance"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _get_cost(self, r, c):
        """Step cost with base + ghost penalty"""
        v = self.game.level.level[r][c]
        base_cost = 1  # Default
        if v == 2:  # Power pellet
            base_cost = 0.1
        elif v == 1:  # Normal pellet
            base_cost = 0.5
        else:  # Empty
            base_cost = 2.0
        penalty = self._get_ghost_penalty(r, c)
        return base_cost + penalty

    def _get_ghost_penalty(self, r, c):
        penalty = 0
        if self.game.mode_manager.frightened_active:
            return penalty
        for ghost in self.game.ghosts:
            if not ghost.eaten and not ghost.returning_home:
                dist = abs(r - ghost.row) + abs(c - ghost.col)
                if dist <= 2:
                    penalty += 100
                elif dist <= 4:
                    penalty += 10
        return penalty

    def find_full_path(self, start_row, start_col, target_row, target_col):
        # Đo thời gian bắt đầu
        start_time = time.time()

        start = (start_row, start_col)
        target = (target_row, target_col)
        if start == target:
            return []

        current = start
        path = [start]
        visited = {start}
        expanded_nodes = 0

        check_func = lambda r, c: self.game.level.checktuong_for_pacman(r, c)

        steps = 0
        while current != target and steps < self.max_steps:
            row, col = current
            neighbors = []
            expanded_nodes += 1  # Mỗi bước xem xét current node

            for dx, dy, d in self.directions:
                next_row = row + dy
                next_col = col + dx
                if dy == 0 and (next_col < 0 or next_col >= self.game.col):
                    if self.game.level.is_tunnel_row(row):
                        next_col = next_col % self.game.col
                        if next_col < 0:
                            next_col += self.game.col
                if not (0 <= next_row < self.game.row and 0 <= next_col < self.game.col):
                    continue
                next_pos = (next_row, next_col)
                if not check_func(next_row, next_col) and next_pos not in visited and self._get_cost(next_row,
                                                                                                     next_col) <= 100:
                    h = self._heuristic(next_pos, target)
                    neighbors.append((h, next_pos))

            if not neighbors:
                break  # Kẹt

            # Stochastic: Chọn random từ top good neighbors (có h < current_h)
            current_h = self._heuristic(current, target)
            good_neighbors = [n for n in neighbors if n[0] < current_h]
            if not good_neighbors:
                # Fallback random từ all neighbors để thoát kẹt
                if neighbors:
                    best_h, best_pos = random.choice(neighbors)
                else:
                    break
            else:
                # Chọn random từ good
                best_h, best_pos = random.choice(good_neighbors)

            current = best_pos
            path.append(current)
            visited.add(current)
            steps += 1

        success = (current == target)

        # Tính toán metrics
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # ms
        path_length = len(path) if success else 0

        # Ước lượng memory usage
        memory_usage = self._estimate_memory_usage(len(visited), path_length, steps, len(neighbors))

        # Cập nhật metrics vào game
        self._update_metrics(execution_time, expanded_nodes, path_length, memory_usage, success)

        if success:
            return path
        return []  # Không đến được hoặc max steps

    def find_path_to_nearest_pellet(self, start_row, start_col):
        # Đo thời gian bắt đầu
        start_time = time.time()

        start = (start_row, start_col)
        pellets = [(r, c) for r in range(self.game.row) for c in range(self.game.col) if
                   self.game.level.level[r][c] in [1, 2]]

        if not pellets:
            return []

        def heuristic_multi(n):
            if not pellets:
                return 0
            return min(self._heuristic(n, p) for p in pellets)

        current = start
        path = [start]
        visited = {start}
        expanded_nodes = 0

        check_func = lambda r, c: self.game.level.checktuong_for_pacman(r, c)
        is_pellet = lambda pos: pos in pellets

        steps = 0
        while (not is_pellet(current) or current == start) and steps < self.max_steps:
            row, col = current
            neighbors = []
            expanded_nodes += 1  # Mỗi bước xem xét current node

            for dx, dy, d in self.directions:
                next_row = row + dy
                next_col = col + dx
                if dy == 0 and (next_col < 0 or next_col >= self.game.col):
                    if self.game.level.is_tunnel_row(row):
                        next_col = next_col % self.game.col
                        if next_col < 0:
                            next_col += self.game.col
                if not (0 <= next_row < self.game.row and 0 <= next_col < self.game.col):
                    continue
                next_pos = (next_row, next_col)
                if not check_func(next_row, next_col) and next_pos not in visited and self._get_cost(next_row,
                                                                                                     next_col) <= 100:
                    h = heuristic_multi(next_pos)
                    neighbors.append((h, next_pos))

            if not neighbors:
                break  # Kẹt

            # Stochastic giống trên
            current_h = heuristic_multi(current)
            good_neighbors = [n for n in neighbors if n[0] < current_h]
            if not good_neighbors:
                if neighbors:
                    best_h, best_pos = random.choice(neighbors)
                else:
                    break
            else:
                best_h, best_pos = random.choice(good_neighbors)

            current = best_pos
            path.append(current)
            visited.add(current)
            steps += 1

        success = (is_pellet(current) and current != start)

        # Tính toán metrics
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # ms
        path_length = len(path) if success else 0

        # Ước lượng memory usage
        memory_usage = self._estimate_memory_usage(len(visited), path_length, steps, len(neighbors))

        # Cập nhật metrics vào game
        self._update_metrics(execution_time, expanded_nodes, path_length, memory_usage, success)

        if success:
            return path
        return []  # Không tìm thấy hoặc max steps

    def _estimate_memory_usage(self, visited_count, path_length, steps_count, neighbors_count):
        """Ước lượng memory usage cho Hill Climbing dựa trên kích thước dữ liệu"""
        # Mỗi node trong visited: ước lượng 50 bytes
        # Mỗi node trong path: ước lượng 30 bytes
        # Mỗi bước: ước lượng 40 bytes (lưu trạng thái hiện tại, neighbors)
        # Danh sách neighbors: ước lượng 20 bytes mỗi neighbor
        # Các cấu trúc khác: ước lượng thêm
        base_memory = 40  # KB cho các biến và cấu trúc cơ bản
        visited_memory = visited_count * 0.05  # KB
        path_memory = path_length * 0.03  # KB
        steps_memory = steps_count * 0.04  # KB cho các bước
        neighbors_memory = neighbors_count * 0.02  # KB cho danh sách neighbors

        total_kb = base_memory + visited_memory + path_memory + steps_memory + neighbors_memory
        return total_kb

    def _update_metrics(self, execution_time, expanded_nodes, path_length, memory_usage, success):
        """Cập nhật metrics vào game"""
        self.game.metrics['execution_time'] = execution_time
        self.game.metrics['expanded_nodes'] = expanded_nodes
        self.game.metrics['path_lengths'].append(path_length)
        self.game.metrics['memory_usage'] = max(self.game.metrics['memory_usage'], memory_usage)
        self.game.metrics['success'] = 1 if success else 0
        self.game.metrics['calls'] += 1
