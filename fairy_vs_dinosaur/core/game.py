import os

import pygame

from fairy_vs_dinosaur.audio.sound_manager import SoundManager
from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.core.board import boards
from fairy_vs_dinosaur.core.game_input import GameInputMixin
from fairy_vs_dinosaur.core.game_render import GameRenderMixin
from fairy_vs_dinosaur.core.game_states import GameStatesMixin
from fairy_vs_dinosaur.core.history_log import append_history, new_metrics
from fairy_vs_dinosaur.core.level import Level
from fairy_vs_dinosaur.core.modes import ModeManager
from fairy_vs_dinosaur.entities.blinky import Blinky
from fairy_vs_dinosaur.entities.clyde import Clyde
from fairy_vs_dinosaur.entities.inky import Inky
from fairy_vs_dinosaur.entities.pinky import Pinky
from fairy_vs_dinosaur.entities.player import Player
from fairy_vs_dinosaur.pathfinding.astar import AStarPathFinder
from fairy_vs_dinosaur.pathfinding.beam import BeamPathFinder
from fairy_vs_dinosaur.pathfinding.bfs import BFSPathFinder
from fairy_vs_dinosaur.pathfinding.dfs import DFSPathFinder
from fairy_vs_dinosaur.pathfinding.greedy import GreedyPathFinder
from fairy_vs_dinosaur.pathfinding.hill_climbing import HillClimbingPathFinder
from fairy_vs_dinosaur.pathfinding.ucs import UCSPathFinder
from fairy_vs_dinosaur.settings_store import load_settings
from fairy_vs_dinosaur.ui.hud import UI
from fairy_vs_dinosaur.ui.level_complete import LevelCompleteAnimation, LevelCompleteMenu
from fairy_vs_dinosaur.ui.pause_menu import PauseMenu


MAX_FRAME_MS = 50  # Giới hạn bước thời gian để không đi xuyên tường khi bị giật hoặc kéo cửa sổ


