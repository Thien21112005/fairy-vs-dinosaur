import unittest

from tests.helpers import hide_ghosts, make_game, REAL_FRAME_TIMES, run_until, use_ai

CLEARS_QUICKLY = ["BFS", "UCS", "ASTAR", "GREEDY", "BEAM", "HILL CLIMBING"]


def level_cleared(game):
    return game.level.remaining_pellets <= 0


class ClearLevelTest(unittest.TestCase):
    def test_every_algorithm_clears_the_level(self):
        for algorithm in CLEARS_QUICKLY:
            with self.subTest(algorithm=algorithm):
                game = make_game()
                hide_ghosts(game)
                use_ai(game, algorithm)
                self.assertIsNotNone(run_until(game, level_cleared, 6000))

    def test_clearing_does_not_depend_on_frame_time(self):
        for frame_times in [(16,), (33,), (50,)]:
            with self.subTest(frame_times=frame_times):
                game = make_game(frame_times)
                hide_ghosts(game)
                use_ai(game, "BFS")
                self.assertIsNotNone(run_until(game, level_cleared, 6000))

    def test_dfs_keeps_making_progress(self):
        game = make_game(REAL_FRAME_TIMES)
        hide_ghosts(game)
        use_ai(game, "DFS")
        run_until(game, level_cleared, 6000)
        self.assertLess(game.level.remaining_pellets, game.level.initial_pellets - 50)


class ReversalTest(unittest.TestCase):
    def test_reverse_means_the_opposite_direction(self):
        game = make_game()
        for direction, opposite in [(0, 1), (1, 0), (2, 3), (3, 2)]:
            game.blinky.direction = direction
            game.blinky.reverse_direction()
            self.assertEqual(game.blinky.direction, opposite)


if __name__ == "__main__":
    unittest.main()
