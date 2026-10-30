import unittest

from tests.helpers import make_game, run_until, use_ai


class AStarVersusUcsTest(unittest.TestCase):
    def test_astar_matches_ucs_cost_and_never_expands_more(self):
        game = make_game()
        use_ai(game, "ASTAR")
        game.check_ghost_collisions = lambda: None
        astar = game.path_finders["ASTAR"]
        ucs = game.path_finders["UCS"]
        real_search = astar.find_path_to_nearest_pellet
        totals = {"states": 0, "astar": 0, "ucs": 0}

        def cost(path):
            return sum(astar._get_cost(*cell) for cell in path[1:])

        def compare(row, col):
            before = game.metrics["expanded_nodes"]
            ucs_path = ucs.find_path_to_nearest_pellet(row, col)
            middle = game.metrics["expanded_nodes"]
            astar_path = real_search(row, col)
            after = game.metrics["expanded_nodes"]
            if ucs_path:
                self.assertAlmostEqual(cost(astar_path), cost(ucs_path))
            totals["states"] += 1
            totals["ucs"] += middle - before
            totals["astar"] += after - middle
            return astar_path

        astar.find_path_to_nearest_pellet = compare
        run_until(game, lambda g: g.level.remaining_pellets <= 0, 4000)
        self.assertGreater(totals["states"], 100)
        self.assertLessEqual(totals["astar"], totals["ucs"])

    def test_heuristic_uses_the_tunnel_shortcut(self):
        game = make_game()
        self.assertEqual(game.bfs_finder._heuristic((15, 0), (15, 29)), 1)


if __name__ == "__main__":
    unittest.main()
