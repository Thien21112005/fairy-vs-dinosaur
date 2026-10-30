import random
import time

from fairy_vs_dinosaur.pathfinding.base import BasePathFinder


class HillClimbingPathFinder(BasePathFinder):
    BASE_MEMORY_KB = 40
    REPLAN_EACH_CELL = False  # Đường đi ngẫu nhiên, tìm lại ở mỗi ô sẽ không tiến được

    def __init__(self, game):
        super().__init__(game)
        self.max_steps = 200  # Ngăn loop

    def find_path_to_nearest_pellet(self, start_row, start_col):
        start_time = time.time()

        start = (start_row, start_col)
        pellets = self._pellets()
        if not pellets:
            return []

        current = start
        path = [start]
        visited = {start}
        expanded_nodes = 0
        steps = 0
        neighbors = []

        while (not self._is_pellet(*current) or current == start) and steps < self.max_steps:
            expanded_nodes += 1

            neighbors = []
            for next_pos in self._neighbors(*current):
                if not self._is_blocked(*next_pos) and next_pos not in visited and self._get_cost(*next_pos) <= 100:
                    neighbors.append((self._distance_to_nearest(next_pos, pellets), next_pos))

            if not neighbors:
                break  # Kẹt

            # Chọn ngẫu nhiên trong các ô tốt hơn; nếu không có thì chọn bất kỳ để thoát kẹt
            current_h = self._distance_to_nearest(current, pellets)
            good_neighbors = [n for n in neighbors if n[0] < current_h]
            _, current = random.choice(good_neighbors or neighbors)

            path.append(current)
            visited.add(current)
            steps += 1

        success = self._is_pellet(*current) and current != start
        return self._finish(start_time, expanded_nodes, path if success else [], len(visited),
                            steps * 0.04, len(neighbors) * 0.02)
