import time
from collections import deque

from fairy_vs_dinosaur.pathfinding.base import BasePathFinder
from fairy_vs_dinosaur.pathfinding.game_model import CHASE_PROBABILITY, GameModel

MAX_NODES = 700  # Giới hạn công việc mỗi lượt để không làm giật khung hình
MAX_DEPTH = 8
NEARBY_GHOSTS = 2  # Chỉ giả lập các khủng long gần nhất, số còn lại đứng yên trong lượt tìm

PELLET_REWARD = 10
POWER_REWARD = 30
GHOST_REWARD = 200
DEATH_PENALTY = -1000
REVISIT_PENALTY = 4  # Tránh đi qua đi lại khi các nước gần bằng điểm nhau


class NodeLimitReached(Exception):
    pass


class ExpectimaxPathFinder(BasePathFinder):
    """Xen kẽ lượt fairy chọn nước tốt nhất và lượt khủng long đi theo xác suất, đào sâu dần tới khi hết giới hạn."""

    BASE_MEMORY_KB = 40

    def __init__(self, game):
        super().__init__(game)
        self.recent_cells = deque(maxlen=6)

    def find_path_to_nearest_pellet(self, start_row, start_col):
        start_time = time.time()
        self.model = GameModel(self.game)
        if not self.model.pellets:
            return []

        self.nodes = 0
        best_move = None
        depth_reached = 0
        for depth in range(1, MAX_DEPTH + 1):
            try:
                best_move = self._best_root_move(depth)
                depth_reached = depth
            except NodeLimitReached:
                break

        self.recent_cells.append(self.model.fairy)
        path = self.model.route_to_pellet(best_move) if best_move else []
        return self._finish(start_time, self.nodes, path, self.nodes, depth_reached * 0.5)

    def _best_root_move(self, depth):
        model = self.model
        best_move, best_value = None, float('-inf')
        ghosts = tuple(sorted(model.ghosts, key=lambda g: model.ghost_gap(g[0], model.fairy))[:NEARBY_GHOSTS])
        for move in model.fairy_moves[model.fairy]:
            value = self._after_fairy_move(move, ghosts, frozenset(), 0, depth)
            value -= REVISIT_PENALTY * self.recent_cells.count(move)
            if value > best_value:
                best_move, best_value = move, value
        return best_move

    def _after_fairy_move(self, fairy, ghosts, eaten, reward, depth):
        """Tính thưởng của ô vừa tới và xử lý va chạm trước khi tới lượt khủng long."""
        pellet = self.model.pellets.get(fairy)
        if pellet and fairy not in eaten:
            reward += POWER_REWARD if pellet == 2 else PELLET_REWARD
            eaten = eaten | {fairy}

        ghosts, reward, dead = self._resolve_contact(fairy, ghosts, reward)
        if dead:
            return reward + DEATH_PENALTY
        return self._ghost_layer(fairy, ghosts, 0, (), eaten, reward, depth)

    def _resolve_contact(self, fairy, ghosts, reward):
        remaining = []
        for cell, vulnerable in ghosts:
            if cell != fairy:
                remaining.append((cell, vulnerable))
            elif vulnerable:
                reward += GHOST_REWARD
            else:
                return ghosts, reward, True
        return tuple(remaining), reward, False

    def _ghost_layer(self, fairy, ghosts, index, moved, eaten, reward, depth):
        """Giá trị kỳ vọng trên các nước đi có thể của từng khủng long."""
        if index == len(ghosts):
            return self._after_ghost_moves(fairy, moved, eaten, reward, depth)

        cell, vulnerable = ghosts[index]
        options = self.model.ranked_ghost_moves(cell, fairy, vulnerable)
        likely = self._ghost_layer(fairy, ghosts, index + 1, moved + ((options[0], vulnerable),), eaten, reward, depth)
        if len(options) == 1:
            return likely
        other = self._ghost_layer(fairy, ghosts, index + 1, moved + ((options[1], vulnerable),), eaten, reward, depth)
        return CHASE_PROBABILITY * likely + (1 - CHASE_PROBABILITY) * other

    def _after_ghost_moves(self, fairy, ghosts, eaten, reward, depth):
        self.nodes += 1
        if self.nodes > MAX_NODES:
            raise NodeLimitReached

        ghosts, reward, dead = self._resolve_contact(fairy, ghosts, reward)
        if dead:
            return reward + DEATH_PENALTY
        if depth <= 1:
            return reward + self._evaluate(fairy, ghosts)
        return max(self._after_fairy_move(move, ghosts, eaten, reward, depth - 1)
                   for move in self.model.fairy_moves[fairy])

    def _evaluate(self, fairy, ghosts):
        """Điểm tại lá: gần hạt thì tốt, gần khủng long thì nguy hiểm, gần khủng long đang yếu thì nên săn."""
        model = self.model
        score = -model.pellet_distance.get(fairy, 30)
        for cell, vulnerable in ghosts:
            gap = model.ghost_gap(cell, fairy)
            if vulnerable:
                if gap < model.frightened_steps:
                    score += max(0, 20 - gap) * 2
            elif gap <= 5:
                score -= (6 - gap) ** 2 * 3
        return score
