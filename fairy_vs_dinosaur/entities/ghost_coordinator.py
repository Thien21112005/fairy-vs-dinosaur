from fairy_vs_dinosaur.pathfinding.game_model import DISTANCE, FAIRY_MOVES

CORRIDOR_LIMIT = 12  # Số ô tối đa khi lần theo một hành lang để tìm lối thoát
CLOSE_ENOUGH = 3  # Đã sát fairy thì lao thẳng vào thay vì đi chặn


class GhostCoordinator:
    """Chia các lối thoát của fairy cho khủng long, để chúng ép từ nhiều phía thay vì cùng đuổi một đường."""

    def __init__(self, game):
        self.game = game
        self.exits = []
        self.assigned = {}
        self._planned_for = None

    def escape_exits(self):
        """Ngã rẽ gần nhất theo từng hướng fairy có thể đi, hướng đang đi đứng đầu."""
        player = self.game.player
        here = (player.row, player.col)
        if here not in FAIRY_MOVES:
            return []

        step = self.game.bfs_finder.directions[player.direction]
        ahead = self.game.bfs_finder.wrap_step(player.row, player.col, step[0], step[1])
        first_moves = sorted(FAIRY_MOVES[here], key=lambda cell: cell != ahead)
        return [self._follow_corridor(here, move) for move in first_moves]

    @staticmethod
    def _follow_corridor(start, first_move):
        previous, current = start, first_move
        for _ in range(CORRIDOR_LIMIT):
            forward = [cell for cell in FAIRY_MOVES[current] if cell != previous]
            if len(forward) != 1:
                break
            previous, current = current, forward[0]
        return current

    def _plan(self):
        """Pinky chặn lối phía trước, Inky chặn lối nó tới nhanh nhất trong số còn lại, Clyde lấy phần còn lại."""
        game = self.game
        player_cell = (game.player.row, game.player.col)
        key = (player_cell, game.player.direction)
        if key == self._planned_for:
            return
        self._planned_for = key

        self.assigned = {}
        free = self.escape_exits()
        for ghost in (game.pinky, game.inky, game.clyde):
            if free:
                ghost_cell = (ghost.row, ghost.col)
                choice = free[0] if ghost is game.pinky else min(free, key=lambda cell: DISTANCE[ghost_cell].get(cell, 99))
                self.assigned[ghost.name] = choice
                free.remove(choice)

    def target_for(self, ghost):
        self._plan()
        game = self.game
        player_cell = (game.player.row, game.player.col)
        ghost_cell = (ghost.row, ghost.col)
        target = self.assigned.get(ghost.name, player_cell)
        if target == ghost_cell or DISTANCE[ghost_cell].get(player_cell, 99) <= CLOSE_ENOUGH:
            return player_cell
        return target