class PacmanGame(GameInputMixin, GameRenderMixin, GameStatesMixin):
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.mixer.init()

        self.width = 600
        self.height = 700
        self.screen = pygame.display.set_mode([self.width, self.height], pygame.NOFRAME)
        self.timer = pygame.time.Clock()
        self.fps = 60
        self.running = True
        self.return_code = None

        self._init_layout()
        self._init_state()
        self._init_components()
        self._load_images()

        self.settings = load_settings()
        self.control_scheme = self.settings.get("control_scheme", "Arrow Keys")
        self.sound_manager.apply_settings(self.settings)

    def _init_layout(self):
        self.row = len(boards)
        self.col = 30
        self.y_offset = 50
        self.bottom_offset = 50
        self.num1_r = (self.height - self.y_offset - self.bottom_offset) // self.row
        self.num2_c = self.width // self.col
        self.pac_w = int(min(self.num2_c, self.num1_r) * 2)
        self.pac_h = self.pac_w
        self.frame_ms = 35
        self.move_delay_ms = 150
        self.speed_h = self.num2_c / (self.move_delay_ms / 1000.0)
        self.speed_v = self.num1_r / (self.move_delay_ms / 1000.0)

    def _init_state(self):
        self.score = 0
        self.high_score = 1000
        self.lives = 3
        self.level_num = 1
        self.play_time = 0.0

        self.dying = False
        self.death_animation_time = 0
        self.death_animation_duration = 2000  # ms
        self.game_over = False
        self.fade_alpha = 0

        self.show_ready = True
        self.intro_played = False
        self.game_started = False
        self.show_level_complete = False

        self.show_hint = False
        self.saved_hint_state = False  # Trạng thái hint trước chuỗi chết
        self.hint_restored = False
        self.just_reset = False
        self.reset_delay = 500  # ms
        self.reset_timer = 0

        self.countdown_active = False
        self.countdown_timer = 0
        self.last_count = 0

        self.eaten_ghosts_count = 0  # Số ghost đã ăn trong lần frightened hiện tại
        self.floating_scores = []  # Mỗi item: (points, x, y, timer_ms)

        self.ai_mode = False
        self.manual_mode = False
        self.solve_locked = False
        self.metrics = new_metrics()

    def _init_components(self):
        self.level = Level(self)
        self.mode_manager = ModeManager(self)
        self.sound_manager = SoundManager()
        self.ui = UI(self)
        self.bfs_finder = BFSPathFinder(self)
        self.path_finders = {
            "BFS": self.bfs_finder,
            "DFS": DFSPathFinder(self),
            "UCS": UCSPathFinder(self),
            "ASTAR": AStarPathFinder(self),
            "GREEDY": GreedyPathFinder(self),
            "HILL CLIMBING": HillClimbingPathFinder(self),
            "BEAM": BeamPathFinder(self),
        }
        self.path_finder = self.bfs_finder
        self.player = Player(self)
        self.blinky = Blinky(self)
        self.pinky = Pinky(self)
        self.inky = Inky(self)
        self.clyde = Clyde(self)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]
        self.pause_menu = PauseMenu(self)
        self.level_anim = LevelCompleteAnimation(self)
        self.level_menu = LevelCompleteMenu(self)
        self.ready_timer = self.sound_manager.intro_sound.get_length() * 1000  # ms

    def _load_images(self):
        background = pygame.image.load(asset("images/tiles/background.jpeg")).convert()
        self.background = pygame.transform.scale(background, (600, 600))

        score_size = (int(self.num2_c * 2.5), int(self.num1_r * 2.5))
        self.score_images = {}
        for points in [200, 400, 800, 1600]:
            image = pygame.image.load(asset(f"images/score/{points}.png")).convert_alpha()
            self.score_images[points] = pygame.transform.smoothscale(image, score_size)

    def visible_ghosts(self):
        return [ghost for ghost, shown in zip(self.ghosts, self.ui.visible_ghost_flags()) if shown]

    def restart_game(self):
        """Khởi động lại game hoàn toàn"""
        self.sound_manager.stop_all_sounds()
        self.player.clear_path()
        self.__init__()

    def run(self):
        self.running = True
        self.fade_in()

        while self.running:
            if self.return_code == 'menu':
                self.player.clear_path()
                break
            dt = min(self.timer.tick(self.fps), MAX_FRAME_MS)
            self._run_frame(dt, dt / 1000.0)
        return self.return_code

    def check_collision(self, player, ghost):
        distance = ((player.x - ghost.x) ** 2 + (player.y - ghost.y) ** 2) ** 0.5
        collision_radius = min(player.pac_w, player.pac_h, ghost.ghost_w, ghost.ghost_h) * 0.3
        return distance < collision_radius

    def check_ghost_collisions(self):
        for ghost in self.visible_ghosts():
            if ghost.eaten or ghost.eating or ghost.returning_home:
                continue

            if self.check_collision(self.player, ghost):
                if self.mode_manager.frightened_active:
                    self.sound_manager.play_magic()
                    ghost.start_eaten_animation()
                    self.eaten_ghosts_count += 1
                    points = 200 * (2 ** (min(self.eaten_ghosts_count, 4) - 1))  # 200, 400, 800, 1600
                    self.score += points
                    self.floating_scores.append((points, ghost.x, ghost.y + self.y_offset, 1000))
                elif not self.dying:
                    ghost.start_eating()
                    self.start_death_sequence()

    def start_death_sequence(self):
        self.saved_hint_state = self.show_hint
        self.show_hint = False
        self.hint_restored = False

        for ghost in self.ghosts:
            ghost.path = []

        self.dying = True
        self.death_animation_time = 0
        self.fade_alpha = 0

        self.sound_manager.stop_ghost()
        self.sound_manager.stop_power()
        self.sound_manager.stop_turn_egg()
        self.sound_manager.stop_egg_hatch()
        self.sound_manager.play_death()

        self.player.die()
        self.game_started = False

    def reset_after_death(self):
        for ghost in self.ghosts:
            ghost.reset_to_start()

        self.player.place_at_start()
        self.player.dead = False
        self.player.clear_path()

        self.just_reset = True
        self.reset_timer = 0
        self.show_ready = True
        self.ready_timer = 2000  # ms
        self.game_started = False
        self.mode_manager.frightened_active = False
        self.eaten_ghosts_count = 0
        self.sound_manager.stop_power()
        self.floating_scores = []

        if not self.game_over:
            self.sound_manager.play_ghost_move()

    def reset_for_next_level(self):
        self.level.load_board(boards)
        self.mode_manager.reset()
        for ghost in self.ghosts:
            ghost.reset_to_start()
            ghost.apply_level_difficulty()

        self.player.reset()
        self.eaten_ghosts_count = 0
        self.floating_scores = []

        self.show_ready = True
        self.ready_timer = self.sound_manager.intro_sound.get_length() * 1000
        self.game_started = False
        self.intro_played = False
        self.play_time = 0.0
        self.countdown_active = False
        self.just_reset = False
        self.dying = False
        self.game_over = False
        self.metrics = new_metrics()

        self.sound_manager.stop_all_sounds()
        self.fade_in()

    def record_game_history(self, success=True):
        """Ghi kết quả ván chơi vào history. Chỉ ghi khi dùng AI."""
        if not self.ai_mode:
            return
        append_history(self.ui.selected_solve, self.level_num, self.metrics, success, self.play_time, self.score)
