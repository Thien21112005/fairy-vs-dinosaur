import heapq
import time

from fairy_vs_dinosaur.pathfinding.base import BasePathFinder


class UCSPathFinder(BasePathFinder):
    BASE_MEMORY_KB = 60

    def find_path_to_nearest_pellet(self, start_row, start_col):
        """Tìm đường đến pellet 'rẻ' nhất (tổng cost thấp nhất)"""
        start_time = time.time()

        start = (start_row, start_col)
        pq = [(0, start, None)]  # (total_cost, current_pos, came_from_pos)
        came_from = {start: None}
        cost_so_far = {start: 0}
        visited = set()
        expanded_nodes = 0

        while pq:
            current_cost, current, _ = heapq.heappop(pq)
            expanded_nodes += 1

            if current in visited:
                continue
            visited.add(current)

            # Chi phí không âm nên hạt đầu tiên lấy ra khỏi hàng đợi là hạt rẻ nhất
            if self._is_pellet(*current) and current != start:
                path = self._reconstruct(came_from, current)
                return self._finish(start_time, expanded_nodes, path, len(visited),
                                    len(pq) * 0.08, len(cost_so_far) * 0.06)

            for next_pos in self._neighbors(*current):
                if self._is_blocked(*next_pos):
                    continue
                new_cost = current_cost + self._get_cost(*next_pos)
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    heapq.heappush(pq, (new_cost, next_pos, current))
                    came_from[next_pos] = current

        return self._finish(start_time, expanded_nodes, [], len(visited), len(pq) * 0.08, len(cost_so_far) * 0.06)
