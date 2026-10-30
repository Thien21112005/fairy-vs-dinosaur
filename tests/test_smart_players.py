import unittest

from fairy_vs_dinosaur.pathfinding.expectimax import MAX_NODES
from fairy_vs_dinosaur.pathfinding.game_model import GameModel
from tests.helpers import hide_ghosts, make_game, run_until, use_ai

SMART = ["EXPECTIMAX", "MCTS"]
OPEN_ROW = 24  # Fairy starts here, with open cells on both sides


def place(ghost, game, row, col, vulnerable=False):
    ghost.row, ghost.col = row, col
    ghost.x = col * game.num2_c + game.num2_c / 2.0
    ghost.y = row * game.num1_r + game.num1_r / 2.0
    ghost.is_vulnerable = lambda: vulnerable
    ghost.release_timer = 0


def scene(algorithm):
    game = make_game()
    use_ai(game, algorithm)
    hide_ghosts(game)
    game.ui.show_blinky = True
    return game, game.path_finders[algorithm]


class SmartPlayerTest(unittest.TestCase):
    def test_clears_the_level(self):
        for algorithm in SMART:
            with self.subTest(algorithm=algorithm):
                game = make_game()
                hide_ghosts(game)
                use_ai(game, algorithm)
                self.assertIsNotNone(run_until(game, lambda g: g.level.remaining_pellets <= 0, 8000))

    def test_steps_away_from_a_ghost_right_ahead(self):
        for algorithm in SMART:
            with self.subTest(algorithm=algorithm):
                game, finder = scene(algorithm)
                player = game.player
                place(game.blinky, game, player.row, player.col + 1)
                path = finder.find_path_to_nearest_pellet(player.row, player.col)
                self.assertNotEqual(path[1], (player.row, player.col + 1))

    def test_hunts_a_vulnerable_ghost_next_to_it(self):
        for algorithm in SMART:
            with self.subTest(algorithm=algorithm):
                game, finder = scene(algorithm)
                player = game.player
                game.mode_manager.frightened_active = True
                game.mode_manager.frightened_timer = 5.0
                place(game.blinky, game, player.row, player.col + 1, vulnerable=True)
                path = finder.find_path_to_nearest_pellet(player.row, player.col)
                self.assertEqual(path[1], (player.row, player.col + 1))

    def test_returned_path_is_walkable_and_starts_at_the_fairy(self):
        for algorithm in SMART:
            with self.subTest(algorithm=algorithm):
                game, finder = scene(algorithm)
                path = finder.find_path_to_nearest_pellet(game.player.row, game.player.col)
                self.assertEqual(path[0], (game.player.row, game.player.col))
                moves = GameModel(game).fairy_moves
                for current, following in zip(path, path[1:]):
                    self.assertIn(following, moves[current])

    def test_expectimax_respects_its_work_limit(self):
        game, finder = scene("EXPECTIMAX")
        for ghost in game.ghosts:
            ghost.is_vulnerable = lambda: False
        game.ui.show_pinky = game.ui.show_inky = game.ui.show_clyde = True
        finder.find_path_to_nearest_pellet(game.player.row, game.player.col)
        self.assertLessEqual(game.metrics["expanded_nodes"], MAX_NODES + 1)


if __name__ == "__main__":
    unittest.main()
