import heapq
import time

from fairy_vs_dinosaur.pathfinding.base import BasePathFinder


class AStarPathFinder(BasePathFinder):
    BASE_MEMORY_KB = 60

    def find_path_to_nearest_pellet(self, start_row, start_col):
        start_time = time.time()

        start = (start_row, start_col)
        pellets = self._pellets()
        if not pellets:
            return []

        pq = [(self._distance_to_nearest(start, pellets), 0, start, None)]  # (f, g, current, came_from)
        came_from = {start: None}
        g_score = {start: 0}
        visited = set()
        expanded_nodes = 0

        best_pellet = None
        best_cost = float('inf')

        while pq:
            _, g, current, _ = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)
            expanded_nodes += 1

            if self._is_pellet(*current) and current != start and g < best_cost:
                best_cost = g
                best_pellet = current

            for next_pos in self._neighbors(*current):
                if self._is_blocked(*next_pos):
                    continue
                tentative_g = g + self._get_cost(*next_pos)
                if next_pos not in g_score or tentative_g < g_score[next_pos]:
                    g_score[next_pos] = tentative_g
                    f_new = tentative_g + self._distance_to_nearest(next_pos, pellets)
                    heapq.heappush(pq, (f_new, tentative_g, next_pos, current))
                    came_from[next_pos] = current

        path = self._reconstruct(came_from, best_pellet) if best_pellet else []
        return self._finish(start_time, expanded_nodes, path, len(visited),
                            len(pq) * 0.10, len(g_score) * 0.06, len(came_from) * 0.06)
