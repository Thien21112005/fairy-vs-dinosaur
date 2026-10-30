from collections import deque

from fairy_vs_dinosaur.core.board import boards
from fairy_vs_dinosaur.core.level import GHOST_GATE, WALLS

COLS = 30
ROWS = len(boards)
STEP_SECONDS = 0.15  # Thời gian fairy đi hết một ô
CHASE_PROBABILITY = 0.8  # Xác suất khủng long chọn nước tốt nhất cho nó


def _neighbors(cell, is_open):
    r, c = cell
    wrap = boards[r][0] not in WALLS and boards[r][COLS - 1] not in WALLS
    for nr, nc in ((r, c + 1), (r, c - 1), (r - 1, c), (r + 1, c)):
        if wrap:
            nc %= COLS
        if 0 <= nr < ROWS and 0 <= nc < COLS and is_open(nr, nc):
            yield nr, nc


def _build_static_map():
    """Đồ thị ô cho fairy và khủng long, cùng khoảng cách đường đi thật giữa mọi cặp ô. Bản đồ không đổi nên chỉ tính một lần."""
    def fairy_open(r, c):
        return boards[r][c] not in WALLS

    def ghost_open(r, c):
        return boards[r][c] not in WALLS or boards[r][c] == GHOST_GATE

    cells = [(r, c) for r in range(ROWS) for c in range(COLS)]
    fairy_moves = {cell: list(_neighbors(cell, fairy_open)) for cell in cells if fairy_open(*cell)}
    ghost_moves = {cell: list(_neighbors(cell, ghost_open)) for cell in cells if ghost_open(*cell)}

    distance = {}
    for source in ghost_moves:
        seen = {source: 0}
        queue = deque([source])
        while queue:
            current = queue.popleft()
            for neighbor in ghost_moves[current]:
                if neighbor not in seen:
                    seen[neighbor] = seen[current] + 1
                    queue.append(neighbor)
        distance[source] = seen
    return fairy_moves, ghost_moves, distance


FAIRY_MOVES, GHOST_MOVES, DISTANCE = _build_static_map()


class GameModel:
    """Ảnh chụp rút gọn của ván chơi để các thuật toán giả lập trước nhiều bước."""

    def __init__(self, game):
        self.fairy_moves, self.ghost_moves, self.distance = FAIRY_MOVES, GHOST_MOVES, DISTANCE
        self.fairy = (game.player.row, game.player.col)
        self.pellets = {(r, c): game.level.level[r][c] for r in range(ROWS) for c in range(COLS)
                        if game.level.level[r][c] in (1, 2)}
        self.ghosts = [((g.row, g.col), g.is_vulnerable()) for g in game.visible_ghosts()
                       if not g.eaten and not g.returning_home and not g.hatching]
        self.ghost_speed = game.pinky.normal_speed_multiplier  # So với tốc độ fairy
        self.frightened_steps = int(game.mode_manager.frightened_timer / STEP_SECONDS) \
            if game.mode_manager.frightened_active else 0
        self.pellet_distance = self._distance_to_pellets()

    def _distance_to_pellets(self):
        """Số bước từ mỗi ô tới hạt gần nhất, tính một lần cho cả lượt tìm kiếm."""
        seen = {cell: 0 for cell in self.pellets}
        queue = deque(self.pellets)
        while queue:
            current = queue.popleft()
            for neighbor in self.fairy_moves[current]:
                if neighbor not in seen:
                    seen[neighbor] = seen[current] + 1
                    queue.append(neighbor)
        return seen

    def ghost_gap(self, ghost_cell, fairy_cell):
        return self.distance[ghost_cell].get(fairy_cell, 99)

    def ranked_ghost_moves(self, ghost_cell, fairy_cell, vulnerable):
        """Các nước của khủng long, tốt nhất cho nó đứng trước: đuổi theo, hoặc bỏ chạy nếu đang yếu."""
        return sorted(self.ghost_moves[ghost_cell], key=lambda cell: self.ghost_gap(cell, fairy_cell),
                      reverse=vulnerable)

    def route_to_pellet(self, first_step):
        """Đường hiển thị và đi theo: từ vị trí hiện tại qua nước đã chọn rồi tới hạt gần nhất."""
        path = [self.fairy, first_step]
        current = first_step
        for _ in range(ROWS + COLS):
            if self.pellet_distance.get(current, 0) == 0:
                break
            current = min(self.fairy_moves[current], key=lambda cell: self.pellet_distance.get(cell, 99))
            path.append(current)
        return path
