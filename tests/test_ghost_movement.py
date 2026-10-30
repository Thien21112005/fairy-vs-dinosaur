import unittest

import pygame

from fairy_vs_dinosaur.entities.path_drawing import blit_wrapped
from tests.helpers import make_game, run_until, use_ai


def run_frames(game, frames, on_frame):
    count = [0]

    def condition(_):
        count[0] += 1
        on_frame()
        return count[0] >= frames
    run_until(game, condition, frames + 1)


class TunnelTest(unittest.TestCase):
    def place_in_tunnel(self, ghost, game, col, direction):
        ghost.release_timer = 0
        ghost.row, ghost.col = 15, col
        ghost.x = col * game.num2_c + game.num2_c / 2.0
        ghost.y = 15 * game.num1_r + game.num1_r / 2.0
        ghost.direction = direction
        ghost.choose_direction = lambda: None  # Keep walking straight through the tunnel

    def test_ghost_keeps_moving_after_crossing_the_tunnel(self):
        for level in [1, 5]:
            with self.subTest(level=level):
                game = make_game()
                game.level_num = level
                game.blinky.apply_level_difficulty()
                game.game_started = True
                game.show_ready = False
                ghost = game.blinky
                self.place_in_tunnel(ghost, game, 2, 1)

                positions = []
                for _ in range(200):
                    ghost.update(16)
                    positions.append(ghost.x)
                moved = [abs(b - a) for a, b in zip(positions, positions[1:])]
                self.assertTrue(any(m > 100 for m in moved), "ghost never crossed")
                crossed = next(i for i, m in enumerate(moved) if m > 100)
                # Row 15 is open for about 11 cells past the edge, so check the walk before the next wall
                self.assertTrue(all(m > 0.1 for m in moved[crossed + 1:crossed + 80]), "ghost stalled after crossing")

    def test_sprite_is_drawn_on_both_sides_while_crossing(self):
        screen = pygame.Surface((100, 50))
        image = pygame.Surface((20, 20))
        image.fill((255, 0, 0))
        blit_wrapped(screen, image, -10, 0)
        self.assertEqual(screen.get_at((5, 5))[:3], (255, 0, 0))
        self.assertEqual(screen.get_at((95, 5))[:3], (255, 0, 0))

    def test_collision_works_across_the_tunnel_edge(self):
        game = make_game()
        game.player.x, game.player.y = 2, 279
        game.blinky.x, game.blinky.y = 598, 279
        self.assertTrue(game.check_collision(game.player, game.blinky))


class TurnDecisionTest(unittest.TestCase):
    def test_ghosts_decide_at_every_cell_at_any_speed(self):
        for level, frame_times in [(1, (16, 17, 17)), (5, (16, 17, 17)), (5, (33,))]:
            with self.subTest(level=level, frame_times=frame_times):
                game = make_game(frame_times)
                use_ai(game, "BFS")
                game.check_ghost_collisions = lambda: None
                game.level_num = level
                for ghost in game.ghosts:
                    ghost.apply_level_difficulty()

                seen = {"cells": 0, "missed": 0}
                ghost = game.blinky
                last = [(ghost.row, ghost.col)]

                def on_frame():
                    cell = (ghost.row, ghost.col)
                    if cell != last[0] and not game.dying:
                        seen["cells"] += 1
                        if ghost.decided_cell != last[0]:
                            seen["missed"] += 1
                        last[0] = cell
                run_frames(game, 1500, on_frame)
                self.assertGreater(seen["cells"], 30)
                self.assertLessEqual(seen["missed"] / seen["cells"], 0.02)


if __name__ == "__main__":
    unittest.main()
