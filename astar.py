import heapq
import time
class AStarPathFinder:
    def __init__(self, game):
        self.game = game
        self.directions = [(1, 0, 0), (-1, 0, 1), (0, -1, 2), (0, 1, 3)]  # (dx, dy, dir)

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

        pq = []  # (f_score, g_score, current, path)
        heapq.heappush(pq, (0 + self._heuristic(start, target), 0, start, [start]))

        visited = set()
        g_score = {start: 0}
        expanded_nodes = 0

        check_func = lambda r, c: self.game.level.checktuong_for_pacman(r, c)

        while pq:
            f, g, current, path = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)
            expanded_nodes += 1

            row, col = current
            if current == target:
                # Tính toán metrics khi tìm thấy đường
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # ms
                path_length = len(path)

                # Ước lượng memory usage
                memory_usage = self._estimate_memory_usage(len(visited), path_length, len(pq), len(g_score))

                # Cập nhật metrics vào game
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
                if check_func(next_row, next_col):
                    continue

                tentative_g = g + self._get_cost(next_row, next_col)
                if next_pos not in g_score or tentative_g < g_score[next_pos]:
                    g_score[next_pos] = tentative_g
                    f_new = tentative_g + self._heuristic(next_pos, target)
                    heapq.heappush(pq, (f_new, tentative_g, next_pos, path + [next_pos]))

        # Không tìm thấy đường
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000

        # Ước lượng memory usage
        memory_usage = self._estimate_memory_usage(len(visited), 0, len(pq), len(g_score))

        self._update_metrics(execution_time, expanded_nodes, 0, memory_usage, False)
        return []

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

        pq = []
        heapq.heappush(pq, (0 + heuristic_multi(start), 0, start, None))  # (f, g, current, came_from)

        came_from = {start: None}
        g_score = {start: 0}
        visited = set()
        expanded_nodes = 0

        check_func = lambda r, c: self.game.level.checktuong_for_pacman(r, c)
        is_pellet = lambda pos: pos in pellets

        best_pellet = None
        best_cost = float('inf')
        best_came_from = None

        while pq:
            f, g, current, _ = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)
            expanded_nodes += 1

            row, col = current
            if is_pellet(current) and current != start:
                if g < best_cost:
                    best_cost = g
                    best_pellet = current
                    best_came_from = came_from[current]

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
                if check_func(next_row, next_col):
                    continue

                tentative_g = g + self._get_cost(next_row, next_col)
                if next_pos not in g_score or tentative_g < g_score[next_pos]:
                    g_score[next_pos] = tentative_g
                    f_new = tentative_g + heuristic_multi(next_pos)
                    heapq.heappush(pq, (f_new, tentative_g, next_pos, current))
                    came_from[next_pos] = current

        if best_pellet is None:
            # Không tìm thấy pellet
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000

            # Ước lượng memory usage
            memory_usage = self._estimate_memory_usage(len(visited), 0, len(pq), len(g_score), len(came_from))

            self._update_metrics(execution_time, expanded_nodes, 0, memory_usage, False)
            return []

        path = []
        current = best_pellet
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()

        # Tính toán metrics khi tìm thấy đường
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        path_length = len(path)

        # Ước lượng memory usage
        memory_usage = self._estimate_memory_usage(len(visited), path_length, len(pq), len(g_score), len(came_from))

        # Cập nhật metrics vào game
        self._update_metrics(execution_time, expanded_nodes, path_length, memory_usage, True)
        return path

    def _estimate_memory_usage(self, visited_count, path_length, queue_size, g_score_size, came_from_size=0):
        """Ước lượng memory usage cho A* dựa trên kích thước dữ liệu"""
        # Mỗi node trong visited: ước lượng 50 bytes
        # Mỗi node trong path: ước lượng 30 bytes
        # Mỗi phần tử trong priority queue: ước lượng 100 bytes (phức tạp hơn vì chứa nhiều thông tin)
        # Mỗi entry trong g_score: ước lượng 60 bytes
        # Mỗi entry trong came_from: ước lượng 60 bytes
        # Các cấu trúc khác: ước lượng thêm
        base_memory = 60  # KB cho các biến và cấu trúc cơ bản
        visited_memory = visited_count * 0.05  # KB
        path_memory = path_length * 0.03  # KB
        queue_memory = queue_size * 0.10  # KB cho priority queue (lớn hơn vì chứa f, g, pos, path)
        g_score_memory = g_score_size * 0.06  # KB cho g_score dictionary
        came_from_memory = came_from_size * 0.06  # KB cho came_from dictionary

        total_kb = base_memory + visited_memory + path_memory + queue_memory + g_score_memory + came_from_memory
        return total_kb

    def _update_metrics(self, execution_time, expanded_nodes, path_length, memory_usage, success):
        """Cập nhật metrics vào game"""
        self.game.metrics['execution_time'] = execution_time
        self.game.metrics['expanded_nodes'] = expanded_nodes
        self.game.metrics['path_lengths'].append(path_length)
        self.game.metrics['memory_usage'] = max(self.game.metrics['memory_usage'], memory_usage)
        self.game.metrics['success'] = 1 if success else 0
        self.game.metrics['calls'] += 1