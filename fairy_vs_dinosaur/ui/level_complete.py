import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui.overlay_menu import OverlayMenu


class LevelCompleteAnimation:
    """Chuỗi hiệu ứng khi ăn hết pellet: gõ chiêng, cầu lửa lớn dần rồi ném về phía nhà ma."""

    def __init__(self, game):
        self.game = game
        self.active = False

        try:
            self.gong_img = pygame.image.load(asset("images/level_complete/gong.png")).convert_alpha()
            self.throw_img = pygame.image.load(asset("images/level_complete/throw.png")).convert_alpha()
            self.fireball_imgs = [
                pygame.image.load(asset("images/level_complete/fireball1.png")).convert_alpha(),
                pygame.image.load(asset("images/level_complete/fireball2.png")).convert_alpha()
            ]
        except pygame.error as e:
            print(f"Không thể load animation images: {e}")
            self.gong_img = self.throw_img = pygame.Surface((self.game.pac_w, self.game.pac_h))
            self.fireball_imgs = [pygame.Surface((20, 20)), pygame.Surface((20, 20))]

        # Các trạng thái: none, gong, blink_fireball, grow_fireball, hold_fireball, throw, fly_fireball, done
        self.state = 'none'
        self.timer = 0
        self.fireball_x = 0
        self.fireball_y = 0
        self.fireball_scale = 1
        self.fireball_frame = 0
        self.fireball_speed = 200  # Pixel/giây bay
        self.fireball_vx = 0
        self.fireball_vy = 0
        self.fireball_initial_dist = 0
        self.fireball_target_x = 15 * self.game.num2_c + self.game.num2_c / 2.0
        self.fireball_target_y = 15 * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset
        self.gong_duration = 2000  # ms
        self.blink_duration = 200  # ms mỗi pha bật/tắt
        self.blink_phase = 0
        self.blink_visible = True
        self.grow_duration = 1000  # ms
        self.hold_duration = 900  # ms
        self.throw_duration = 500  # ms
        self.direction = 'right'

    def start(self):
        self.active = True
        self.state = 'gong'
        self.timer = 0
        self.game.game_started = False
        self.game.sound_manager.stop_all_sounds()

        self.direction = 'left' if self.game.player.x > self.fireball_target_x else 'right'

        # Cầu lửa nằm ngay trên đầu nhân vật
        self.fireball_x = self.game.player.x
        self.fireball_y = self.game.player.y + self.game.y_offset - (self.game.pac_h / 2 + 70)
        self.fireball_scale = 0.5

        dx = self.fireball_target_x - self.fireball_x
        dy = self.fireball_target_y - self.fireball_y
        self.fireball_initial_dist = (dx ** 2 + dy ** 2) ** 0.5

        self.game.sound_manager.stop_ghost()
        self.game.sound_manager.stop_power()

        self.game.level_num += 1

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt
        handler = getattr(self, f"_update_{self.state}", None)
        if handler:
            handler(dt)

        if self.state == 'done':
            self.game.level_menu.open()
            self.game.show_level_complete = True
            self.active = False
            self.state = 'none'

    def _update_gong(self, dt):
        if self.timer >= self.gong_duration:
            self.state = 'blink_fireball'
            self.timer = 0
            self.blink_phase = 0
            self.blink_visible = True
            self.game.sound_manager.play_flick()

    def _update_blink_fireball(self, dt):
        if self.timer >= self.blink_duration:
            self.blink_phase += 1
            self.timer = 0
            self.blink_visible = self.blink_phase % 2 == 0
            if self.blink_phase >= 4:  # Sau 2 lần chớp tắt
                self.state = 'grow_fireball'
                self.timer = 0
                self.game.sound_manager.stop_flick()
                self.game.sound_manager.play_hold()
        if self.blink_visible:
            self.fireball_frame = (self.fireball_frame + 1) % 2

    def _update_grow_fireball(self, dt):
        progress = min(1, self.timer / self.grow_duration)
        self.fireball_scale = 0.5 + 6.0 * progress
        self.fireball_frame = (self.fireball_frame + 1) % 2
        if self.timer >= self.grow_duration:
            self.state = 'hold_fireball'
            self.timer = 0

    def _update_hold_fireball(self, dt):
        self.fireball_scale = 6.0
        self.fireball_frame = (self.fireball_frame + 1) % 2
        if self.timer >= self.hold_duration:
            self.state = 'throw'
            self.timer = 0
            self.game.sound_manager.stop_hold()
            self.game.sound_manager.play_throw()

    def _update_throw(self, dt):
        if self.timer >= self.throw_duration:
            self.state = 'fly_fireball'
            self.timer = 0
            dx = self.fireball_target_x - self.fireball_x
            dy = self.fireball_target_y - self.fireball_y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            self.fireball_vx = dx / dist * self.fireball_speed if dist > 0 else 0
            self.fireball_vy = dy / dist * self.fireball_speed if dist > 0 else 0
            self.fireball_initial_dist = dist

    def _update_fly_fireball(self, dt):
        self.fireball_x += self.fireball_vx * (dt / 1000.0)
        self.fireball_y += self.fireball_vy * (dt / 1000.0)
        self.fireball_frame = (self.fireball_frame + 1) % 2

        dx_remaining = self.fireball_target_x - self.fireball_x
        dy_remaining = self.fireball_target_y - self.fireball_y
        remaining_dist = (dx_remaining ** 2 + dy_remaining ** 2) ** 0.5
        if self.fireball_initial_dist > 0:
            scale_ratio = remaining_dist / self.fireball_initial_dist
            self.fireball_scale = 5.0 * scale_ratio + 3 * (1 - scale_ratio)

        if remaining_dist < 20:
            self.state = 'done'
            self.game.sound_manager.stop_throw()

    def draw(self):
        if not self.active:
            return

        if self.state in ['gong', 'blink_fireball', 'grow_fireball', 'hold_fireball']:
            pac_img = self.gong_img
        elif self.state in ['throw', 'fly_fireball']:
            pac_img = self.throw_img
        else:
            return

        if self.direction == 'left':
            pac_img = pygame.transform.flip(pac_img, True, False)

        scaled_pac = pygame.transform.scale(pac_img, (int(self.game.pac_w), int(self.game.pac_h)))
        self.game.screen.blit(scaled_pac, (int(self.game.player.x - self.game.pac_w / 2),
                                           int(self.game.player.y + self.game.y_offset - self.game.pac_h / 2)))

        if self.state != 'gong' and (self.state != 'blink_fireball' or self.blink_visible):
            size = int(20 * self.fireball_scale)
            scaled_fb = pygame.transform.scale(self.fireball_imgs[self.fireball_frame], (size, size))
            self.game.screen.blit(scaled_fb, scaled_fb.get_rect(center=(int(self.fireball_x), int(self.fireball_y))))


