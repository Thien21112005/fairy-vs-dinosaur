import time
from collections import deque

from fairy_vs_dinosaur.pathfinding.base import BasePathFinder


class BFSPathFinder(BasePathFinder):
    BASE_MEMORY_KB = 100

    def find_full_path(self, start_row, start_col, target_row, target_col, ghost=None):
        """Đường ngắn nhất tới một ô cụ thể. Ghost dùng hàm này nên không tính vào metrics của người chơi."""
        start = (start_row, start_col)
        target = (target_row, target_col)
        if start == target:
            return []

        queue = deque([(start, [start])])
        visited = {start}

        if ghost:
            is_blocked = lambda r, c: self.game.level.checktuong_for_ghost(r, c, ghost)
        else:
            is_blocked = self._is_blocked

        while queue:
            current, path = queue.popleft()

            if current == target:
                return path

            for next_pos in self._neighbors(*current):
                if not is_blocked(*next_pos) and next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))

        return []

    def find_path_to_nearest_pellet(self, start_row, start_col):
        start_time = time.time()

        start = (start_row, start_col)
        queue = deque([start])
        visited = {start}
        came_from = {start: None}
        expanded_nodes = 0

        while queue:
            current = queue.popleft()
            expanded_nodes += 1

            if self._is_pellet(*current) and current != start:
                return self._finish(start_time, expanded_nodes, self._reconstruct(came_from, current), len(visited))

            for next_pos in self._neighbors(*current):
                if not self._is_blocked(*next_pos) and next_pos not in visited:
                    visited.add(next_pos)
                    queue.append(next_pos)
                    came_from[next_pos] = current

        return self._finish(start_time, expanded_nodes, [], len(visited))
