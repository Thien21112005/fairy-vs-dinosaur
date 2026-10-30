import heapq
import time

from fairy_vs_dinosaur.pathfinding.base import BasePathFinder


class GreedyPathFinder(BasePathFinder):
    BASE_MEMORY_KB = 50

    def find_path_to_nearest_pellet(self, start_row, start_col):
        start_time = time.time()

        start = (start_row, start_col)
        pellets = self._pellets()
        if not pellets:
            return []

        pq = [(self._distance_to_nearest(start, pellets), start, None)]  # (h, current, came_from)
        came_from = {start: None}
        visited = set()
        expanded_nodes = 0

        while pq:
            _, current, _ = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)
            expanded_nodes += 1

            if self._is_pellet(*current) and current != start:
                # Lấy pellet đầu tiên tìm được, không đảm bảo tối ưu
                path = self._reconstruct(came_from, current)
                return self._finish(start_time, expanded_nodes, path, len(visited),
                                    len(pq) * 0.08, len(came_from) * 0.06)

            for next_pos in self._neighbors(*current):
                if self._is_blocked(*next_pos) or self._get_cost(*next_pos) > 100:  # Bỏ qua ô quá gần ghost
                    continue
                if next_pos not in visited:
                    heapq.heappush(pq, (self._distance_to_nearest(next_pos, pellets), next_pos, current))
                    came_from[next_pos] = current

        return self._finish(start_time, expanded_nodes, [], len(visited), len(pq) * 0.08, len(came_from) * 0.06)