class LevelCompleteMenu(OverlayMenu):
    TITLE_KEY = "level complete"

    def _build_buttons(self):
        return [
            {"text": get_translation("continue"), "action": self.continue_game},
            {"text": get_translation("main_menu"), "action": self.confirm_main_menu}
        ]

    def _buttons_start_y(self):
        total_buttons_height = len(self.buttons) * self.BUTTON_HEIGHT + (len(self.buttons) - 1) * self.BUTTON_MARGIN
        return (self.game.height - total_buttons_height) // 2 + 80

    def _confirm_question(self):
        return "Return to main menu? Progress will not be saved."

    def _execute_confirm_action(self):
        if self.confirm_selected == 0:
            self.game.return_code = 'menu'
            self.game.running = False
        else:
            self.show_confirm = False
        return True

    def _draw_extra_info(self, screen):
        y_pos = self.y + 160
        minutes = int(self.game.play_time // 60000)
        seconds = int((self.game.play_time // 1000) % 60)
        milliseconds = int(self.game.play_time % 1000)
        self._draw_info_line(screen, f"Score: {self.game.score}", y_pos)
        self._draw_info_line(screen, f"Time: {minutes:02d}:{seconds:02d}.{milliseconds:03d}", y_pos + 25)

    def _draw_info_line(self, screen, text, y):
        surface = self.small_font.render(text, True, (255, 255, 100))
        shadow = self.small_font.render(text, True, (100, 100, 0))
        rect = surface.get_rect(center=(self.game.width // 2, y))
        screen.blit(shadow, shadow.get_rect(center=(rect.centerx + 1, rect.centery + 1)))
        screen.blit(surface, rect)

    def open(self):
        """Chuẩn bị hiển thị: nền mờ phải chụp lại từ màn chơi hiện tại"""
        self.background_surface = None
        self.selected_index = 0
        self.show_confirm = False

    def draw(self, screen):
        if self.game.show_level_complete:
            self._draw_overlay(screen)

    def update_hover(self, mouse_pos):
        self._update_overlay_hover(mouse_pos)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.show_confirm:
                    self.show_confirm = False
                else:
                    self.continue_game()
                return True
            if self.show_confirm:
                return self._handle_confirm_keydown(event)
            return self._handle_menu_keydown(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_overlay_click(pygame.mouse.get_pos())
        return False

    def continue_game(self):
        self.game.show_level_complete = False
        self.game.reset_for_next_level()

    def confirm_main_menu(self):
        self._ask_confirm(2)
