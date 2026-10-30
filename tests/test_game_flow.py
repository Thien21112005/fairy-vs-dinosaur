import json
import os
import unittest

import pygame

from fairy_vs_dinosaur.config import HISTORY_FILE
from tests.helpers import hide_ghosts, make_game, run_until, use_ai


class DeathResetTest(unittest.TestCase):
    def test_returning_ghost_sound_stops_on_death(self):
        game = make_game()
        game.game_started = True
        game.blinky.start_returning_home()
        game.start_death_sequence()
        game.reset_after_death()
        self.assertFalse(game.sound_manager.turn_egg_channel.get_busy())

    def test_special_ghost_states_are_cleared(self):
        game = make_game()
        game.game_started = True
        game.pinky.start_eaten_animation()
        game.inky.start_hatching()
        game.start_death_sequence()
        game.reset_after_death()
        self.assertFalse(game.pinky.eaten)
        self.assertFalse(game.inky.hatching)


class PauseTest(unittest.TestCase):
    def test_power_sound_returns_after_countdown(self):
        game = make_game()
        game.game_started = True
        game.mode_manager.activate_frightened()
        game.pause_menu.pause_game()
        game.pause_menu.resume_game()
        game.countdown_timer = 0.001
        game._run_frame(16, 0.016)
        self.assertIs(game.sound_manager.power_channel.get_sound(), game.sound_manager.power_pellet_sound)


class NextLevelTest(unittest.TestCase):
    def test_modes_reset_and_ghosts_get_faster(self):
        game = make_game()
        game.fade_in = lambda: None
        game.mode_manager.activate_frightened()
        game.mode_manager.current_phase = 3
        speed_on_level_one = game.pinky.normal_speed_multiplier

        game.level_num = 2
        game.reset_for_next_level()

        self.assertFalse(game.mode_manager.frightened_active)
        self.assertEqual(game.mode_manager.current_phase, 0)
        self.assertGreater(game.pinky.normal_speed_multiplier, speed_on_level_one)
        self.assertEqual(game.blinky.elroy1_threshold, 30)

    def test_menu_background_is_captured_again(self):
        game = make_game()
        game.level_menu.background_surface = pygame.Surface((1, 1))
        game.level_menu.open()
        self.assertIsNone(game.level_menu.background_surface)


class HistoryTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)

    def test_completed_level_is_recorded_with_real_metrics(self):
        game = make_game()
        hide_ghosts(game)
        use_ai(game, "BFS")
        self.assertIsNotNone(run_until(game, lambda g: g.level_anim.active, 6000))

        with open(HISTORY_FILE, encoding="utf-8") as f:
            entry = json.load(f)[-1]
        self.assertEqual(entry["algorithm"], "BFS")
        self.assertEqual(entry["level"], 1)
        self.assertEqual(entry["success_rate"], 100)
        self.assertGreaterEqual(entry["path_length"], game.level.initial_pellets)
        self.assertGreater(entry["expanded_nodes"], entry["path_length"])

    def test_ghost_pathfinding_does_not_touch_player_metrics(self):
        game = make_game()
        game.bfs_finder.find_full_path(12, 15, 24, 15, game.blinky)
        self.assertEqual(game.metrics["calls"], 0)
        self.assertEqual(game.metrics["expanded_nodes"], 0)


class LevelCompleteFlowTest(unittest.TestCase):
    def test_animation_leads_to_menu_and_next_level(self):
        game = make_game()
        hide_ghosts(game)
        use_ai(game, "BFS")
        self.assertIsNotNone(run_until(game, lambda g: g.show_level_complete, 6000))

        game.level_menu.continue_game()
        self.assertEqual(game.level_num, 2)
        self.assertEqual(game.level.remaining_pellets, game.level.initial_pellets)

    def test_space_does_not_teleport_the_player(self):
        game = make_game()
        game.show_ready = False
        position = game.player.row, game.player.col
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0, unicode=" "))
        game.handle_events()
        self.assertEqual((game.player.row, game.player.col), position)


class GameOverTest(unittest.TestCase):
    def test_losing_all_lives_shows_game_over_and_can_return_to_menu(self):
        game = make_game()
        use_ai(game, "BFS")
        self.assertIsNotNone(run_until(game, lambda g: g.ui.game_over.visible, 20000))

        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, mod=0, unicode=""))
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode=""))
        game._frame_game_over()
        self.assertEqual(game.return_code, "menu")


if __name__ == "__main__":
    unittest.main()
