import time

from fairy_vs_dinosaur.pathfinding.base import BasePathFinder


class BeamPathFinder(BasePathFinder):
    BASE_MEMORY_KB = 60

    def __init__(self, game, beam_width=5):
        super().__init__(game)
        self.beam_width = beam_width
        self.max_depth = 200  # Ngăn loop vô tận/treo

    def find_path_to_nearest_pellet(self, start_row, start_col):
        start_time = time.time()

        start = (start_row, start_col)
        pellets = self._pellets()
        if not pellets:
            return []

        beam = [(self._distance_to_nearest(start, pellets), 0, start, None)]  # (f, g, current, came_from)
        came_from = {start: None}
        visited = {start}
        expanded_nodes = 0
        depth = 0

        def extra_memory(new_beam_size):
            return (len(beam) * 0.10, new_beam_size * 0.10, len(came_from) * 0.06, depth * 0.02)

        while beam and depth < self.max_depth:
            new_beam = []
            for _, g, current, _ in beam:
                expanded_nodes += 1

                if self._is_pellet(*current) and current != start:
                    path = self._reconstruct(came_from, current)
                    return self._finish(start_time, expanded_nodes, path, len(visited), *extra_memory(len(new_beam)))

                for next_pos in self._neighbors(*current):
                    if self._is_blocked(*next_pos) or self._get_cost(*next_pos) > 100 or next_pos in visited:
                        continue
                    new_g = g + self._get_cost(*next_pos)
                    new_beam.append((new_g + self._distance_to_nearest(next_pos, pellets), new_g, next_pos, current))

            # Chỉ giữ beam_width nút có f nhỏ nhất
            new_beam.sort(key=lambda x: x[0])
            beam = new_beam[:self.beam_width]
            for _, _, pos, prev in beam:
                came_from[pos] = prev
                visited.add(pos)
            depth += 1

        return self._finish(start_time, expanded_nodes, [], len(visited), *extra_memory(0))
