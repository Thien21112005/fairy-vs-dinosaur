import json
import os
from datetime import datetime

import pygame

from fairy_vs_dinosaur.config import asset, HISTORY_FILE
from fairy_vs_dinosaur.audio.sound_manager import SoundManager
from fairy_vs_dinosaur.core.board import boards
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


class PacmanGame:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'  # Thêm dòng này để căn giữa cửa sổ
        pygame.init()
        pygame.mixer.init()

        self.width = 600
        self.height = 700
        self.screen = pygame.display.set_mode([self.width, self.height], pygame.NOFRAME)
        self.timer = pygame.time.Clock()
        self.fps = 60
        self.running = True
        self.return_code = None

        # THÊM HÌNH NỀN
        try:
            # Load hình nền và scale về kích thước 600x600
            self.background = pygame.image.load(asset("images/tiles/background.jpeg")).convert()
            self.background = pygame.transform.scale(self.background, (600, 600))
        except:
            print("Không thể load hình nền. Sử dụng nền đen.")
            self.background = None

        self.row = len(boards)
        self.col = 30
        self.y_offset = 50
        self.bottom_offset = 50
        self.num1_r = (self.height - self.y_offset - self.bottom_offset) // self.row
        self.num2_c = self.width // self.col

        # Thêm các biến trạng thái
        self.dying = False
        self.death_animation_time = 0
        self.death_animation_duration = 2000  # 2 giây cho toàn bộ hiệu ứng
        self.game_over = False
        self.fade_alpha = 0

        # Items (pellets, walls, etc.)

        self.pac_w = int(min(self.num2_c, self.num1_r) * 2)
        self.pac_h = self.pac_w

        self.direction = 0

        self.frame_ms = 35
        self.move_delay_ms = 150
        self.speed_h = self.num2_c / (self.move_delay_ms / 1000.0)
        self.speed_v = self.num1_r / (self.move_delay_ms / 1000.0)

        self.show_ready = True
        self.intro_played = False
        self.game_started = False

        self.score = 0
        self.high_score = 1000
        self.lives = 3

        # Sounds

        self.play_time = 0.0

        # Mode management
        self.level_num = 1

        # Pellets
        # Classes
        self.level = Level(self)
        self.mode_manager = ModeManager(self)
        self.sound_manager = SoundManager()
        self.ui = UI(self)
        self.bfs_finder = BFSPathFinder(self)  # Instance for BFS
        self.dfs_finder = DFSPathFinder(self)  # Instance for DFS
        self.ucs_finder = UCSPathFinder(self)  # Instance for UCS
        self.astar_finder = AStarPathFinder(self)  # Instance for ASTAR
        self.greedy_finder = GreedyPathFinder(self)  # Instance for Greedy
        self.hill_climbing_finder = HillClimbingPathFinder(self)
        self.beam_finder = BeamPathFinder(self)
        self.path_finder = self.bfs_finder  # Default to BFS for Pacman
        self.ghost_path_finder = self.bfs_finder  # Always BFS for ghosts
        self.player = Player(self)
        self.blinky = Blinky(self)
        self.pinky = Pinky(self)
        self.inky = Inky(self)
        self.clyde = Clyde(self)
        self.pause_menu = PauseMenu(self)
        self.level_anim = LevelCompleteAnimation(self)
        self.level_menu = LevelCompleteMenu(self)
        self.show_level_complete = False
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]
        self.ready_timer = self.sound_manager.intro_sound.get_length() * 1000  # ms
        self.show_hint = False  # For toggling Blinky path
        self.just_reset = False
        self.reset_delay = 500  # 0.5 giây delay sau khi reset
        self.reset_timer = 0

        # Thêm biến để lưu trạng thái hint
        self.saved_hint_state = False  # Lưu trạng thái hint trước khi death sequence
        self.hint_restored = False  # Đánh dấu đã khôi phục hint chưa

        self.settings = load_settings()

        # Control scheme
        self.control_scheme = self.settings.get("control_scheme", "Arrow Keys")
        self.sound_manager.apply_settings(self.settings)

        # Thêm cho countdown
        self.countdown_active = False
        self.countdown_timer = 0
        self.countdown_font = pygame.font.SysFont('monospace', 100, bold=True)

        # Thêm biến đếm số ghost ăn trong frightened mode hiện tại
        self.eaten_ghosts_count = 0

        # Thêm list để theo dõi điểm số floating
        self.floating_scores = []  # Mỗi item: (points, x, y, timer_ms)

        # Load hình ảnh điểm số
        self.score_images = {}
        for points in [200, 400, 800, 1600]:
            try:
                img = pygame.image.load(asset(f"images/score/{points}.png")).convert_alpha()
                self.score_images[points] = pygame.transform.smoothscale(img, (int(self.num2_c * 2.5),
                                                                               int(self.num1_r * 2.5)))  # Scale to hơn một chút (1.5 lần)
            except:
                print(f"Không thể load {points}.png")
                self.score_images[points] = None

        # Thêm biến cho AI mode
        self.ai_mode = False

        # Thêm biến cho manual mode (chơi thủ công)
        self.manual_mode = False

        # THÊM: Biến lock solve button
        self.solve_locked = False

        # THÊM: Metrics cho history
        self.metrics = {
            'execution_time': 0.0,
            'expanded_nodes': 0,
            'path_lengths': [],
            'memory_usage': 0,
            'success': 0,
            'calls': 0
        }

        self.history_file = HISTORY_FILE

    def restart_game(self):
        """Khởi động lại game hoàn toàn"""
        # Dừng tất cả âm thanh
        self.sound_manager.stop_all_sounds()
        self.player.clear_path()
        self.__init__()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            if self.pause_menu.handle_events(event):
                continue
            elif event.type == pygame.KEYDOWN and not self.show_ready and not self.ui.game_over.visible:
                # Nếu đang ở AI mode, bỏ qua input bàn phím cho di chuyển để tránh conflict
                if self.ai_mode:
                    continue

                # Sử dụng control scheme từ settings
                if self.control_scheme == "Arrow Keys":
                    if event.key == pygame.K_RIGHT:
                        self.player.requested_direction = 0
                    elif event.key == pygame.K_LEFT:
                        self.player.requested_direction = 1
                    elif event.key == pygame.K_UP:
                        self.player.requested_direction = 2
                    elif event.key == pygame.K_DOWN:
                        self.player.requested_direction = 3
                elif self.control_scheme == "WASD":
                    if event.key == pygame.K_d:
                        self.player.requested_direction = 0
                    elif event.key == pygame.K_a:
                        self.player.requested_direction = 1
                    elif event.key == pygame.K_w:
                        self.player.requested_direction = 2
                    elif event.key == pygame.K_s:
                        self.player.requested_direction = 3
                elif self.control_scheme == "Mixed":
                    if event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.player.requested_direction = 0
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.player.requested_direction = 1
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        self.player.requested_direction = 2
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.player.requested_direction = 3

                # THÊM: Nếu nhấn key di chuyển, kích hoạt manual mode (chơi thủ công) và lock solve
                if event.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_d, pygame.K_a,
                                 pygame.K_w, pygame.K_s]:
                    self.manual_mode = True
                    self.ai_mode = False  # Tắt AI nếu đang bật
                    self.solve_locked = True  # Lock solve button
                    # THÊM: Đóng menu solve nếu đang mở
                    if self.ui.solve_menu_visible:
                        self.ui.solve_menu_visible = False

                if event.key == pygame.K_SPACE:
                    self.player.col = 15 if self.player.col == 14 else 14
                    self.player.row = 24
                    self.player.x = self.player.col * self.num2_c + self.num2_c / 2.0
                    self.player.y = self.player.row * self.num1_r + self.num1_r / 2.0
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.ui.game_over.visible:
                mouse_pos = pygame.mouse.get_pos()
                if self.ui.hint_rect.collidepoint(mouse_pos):
                    self.show_hint = not self.show_hint
                    self.sound_manager.button_click_sound.play()
                for i, rect in enumerate(self.ui.ghost_rects):
                    if rect.collidepoint(mouse_pos):
                        shows = [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde]
                        shows[i] = not shows[i]
                        setattr(self.ui, f"show_{['blinky', 'pinky', 'inky', 'clyde'][i]}", shows[i])
                        self.sound_manager.button_click_sound.play()
                        break
                # Xử lý click cho solve button - DI CHUYỂN RA NGOÀI ĐỂ LUÔN CLICK ĐƯỢC, nhưng check lock
                if not self.solve_locked and self.ui.solve_rect.collidepoint(mouse_pos):
                    self.ui.solve_menu_visible = not self.ui.solve_menu_visible
                    if self.ui.solve_menu_visible:
                        self.ui.solve_option_rects = []
                        for i, option in enumerate(self.ui.solve_options):
                            opt_rect = pygame.Rect(self.ui.solve_rect.x, self.ui.solve_rect.y - (i + 1) * 30, 80, 25)
                            self.ui.solve_option_rects.append(opt_rect)
                    self.sound_manager.button_click_sound.play()
                # THÊM: Nếu menu mở và click ngoài menu hoặc ngoài options, đóng menu
                elif self.ui.solve_menu_visible and not any(rect.collidepoint(mouse_pos) for rect in
                                                            self.ui.solve_option_rects) and not self.ui.solve_rect.collidepoint(
                        mouse_pos):
                    self.ui.solve_menu_visible = False
                if self.ui.solve_menu_visible:
                    for i, rect in enumerate(self.ui.solve_option_rects):
                        if rect.collidepoint(mouse_pos):
                            selected_option = self.ui.solve_options[i]
                            self.ai_mode = True
                            self.manual_mode = False  # Tắt manual nếu chọn AI
                            self.player.clear_path()  # Clear current path when switching algorithm
                            if selected_option == "BFS":
                                self.path_finder = self.bfs_finder
                                self.ui.selected_solve = "BFS"
                            elif selected_option == "DFS":
                                self.path_finder = self.dfs_finder
                                self.ui.selected_solve = "DFS"
                            elif selected_option == "UCS":
                                self.path_finder = self.ucs_finder
                                self.ui.selected_solve = "UCS"
                            elif selected_option == "ASTAR":
                                self.path_finder = self.astar_finder
                                self.ui.selected_solve = "ASTAR"
                            elif selected_option == "GREEDY":
                                self.path_finder = self.greedy_finder
                                self.ui.selected_solve = "GREEDY"
                            elif selected_option == "BEAM":
                                self.path_finder = self.beam_finder
                                self.ui.selected_solve = "BEAM"
                            elif selected_option == "HILL CLIMBING":
                                self.path_finder = self.hill_climbing_finder
                                self.ui.selected_solve = "HILL CLIMBING"
                            self.ui.solve_menu_visible = False
                            self.solve_locked = True  # Lock sau khi chọn
                            self.sound_manager.button_click_sound.play()
                            break
        return True

    def fade_in(self):
        fade_surface = pygame.Surface((self.width, self.height)).convert_alpha()
        fade_surface.fill((0, 0, 0))
        for alpha in range(255, -1, -5):  # Giảm dần alpha từ 255 xuống 0
            fade_surface.set_alpha(alpha)
            self.screen.fill('black')
            # THÊM VẼ HÌNH NỀN TRONG FADE IN
            if self.background:
                self.screen.blit(self.background, (0, self.y_offset))
            self.ui.draw_header()
            self.level.draw_board()
            if self.show_hint and not self.dying and not self.just_reset:
                self.player.draw_path()
                for ghost in self.ghosts:
                    ghost.draw_path()
            self.player.draw()
            for i, ghost in enumerate(self.ghosts):
                if [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                    ghost.draw()
            self.ui.draw_ready()
            self.ui.draw_lives()
            self.ui.draw_hint_button()
            self.ui.draw_ghost_toggle_buttons()
            self.ui.draw_solve_button()  # Thêm vẽ nút solve
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.timer.tick(60)

    def draw_game_screen(self):
        """Phương thức helper để vẽ màn hình game"""
        self.screen.fill('black')
        if self.background:
            self.screen.blit(self.background, (0, self.y_offset))
        self.ui.draw_header()
        self.level.draw_board()
        if self.show_hint and not self.dying and not self.just_reset:
            self.player.draw_path()
            for ghost in self.ghosts:
                ghost.draw_path()
        self.player.draw()
        for i, ghost in enumerate(self.ghosts):
            if [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                ghost.draw()
        self.ui.draw_ready()
        self.ui.draw_lives()
        self.ui.draw_hint_button()
        self.ui.draw_ghost_toggle_buttons()
        self.ui.draw_solve_button()  # Thêm vẽ nút solve

        # VẼ PAUSE MENU NẾU ĐANG HIỂN THỊ - THÊM DÒNG NÀY
        self.pause_menu.draw(self.screen)

        pygame.display.flip()

    def run(self):
        self.running = True

        # Fade in khi bắt đầu game
        self.fade_in()

        # THÊM: Biến để theo dõi số countdown trước đó
        self.last_count = 0

        while self.running:
            if self.return_code == 'menu':
                # THÊM: Clear AI path khi quay về menu
                self.player.clear_path()
                break
            dt = self.timer.tick(self.fps)
            delta_time = dt / 1000.0

            if self.pause_menu.visible:
                # Chỉ xử lý sự kiện và vẽ, không cập nhật game
                self.handle_events()
                mouse_pos = pygame.mouse.get_pos()
                self.pause_menu.update_hover(mouse_pos)
                self.ui.update_hover(mouse_pos)
                self.draw_game_screen()
                continue

            if self.countdown_active:
                self.countdown_timer -= delta_time
                count = int(self.countdown_timer + 1)  # Hiển thị 3,2,1

                # THÊM: Chỉ phát âm thanh khi số thay đổi
                if count != self.last_count and count > 0:
                    self.sound_manager.play_count_down()
                    self.last_count = count

                # Tính toán hiệu ứng
                progress = 1.0 - (self.countdown_timer % 1.0)  # 0.0 -> 1.0 trong mỗi giây
                scale = 1.0 + progress * 0.3  # Giảm độ phóng to
                alpha = int(255 * (1 - progress * 0.8))  # Giữ độ trong suốt tốt hơn

                self.screen.fill('black')
                if self.background:
                    self.screen.blit(self.background, (0, self.y_offset))
                self.level.draw_board()
                self.player.draw()
                for i, ghost in enumerate(self.ghosts):
                    if [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                        ghost.draw()
                self.ui.draw_header()
                self.ui.draw_lives()

                if count > 0:
                    # Tạo font với kích thước động
                    dynamic_font_size = int(120 * scale)  # Tăng kích thước base
                    countdown_font = pygame.font.SysFont('Arial', dynamic_font_size, bold=True)

                    # Màu gradient đẹp hơn - xanh cyan với hiệu ứng neon
                    base_color = (0, 255, 255)  # Cyan
                    dark_color = (0, 150, 200)  # Cyan đậm
                    bright_color = (100, 255, 255)  # Cyan sáng

                    # Tạo text với gradient effect
                    text_surface = pygame.Surface((dynamic_font_size * 2, dynamic_font_size * 2), pygame.SRCALPHA)

                    # Vẽ hiệu ứng glow bên ngoài
                    glow_radius = int(20 * scale)
                    for r in range(glow_radius, 0, -2):
                        glow_alpha = int(50 * (r / glow_radius) * (alpha / 255))
                        glow_color = (*bright_color[:3], glow_alpha)
                        pygame.draw.circle(text_surface, glow_color,
                                           (dynamic_font_size, dynamic_font_size),
                                           dynamic_font_size + r)

                    # Vẽ shadow
                    shadow_text = countdown_font.render(str(count), True, (0, 50, 100))
                    shadow_rect = shadow_text.get_rect(center=(dynamic_font_size + 4, dynamic_font_size + 4))
                    shadow_text.set_alpha(alpha // 2)
                    text_surface.blit(shadow_text, shadow_rect)

                    # Vẽ text chính với gradient
                    main_text = countdown_font.render(str(count), True, base_color)
                    main_rect = main_text.get_rect(center=(dynamic_font_size, dynamic_font_size))
                    main_text.set_alpha(alpha)
                    text_surface.blit(main_text, main_rect)

                    # Vẽ highlight
                    highlight_text = countdown_font.render(str(count), True, bright_color)
                    highlight_rect = highlight_text.get_rect(center=(dynamic_font_size - 2, dynamic_font_size - 2))
                    highlight_text.set_alpha(min(alpha, 200))
                    text_surface.blit(highlight_text, highlight_rect)

                    # Đặt text surface vào màn hình
                    final_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
                    self.screen.blit(text_surface, final_rect)

                pygame.display.flip()

                if self.countdown_timer <= 0:
                    self.countdown_active = False
                    self.last_count = 0  # Reset biến đếm
                    if self.game_started and not self.dying:
                        self.sound_manager.play_ghost_move()
                    # CHỈ UNPAUSE INTRO KHI COUNTDOWN KẾT THÚC
                    # Và chỉ unpause nếu intro đang được pause (tức là đang ở trạng thái pause)
                    if self.sound_manager.intro_channel.get_busy():
                        self.sound_manager.unpause_intro()
                    self.sound_manager.unpause_turn_egg()
                self.handle_events()
                continue

            # Xử lý game over screen
            if self.ui.game_over.visible:
                self.ui.game_over.update(pygame.mouse.get_pos())

                # Xử lý sự kiện
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    else:
                        self.ui.game_over.handle_event(event)

                # Vẽ game
                self.screen.fill('black')
                # THÊM VẼ HÌNH NỀN TRONG GAME OVER
                if self.background:
                    self.screen.blit(self.background, (0, self.y_offset))
                self.level.draw_board()
                self.player.draw()
                for i, ghost in enumerate(self.ghosts):
                    if [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                        ghost.draw()
                self.ui.draw_header()
                self.ui.draw_lives()

                # Vẽ game over screen
                self.ui.game_over.draw()

                pygame.display.flip()
                continue

                # THÊM: Xử lý level complete animation
            if self.level_anim.active:
                self.level_anim.update(dt)
                self.handle_events()
                self.screen.fill('black')
                if self.background:
                    self.screen.blit(self.background, (0, self.y_offset))
                self.ui.draw_header()
                self.level.draw_board()
                if self.show_hint and not self.dying and not self.just_reset:
                    self.player.draw_path()
                    for ghost in self.ghosts:
                        ghost.draw_path()
                    self.player.draw()
                for i, ghost in enumerate(self.ghosts):
                    if [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                        ghost.draw()
                self.ui.draw_ready()
                self.ui.draw_lives()
                self.ui.draw_hint_button()
                self.ui.draw_ghost_toggle_buttons()
                self.ui.draw_solve_button()
                # Vẽ animation
                self.level_anim.draw()
                pygame.display.flip()
                continue
                # THÊM: Xử lý level complete menu
            if self.show_level_complete:
                mouse_pos = pygame.mouse.get_pos()
                self.level_menu.update_hover(mouse_pos)
                # Xử lý sự kiện
                if not self.handle_level_complete_events():
                    continue
                    # Vẽ màn hình game cơ bản
                self.screen.fill('black')
                if self.background:
                    self.screen.blit(self.background, (0, self.y_offset))
                self.level.draw_board()
                self.player.draw()
                for i, ghost in enumerate(self.ghosts):
                    if [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                        ghost.draw()
                self.ui.draw_header()
                self.ui.draw_lives()
                # Vẽ level complete menu
                self.level_menu.draw(self.screen)
                pygame.display.flip()
                continue
            # Xử lý trạng thái just_reset
            if self.just_reset:
                self.reset_timer += dt
                if self.reset_timer >= self.reset_delay:
                    self.just_reset = False
                    if not self.hint_restored and self.saved_hint_state:
                        self.show_hint = True
                        self.hint_restored = True
            if self.dying:
                self.death_animation_time += dt
                self.fade_alpha = min(255, int(255 * (self.death_animation_time / self.death_animation_duration)))

                # Cập nhật eat animation cho các ghost đang eating (nếu có)
                for ghost in self.ghosts:
                    if ghost.eating:
                        ghost.eat_animation_time += dt

                # Kết thúc hiệu ứng chết
                if self.death_animation_time >= self.death_animation_duration:
                    self.dying = False
                    self.fade_alpha = 0
                    self.lives -= 1

                    if self.lives <= 0:
                        self.game_over = True
                        self.ui.game_over.show()
                        self.sound_manager.play_game_over()  # Phát âm thanh game over
                        print("GAME OVER")
                        self.solve_locked = False  # Unlock solve khi game over
                        # THÊM: Ghi history khi game over với success=False
                        self.record_game_history(success=False)
                    else:
                        self.reset_after_death()

                # Bỏ qua các cập nhật khác khi đang chết
                self.handle_events()
                self.screen.fill('black')
                # THÊM VẼ HÌNH NỀN KHI ĐANG CHẾT
                if self.background:
                    self.screen.blit(self.background, (0, self.y_offset))
                self.level.draw_board()
                self.player.draw()
                for i, ghost in enumerate(self.ghosts):
                    if [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                        ghost.draw()
                self.ui.draw_header()
                self.ui.draw_ready()
                self.ui.draw_lives()
                self.ui.draw_hint_button()
                self.ui.draw_ghost_toggle_buttons()
                self.ui.draw_solve_button()  # Thêm vẽ nút solve

                # Vẽ hiệu ứng fade
                if self.fade_alpha > 0:
                    fade_surface = pygame.Surface((self.width, self.height))
                    fade_surface.fill((0, 0, 0))
                    fade_surface.set_alpha(self.fade_alpha)
                    self.screen.blit(fade_surface, (0, 0))

                pygame.display.flip()
                continue
            # Handle intro and ready
            if self.show_ready:
                if not self.intro_played:
                    self.sound_manager.play_intro()
                    self.intro_played = True
                self.ready_timer -= dt
                if self.ready_timer <= 0:
                    self.show_ready = False
                    self.game_started = True
                    self.sound_manager.play_ghost_move()

            if self.game_started:
                self.play_time += dt
            # Update modes
            if self.game_started and not self.mode_manager.frightened_active:
                self.mode_manager.phase_timer += delta_time
                phase_duration = self.mode_manager.mode_phases[self.mode_manager.current_phase][1]
                if self.mode_manager.phase_timer >= phase_duration:
                    self.mode_manager.phase_timer = 0.0
                    self.mode_manager.current_phase += 1
                    if self.mode_manager.current_phase >= len(self.mode_manager.mode_phases):
                        self.mode_manager.current_phase = len(self.mode_manager.mode_phases) - 1
            if self.mode_manager.frightened_active:
                self.mode_manager.frightened_timer -= delta_time
                if self.mode_manager.frightened_timer <= 0:
                    self.mode_manager.frightened_active = False
                    self.sound_manager.stop_power()
                    self.eaten_ghosts_count = 0  # Reset đếm ghost ăn khi hết frightened

            self.handle_events()
            mouse_pos = pygame.mouse.get_pos()
            self.ui.update_hover(mouse_pos)
            self.pause_menu.update_hover(mouse_pos)

            if not self.dying:
                # THÊM: Chỉ update nếu ai_mode hoặc manual_mode (chơi thủ công đã kích hoạt)
                if self.game_started and (self.ai_mode or self.manual_mode):
                    self.player.update(dt)
                    for i, ghost in enumerate(self.ghosts):
                        if [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                            ghost.update(dt)
                    self.check_ghost_collisions()
                    # THÊM: Kiểm tra hết pellets để bắt đầu level complete
                    if self.level.remaining_pellets <= 0 and not self.dying and not self.game_over:
                        self.level_anim.start()
                        self.record_game_history(success=True)
                        continue

            if self.score > self.high_score:
                self.high_score = self.score

            self.screen.fill('black')
            # THÊM VẼ HÌNH NỀN CHÍNH - QUAN TRỌNG NHẤT
            if self.background:
                self.screen.blit(self.background, (0, self.y_offset))
            self.ui.draw_header()
            self.level.draw_board()

            # CHỈ vẽ path khi:
            # - show_hint được bật
            # - KHÔNG đang trong death sequence
            # - KHÔNG vừa reset xong
            if self.show_hint and not self.dying and not self.just_reset:
                for i, ghost in enumerate(self.ghosts):
                    if [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                        ghost.draw_path()
                if self.ai_mode:
                    self.player.draw_path()
            self.player.draw()
            for i, ghost in enumerate(self.ghosts):
                if [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                    ghost.draw()
            self.ui.draw_ready()
            self.ui.draw_lives()
            self.ui.draw_hint_button()
            self.ui.draw_ghost_toggle_buttons()
            self.ui.draw_solve_button()  # Thêm vẽ nút solve

            # Cập nhật và vẽ floating scores
            for i in range(len(self.floating_scores) - 1, -1, -1):
                points, x, y, timer = self.floating_scores[i]
                timer -= dt
                if timer <= 0:
                    del self.floating_scores[i]
                    continue
                self.floating_scores[i] = (points, x, y, timer)
                if points in self.score_images and self.score_images[points]:
                    img = self.score_images[points]
                    px = x - img.get_width() / 2
                    py = y - img.get_height() / 2
                    self.screen.blit(img, (px, py))

            pygame.display.flip()
        return self.return_code

    def check_collision(self, player, ghost):
        """Kiểm tra va chạm giữa pacman và ghost với khoảng cách chính xác hơn"""
        # Tính toán hitbox chính xác hơn
        player_center_x = player.x
        player_center_y = player.y + self.y_offset  # Cộng thêm y_offset để đúng vị trí thực tế

        ghost_center_x = ghost.x
        ghost_center_y = ghost.y + self.y_offset  # Cộng thêm y_offset để đúng vị trí thực tế

        # Tính khoảng cách giữa hai tâm
        distance = ((player_center_x - ghost_center_x) ** 2 + (player_center_y - ghost_center_y) ** 2) ** 0.5

        # Sử dụng bán kính va chạm nhỏ hơn để cảm giác chạm thực tế hơn
        collision_radius = min(player.pac_w, player.pac_h, ghost.ghost_w, ghost.ghost_h) * 0.3

        return distance < collision_radius

    def check_ghost_collisions(self):
        """Kiểm tra va chạm với ghost và xử lý khi ăn ghost"""
        for i, ghost in enumerate(self.ghosts):
            if not [self.ui.show_blinky, self.ui.show_pinky, self.ui.show_inky, self.ui.show_clyde][i]:
                continue
            # Bỏ qua nếu ghost đang bị ăn, đang ăn, hoặc đang về nhà
            if ghost.eaten or ghost.eating or ghost.returning_home:
                continue

            # Kiểm tra va chạm với Pacman
            if self.check_collision(self.player, ghost):
                if self.mode_manager.frightened_active:
                    # Pacman ăn ghost trong chế độ frightened
                    self.sound_manager.play_magic()  # Phát âm thanh magic
                    ghost.start_eaten_animation()  # Bắt đầu animation bị ăn
                    self.eaten_ghosts_count += 1  # Tăng số ghost ăn trong frightened hiện tại
                    # Cộng điểm theo thứ tự: 200, 400, 800, 1600 (giả sử 600 là lỗi gõ, dùng chuẩn Pacman 800)
                    points = 200 * (2 ** (self.eaten_ghosts_count - 1))
                    self.score += points  # Cộng điểm theo thứ tự

                    # Thêm floating score tại vị trí ghost
                    display_x = ghost.x
                    display_y = ghost.y + self.y_offset
                    self.floating_scores.append((points, display_x, display_y, 1000))  # Hiển thị 1 giây
                elif not self.dying:
                    # Ghost ăn Pacman
                    ghost.start_eating()  # Bắt đầu animation ăn pacman
                    self.start_death_sequence()  # Bắt đầu chuỗi chết

    def start_death_sequence(self):
        """Bắt đầu chuỗi hiệu ứng khi pacman bị ăn"""
        # Lưu trạng thái hint hiện tại và tắt hint
        self.saved_hint_state = self.show_hint
        self.show_hint = False
        self.hint_restored = False

        # XÓA PATH CỦA GHOST để tránh vẽ đường đến vị trí cũ
        for ghost in self.ghosts:
            ghost.path = []

        self.dying = True
        self.death_animation_time = 0
        self.fade_alpha = 0

        # Dừng các âm thanh khác
        self.sound_manager.stop_ghost()
        self.sound_manager.stop_power()

        # Phát âm thanh ghost eat
        self.sound_manager.play_death()

        # Kích hoạt trạng thái chết cho pacman
        self.player.die()

        # Dừng thời gian và cập nhật điểm
        self.game_started = False

    def reset_after_death(self):
        """Reset game sau khi mất mạng"""
        # Reset trạng thái miễn nhiễm của ghost
        for ghost in self.ghosts:
            ghost.frightened_disabled = False  # Sử dụng đúng tên thuộc tính
            # Reset vị trí
            ghost.row = ghost.start_row
            ghost.col = ghost.start_col
            ghost.x = ghost.col * self.num2_c + self.num2_c / 2.0
            ghost.y = ghost.row * self.num1_r + self.num1_r / 2.0
            ghost.direction = 0
            # Reset trạng thái eating
            ghost.eating = False
            ghost.eat_animation_time = 0
            # Xóa path
            ghost.path = []
            ghost.just_eaten = False
            ghost.returning_home = False
            ghost.reached_home = False
            # Reset release timer cho delay
            ghost.release_timer = ghost.release_delay
            self.player.clear_path()

        # Reset pacman
        self.player.row = 24
        self.player.col = 15
        self.player.x = self.player.col * self.num2_c + self.num2_c / 2.0
        self.player.y = self.player.row * self.num1_r + self.num1_r / 2.0
        self.player.direction = 0
        self.player.requested_direction = -1
        self.player.dead = False

        # THÊM: Clear AI path khi chết
        self.player.ai_path = []

        # Đặt trạng thái just_reset để tiếp tục ẩn hint
        self.just_reset = True
        self.reset_timer = 0
        # Reset trạng thái game
        self.show_ready = True
        self.ready_timer = 2000  # 2 giây hiển thị READY!
        self.game_started = False
        self.mode_manager.frightened_active = False
        self.eaten_ghosts_count = 0  # Reset đếm ghost ăn khi reset sau death
        self.sound_manager.stop_power()

        # Clear floating scores
        self.floating_scores = []

        # Đảm bảo ghost channel được bật lại
        if not self.game_over:
            self.sound_manager.play_ghost_move()

    def reset_for_next_level(self):
        """Reset game cho level tiếp theo sau khi hoàn thành level"""
        # Tăng level num đã làm trong start()
        # Reset pellets
        self.level.remaining_pellets = sum(1 for row in boards for cell in row if cell in [2, 3])
        self.level.initial_pellets = self.level.remaining_pellets
        self.level.load_board(boards)  # Giả sử có method load_board để reset board
        # Reset positions
        self.player.row = 24
        self.player.col = 15
        self.player.x = self.player.col * self.num2_c + self.num2_c / 2.0
        self.player.y = self.player.row * self.num1_r + self.num1_r / 2.0
        self.player.direction = 0
        self.player.requested_direction = -1
        self.player.visible = True
        self.player.clear_path()
        # Reset ghosts
        for ghost in self.ghosts:
            ghost.row = ghost.start_row
            ghost.col = ghost.start_col
            ghost.x = ghost.col * self.num2_c + self.num2_c / 2.0
            ghost.y = ghost.row * self.num1_r + self.num1_r / 2.0
            ghost.direction = 0
            ghost.path = []
            ghost.eaten = False
            ghost.eating = False
            ghost.returning_home = False
            ghost.just_eaten = False
            ghost.reached_home = False
            ghost.release_timer = ghost.release_delay
            ghost.frightened_disabled = False
        # Reset modes
        self.player.reset()
        self.eaten_ghosts_count = 0
        self.floating_scores = []
        # Reset trạng thái game
        self.show_ready = True
        self.ready_timer = self.sound_manager.intro_sound.get_length() * 1000
        self.game_started = False
        self.intro_played = False
        self.play_time = 0.0
        self.countdown_active = False
        self.just_reset = False
        self.dying = False
        self.game_over = False

        # THÊM: Reset metrics cho level mới
        self.metrics = {
            'execution_time': 0.0,
            'expanded_nodes': 0,
            'path_lengths': [],
            'memory_usage': 0,
            'success': 0,
            'calls': 0
        }

        # Âm thanh
        self.sound_manager.stop_all_sounds()
        # Fade in lại
        self.fade_in()

    def return_to_main_menu(self):
        """Quay về main menu"""
        self.return_code = 'menu'
        self.running = False

    def handle_level_complete_events(self):
        """Xử lý sự kiện cho màn hình level complete"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            else:
                if self.level_menu.handle_events(event):
                    continue
        return True

    def record_game_history(self, success=True):
        """Record game metrics to history when level is completed or game over"""
        # Only record if AI mode was used
        if not self.ai_mode:
            return

        # Tính success_rate
        success_rate = 100 if success else 0

        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'algorithm': self.ui.selected_solve,
            'level': self.level_num,
            'execution_time': self.metrics['execution_time'],
            'expanded_nodes': self.metrics['expanded_nodes'],
            'path_length': len(self.metrics['path_lengths']) if self.metrics['path_lengths'] else 0,
            'memory_usage': self.metrics['memory_usage'],
            'success_rate': success_rate,
            'total_time': self.play_time / 1000.0,  # Convert to seconds
            'score': self.score
        }

        # Load existing history
        history_data = []
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history_data = json.load(f)
        except:
            pass

        # Add new entry
        history_data.append(history_entry)

        # Save history
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
