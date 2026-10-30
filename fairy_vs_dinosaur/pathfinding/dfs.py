import time

from fairy_vs_dinosaur.pathfinding.base import BasePathFinder


class DFSPathFinder(BasePathFinder):
    BASE_MEMORY_KB = 50
    REPLAN_EACH_CELL = False  # Tìm lại ở mỗi ô sẽ khiến DFS đi qua đi lại giữa hai ô

    def find_path_to_nearest_pellet(self, start_row, start_col):
        """Tìm đường đến pellet đầu tiên gặp được khi duyệt theo chiều sâu"""
        start_time = time.time()

        start = (start_row, start_col)
        stack = [start]
        visited = {start}
        came_from = {start: None}
        expanded_nodes = 0

        while stack:
            current = stack.pop()
            expanded_nodes += 1

            if self._is_pellet(*current) and current != start:
                path = self._reconstruct(came_from, current)
                return self._finish(start_time, expanded_nodes, path, len(visited), len(stack) * 0.06)

            for next_pos in self._neighbors(*current):
                if not self._is_blocked(*next_pos) and next_pos not in visited:
                    visited.add(next_pos)
                    stack.append(next_pos)
                    came_from[next_pos] = current

        return self._finish(start_time, expanded_nodes, [], len(visited), len(stack) * 0.06)
