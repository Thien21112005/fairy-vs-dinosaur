import random

import pygame

from fairy_vs_dinosaur.core.game import PacmanGame

REAL_FRAME_TIMES = (16, 17, 17)  # What Clock.tick(60) alternates between


class FakeClock:
    def __init__(self, frame_times=REAL_FRAME_TIMES):
        self.frame_times = frame_times
        self.index = 0

    def tick(self, *_):
        self.index += 1
        return self.frame_times[self.index % len(self.frame_times)]


class StopGame(Exception):
    pass


def make_game(frame_times=REAL_FRAME_TIMES, seed=7):
    random.seed(seed)
    game = PacmanGame()
    game.timer = FakeClock(frame_times)
    game.ready_timer = 0
    return game


def hide_ghosts(game):
    game.ui.show_blinky = game.ui.show_pinky = game.ui.show_inky = game.ui.show_clyde = False


def use_ai(game, algorithm):
    game.ai_mode = True
    game.path_finder = game.path_finders[algorithm]
    game.ui.selected_solve = algorithm


def run_until(game, condition, max_frames):
    """Run the real game loop until condition(game) holds. Returns the frames used, or None if it never did."""
    frames = [0]
    real_flip = pygame.display.flip

    def flip():
        real_flip()
        frames[0] += 1
        if condition(game) or frames[0] >= max_frames:
            raise StopGame

    pygame.display.flip = flip
    try:
        game.run()
    except StopGame:
        pass
    finally:
        pygame.display.flip = real_flip
    return frames[0] if condition(game) else None
