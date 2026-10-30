import pygame

ARROW_KEYS = {pygame.K_RIGHT: 0, pygame.K_LEFT: 1, pygame.K_UP: 2, pygame.K_DOWN: 3}
WASD_KEYS = {pygame.K_d: 0, pygame.K_a: 1, pygame.K_w: 2, pygame.K_s: 3}
CONTROL_SCHEMES = {
    "Arrow Keys": ARROW_KEYS,
    "WASD": WASD_KEYS,
    "Mixed": {**ARROW_KEYS, **WASD_KEYS},
}
MOVEMENT_KEYS = set(ARROW_KEYS) | set(WASD_KEYS)


class GameInputMixin:
    """Xử lý bàn phím và chuột trong lúc chơi."""

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            if self.pause_menu.handle_events(event):
                continue
            if event.type == pygame.KEYDOWN and not self.show_ready and not self.ui.game_over.visible:
                # AI đang điều khiển thì bỏ qua phím di chuyển
                if not self.ai_mode:
                    self._handle_movement_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.ui.game_over.visible:
                self._handle_hud_click(pygame.mouse.get_pos())
        return True

    def _handle_movement_key(self, key):
        scheme = CONTROL_SCHEMES.get(self.control_scheme, {})
        if key in scheme:
            self.player.requested_direction = scheme[key]

        # Nhấn phím di chuyển nghĩa là chơi thủ công: khóa nút giải
        if key in MOVEMENT_KEYS:
            self.manual_mode = True
            self.ai_mode = False
            self.solve_locked = True
            self.ui.solve_menu_visible = False

        if key == pygame.K_SPACE:
            self.player.col = 15 if self.player.col == 14 else 14
            self.player.row = 24
            self.player.x = self.player.col * self.num2_c + self.num2_c / 2.0
            self.player.y = self.player.row * self.num1_r + self.num1_r / 2.0

    def _handle_hud_click(self, mouse_pos):
        ui = self.ui
        if ui.hint_rect.collidepoint(mouse_pos):
            self.show_hint = not self.show_hint
            self.sound_manager.button_click_sound.play()

        for i, rect in enumerate(ui.ghost_rects):
            if rect.collidepoint(mouse_pos):
                name = f"show_{['blinky', 'pinky', 'inky', 'clyde'][i]}"
                setattr(ui, name, not getattr(ui, name))
                self.sound_manager.button_click_sound.play()
                break

        if not self.solve_locked and ui.solve_rect.collidepoint(mouse_pos):
            ui.solve_menu_visible = not ui.solve_menu_visible
            if ui.solve_menu_visible:
                ui.solve_option_rects = [pygame.Rect(ui.solve_rect.x, ui.solve_rect.y - (i + 1) * 30, 80, 25)
                                         for i in range(len(ui.solve_options))]
            self.sound_manager.button_click_sound.play()
        elif ui.solve_menu_visible and not ui.solve_rect.collidepoint(mouse_pos) and not any(
                rect.collidepoint(mouse_pos) for rect in ui.solve_option_rects):
            ui.solve_menu_visible = False

        if ui.solve_menu_visible:
            self._handle_solve_option_click(mouse_pos)

    def _handle_solve_option_click(self, mouse_pos):
        ui = self.ui
        for i, rect in enumerate(ui.solve_option_rects):
            if rect.collidepoint(mouse_pos):
                option = ui.solve_options[i]
                self.ai_mode = True
                self.manual_mode = False
                self.player.clear_path()
                self.path_finder = self.path_finders[option]
                ui.selected_solve = option
                ui.solve_menu_visible = False
                self.solve_locked = True
                self.sound_manager.button_click_sound.play()
                break
