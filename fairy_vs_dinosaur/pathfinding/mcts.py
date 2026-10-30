import math
import random
import time

from fairy_vs_dinosaur.pathfinding.base import BasePathFinder
from fairy_vs_dinosaur.pathfinding.game_model import CHASE_PROBABILITY, GameModel

ITERATIONS = 90  # Số ván giả lập mỗi lượt
TREE_DEPTH = 4
ROLLOUT_DEPTH = 8
EXPLORATION = 0.5
SCORE_SCALE = 30.0  # Đưa điểm về cùng thang với hệ số khám phá
DISCOUNT = 0.9  # Điểm đến sớm có giá trị hơn, để fairy không chần chừ quanh một hạt

PELLET_REWARD = 10
POWER_REWARD = 30
GHOST_REWARD = 200
DEATH_PENALTY = -500


class _Node:
    __slots__ = ("visits", "total", "children")

    def __init__(self):
        self.visits = 0
        self.total = 0.0
        self.children = {}


class MCTSPathFinder(BasePathFinder):
    """Giả lập nhiều ván ngắn từ vị trí hiện tại, dần tập trung vào các nước cho kết quả tốt, rồi chọn nước đi nhiều nhất."""

    BASE_MEMORY_KB = 40

    def find_path_to_nearest_pellet(self, start_row, start_col):
        start_time = time.time()
        self.model = GameModel(self.game)
        if not self.model.pellets:
            return []

        root = _Node()
        for _ in range(ITERATIONS):
            self._simulate(root)

        best_move = max(self._safe_moves(), key=lambda move: root.children[move].visits)
        path = self.model.route_to_pellet(best_move)
        return self._finish(start_time, ITERATIONS, path, ITERATIONS, len(root.children) * 0.1)

    def _safe_moves(self):
        """Giả lập có yếu tố ngẫu nhiên nên không được phép chọn nước đi thẳng vào cạnh khủng long nếu còn lối khác."""
        model = self.model
        moves = model.fairy_moves[model.fairy]
        danger = [cell for cell, vulnerable in model.ghosts if not vulnerable]
        safe = [move for move in moves if all(model.ghost_gap(cell, move) > 2 for cell in danger)]
        return safe or moves

    def _simulate(self, root):
        model = self.model
        fairy = model.fairy
        ghosts = list(model.ghosts)
        eaten = set()
        frightened_left = model.frightened_steps
        score = 0.0
        weight = 1.0
        visited = [root]
        node = root

        for ply in range(TREE_DEPTH + ROLLOUT_DEPTH):
            if ply < TREE_DEPTH:
                move, node = self._select(node, fairy)
                visited.append(node)
            else:
                move = self._rollout_move(fairy, ghosts)
            fairy = move

            pellet = model.pellets.get(fairy)
            if pellet and fairy not in eaten:
                eaten.add(fairy)
                score += weight * (POWER_REWARD if pellet == 2 else PELLET_REWARD)

            ghosts, gained, dead = self._step_ghosts(fairy, ghosts, frightened_left > 0)
            score += weight * gained
            if dead:
                score += weight * DEATH_PENALTY
                break
            frightened_left -= 1
            weight *= DISCOUNT
        else:
            score -= weight * model.pellet_distance.get(fairy, 30)

        for visited_node in visited:
            visited_node.visits += 1
            visited_node.total += score / SCORE_SCALE

    def _select(self, node, fairy):
        """Chọn nước theo UCB1: thử mọi nước một lần, sau đó cân bằng giữa nước tốt và nước ít được thử."""
        moves = self.model.fairy_moves[fairy]
        for move in moves:
            if move not in node.children:
                node.children[move] = _Node()
                return move, node.children[move]

        log_visits = math.log(node.visits + 1)

        def ucb(move):
            child = node.children[move]
            return child.total / child.visits + EXPLORATION * math.sqrt(log_visits / child.visits)

        # Vị trí có thể khác nhau giữa các lần giả lập nên một số nhánh có thể chưa từng được lượt qua
        best = max((m for m in moves if node.children[m].visits > 0), key=ucb, default=moves[0])
        return best, node.children[best]

    def _rollout_move(self, fairy, ghosts):
        """Ở phần giả lập nhanh, fairy đi về phía hạt gần nhất và tránh ô sát khủng long."""
        model = self.model
        danger = {cell for cell, vulnerable in ghosts if not vulnerable}

        def rank(move):
            near_ghost = any(model.ghost_gap(cell, move) <= 1 for cell in danger)
            return (near_ghost, model.pellet_distance.get(move, 99), random.random())
        return min(model.fairy_moves[fairy], key=rank)

    def _step_ghosts(self, fairy, ghosts, frightened):
        """Mỗi khủng long đi một bước theo xác suất; trả về vị trí mới, điểm săn được và fairy còn sống không."""
        model = self.model
        moved = []
        gained = 0
        for cell, vulnerable in ghosts:
            vulnerable = vulnerable and frightened
            if cell == fairy:
                if not vulnerable:
                    return moved, gained, True
                gained += GHOST_REWARD
                continue
            if random.random() > model.ghost_speed:
                moved.append((cell, vulnerable))
                continue
            options = model.ranked_ghost_moves(cell, fairy, vulnerable)
            choice = options[0] if len(options) == 1 or random.random() < CHASE_PROBABILITY else options[1]
            if choice == fairy:
                if not vulnerable:
                    return moved, gained, True
                gained += GHOST_REWARD
                continue
            moved.append((choice, vulnerable))
        return moved, gained, False
