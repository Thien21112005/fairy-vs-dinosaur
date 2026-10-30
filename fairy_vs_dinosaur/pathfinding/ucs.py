import heapq
import time


class UCSPathFinder:
    def __init__(self, game):
        self.game = game
        self.directions = [(1, 0, 0), (-1, 0, 1), (0, -1, 2), (0, 1, 3)]  # (dx, dy, dir) - phải, trái, lên, xuống

    def find_full_path(self, start_row, start_col, target_row, target_col):
        # Đo thời gian bắt đầu
        start_time = time.time()

        start = (start_row, start_col)
        target = (target_row, target_col)
        if start == target:
            return []

        # Priority queue: (total_cost, current_pos, path)
        pq = []
        heapq.heappush(pq, (0, start, [start]))  # Bắt đầu với cost 0

        visited = set()  # Chỉ visited pos, không cần cost vì UCS visit khi pop (không như Dijkstra full)
        cost_so_far = {start: 0}  # Theo dõi cost tối thiểu đến mỗi pos
        expanded_nodes = 0

        check_func = lambda r, c: self.game.level.checktuong_for_pacman(r, c)  # Chỉ dùng cho Pacman, né ghost như tường

        while pq:
            current_cost, current, path = heapq.heappop(pq)
            row, col = current
            expanded_nodes += 1

            if current == target:
                # Tính toán metrics khi tìm thấy đường
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # ms
                path_length = len(path)

                # Ước lượng memory usage
                memory_usage = self._estimate_memory_usage(len(visited), path_length, len(pq), len(cost_so_far))

                # Cập nhật metrics vào game
                self._update_metrics(execution_time, expanded_nodes, path_length, memory_usage, True)
                return path

            if current in visited:
                continue
            visited.add(current)

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

                if check_func(next_row, next_col):  # Nếu là tường (bao gồm ghost), skip
                    continue

                # Tính cost cho ô tiếp theo (tự định nghĩa)
                step_cost = self._get_cost(next_row, next_col)
                new_cost = current_cost + step_cost

                # Nếu cost mới tốt hơn, update và push
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    heapq.heappush(pq, (new_cost, next_pos, path + [next_pos]))

        # Không tìm thấy đường
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000

        # Ước lượng memory usage
        memory_usage = self._estimate_memory_usage(len(visited), 0, len(pq), len(cost_so_far))

        self._update_metrics(execution_time, expanded_nodes, 0, memory_usage, False)
        return []  # No path found

    def find_path_to_nearest_pellet(self, start_row, start_col):
        """Tìm đường đến pellet 'rẻ' nhất (tổng cost thấp nhất) bằng UCS"""
        # Đo thời gian bắt đầu
        start_time = time.time()

        start = (start_row, start_col)

        # Priority queue: (total_cost, current_pos, came_from_pos)
        pq = []
        heapq.heappush(pq, (0, start, None))  # Bắt đầu với cost 0

        came_from = {start: None}
        cost_so_far = {start: 0}
        expanded_nodes = 0

        visited = set()

        check_func = lambda r, c: self.game.level.checktuong_for_pacman(r, c)
        is_pellet = lambda r, c: self.game.level.level[r][c] in [1, 2]

        best_pellet = None
        best_cost = float('inf')
        best_came_from = None

        while pq:
            current_cost, current, _ = heapq.heappop(pq)
            row, col = current
            expanded_nodes += 1

            if current in visited:
                continue
            visited.add(current)

            # Nếu ô hiện tại là pellet (không tính start nếu start là pellet)
            if is_pellet(row, col) and current != start:
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_pellet = current
                    best_came_from = came_from[current]
                    # Tiếp tục để tìm có thể có pellet rẻ hơn, nhưng có thể early stop nếu cần optimize

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
                        continue

                if not (0 <= next_row < self.game.row and 0 <= next_col < self.game.col):
                    continue

                next_pos = (next_row, next_col)

                if check_func(next_row, next_col):  # Tường hoặc ghost
                    continue

                step_cost = self._get_cost(next_row, next_col)
                new_cost = current_cost + step_cost

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    heapq.heappush(pq, (new_cost, next_pos, current))
                    came_from[next_pos] = current

        if best_pellet is None:
            # Không tìm thấy pellet
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000

            # Ước lượng memory usage
            memory_usage = self._estimate_memory_usage(len(visited), 0, len(pq), len(cost_so_far))

            self._update_metrics(execution_time, expanded_nodes, 0, memory_usage, False)
            return []  # No pellet found

        # Reconstruct path
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
        memory_usage = self._estimate_memory_usage(len(visited), path_length, len(pq), len(cost_so_far))

        # Cập nhật metrics vào game
        self._update_metrics(execution_time, expanded_nodes, path_length, memory_usage, True)
        return path

    def _get_cost(self, r, c):
        """Hàm tự định nghĩa cost cho mỗi ô. Chỉ tính cho ô đi được."""
        v = self.game.level.level[r][c]  # Lấy giá trị ô từ level
        base_cost = 1  # Default cost

        if v == 2:  # Power pellet: cost thấp để ưu tiên
            base_cost = 0.1
        elif v == 1:  # Normal pellet: cost trung bình
            base_cost = 0.5
        else:  # Ô trống: cost cao để tránh lãng phí thời gian quay lại
            base_cost = 2.0

        # Tăng cost nếu ô gần ghost (vùng xung quanh ghost cost siêu cao)
        penalty = self._get_ghost_penalty(r, c)
        return base_cost + penalty

    def _get_ghost_penalty(self, r, c):
        """Tính penalty nếu ô gần ghost (Manhattan distance <= 2)"""
        penalty = 0
        if self.game.mode_manager.frightened_active:
            return penalty  # Không penalty nếu frightened mode

        for ghost in self.game.ghosts:
            if not ghost.eaten and not ghost.returning_home:
                dist = abs(r - ghost.row) + abs(c - ghost.col)
                if dist <= 2:  # Vùng xung quanh ghost (bao gồm chính ghost, nhưng ghost đã là tường)
                    penalty += 100  # Cost siêu cao để né
                elif dist <= 4:  # Vùng xa hơn một chút, penalty nhẹ hơn
                    penalty += 10

        return penalty

    def _estimate_memory_usage(self, visited_count, path_length, queue_size, cost_dict_size):
        """Ước lượng memory usage cho UCS dựa trên kích thước dữ liệu"""
        # Mỗi node trong visited: ước lượng 50 bytes
        # Mỗi node trong path: ước lượng 30 bytes
        # Mỗi phần tử trong priority queue: ước lượng 80 bytes (phức tạp hơn)
        # Mỗi entry trong cost_so_far: ước lượng 60 bytes
        # Các cấu trúc khác: ước lượng thêm
        base_memory = 60  # KB cho các biến và cấu trúc cơ bản
        visited_memory = visited_count * 0.05  # KB
        path_memory = path_length * 0.03  # KB
        queue_memory = queue_size * 0.08  # KB cho priority queue
        cost_dict_memory = cost_dict_size * 0.06  # KB cho cost dictionary

        total_kb = base_memory + visited_memory + path_memory + queue_memory + cost_dict_memory
        return total_kb

    def _update_metrics(self, execution_time, expanded_nodes, path_length, memory_usage, success):
        """Cập nhật metrics vào game"""
        self.game.metrics['execution_time'] = execution_time
        self.game.metrics['expanded_nodes'] = expanded_nodes
        self.game.metrics['path_lengths'].append(path_length)
        self.game.metrics['memory_usage'] = max(self.game.metrics['memory_usage'], memory_usage)
        self.game.metrics['success'] = 1 if success else 0
        self.game.metrics['calls'] += 1
