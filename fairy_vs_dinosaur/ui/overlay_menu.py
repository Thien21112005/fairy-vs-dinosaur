import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.i18n import get_translation


class OverlayMenu:
    """Menu nổi trên màn chơi (pause, level complete): nền mờ, thanh tiến độ, các nút và hộp thoại xác nhận."""

    WIDTH = 420
    HEIGHT = 400
    BUTTON_WIDTH = 220
    BUTTON_HEIGHT = 55
    BUTTON_MARGIN = 25
    TITLE_KEY = ""

    def __init__(self, game):
        self.game = game
        self.x = (game.width - self.WIDTH) // 2
        self.y = (game.height - self.HEIGHT) // 2

        self.title_font = pygame.font.SysFont('monospace', 50, bold=True)
        self.button_font = pygame.font.SysFont('monospace', 34, bold=True)
        self.small_font = pygame.font.SysFont('monospace', 20, bold=True)
        self.progress_font = pygame.font.SysFont('monospace', 16, bold=True)

        self.buttons = self._build_buttons()
        self.selected_index = 0
        self.hover_states = [False] * len(self.buttons)
        self.prev_hover_states = [False] * len(self.buttons)
        self.background_surface = None

        self.show_confirm = False
        self.confirm_selected = 0
        self.confirm_action = None
        self.confirm_hover = [False, False]
        self.prev_confirm_hover = [False, False]

        try:
            fairy_raw = pygame.image.load(asset("images/fairy/blue/tile003.png")).convert_alpha()
            self.fairy_icon = pygame.transform.smoothscale(fairy_raw, (30, 30))
        except (pygame.error, FileNotFoundError):
            print("Không thể load hình nàng tiên. Sử dụng hình tròn thay thế.")
            self.fairy_icon = None

    def _build_buttons(self):
        raise NotImplementedError

    def _buttons_start_y(self):
        raise NotImplementedError

    def _confirm_question(self):
        raise NotImplementedError

    def _execute_confirm_action(self):
        raise NotImplementedError

    def _draw_extra_info(self, screen):
        """Thông tin thêm giữa thanh tiến độ và các nút."""

    def _button_rect(self, index):
        return pygame.Rect(
            self.game.width // 2 - self.BUTTON_WIDTH // 2,
            self._buttons_start_y() + index * (self.BUTTON_HEIGHT + self.BUTTON_MARGIN),
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )

    def _confirm_button_rect(self, index):
        return pygame.Rect(self.game.width // 2 - 130 + index * 160, self.game.height // 2 + 20, 100, 40)

    # --- Vẽ ---

    def _draw_overlay(self, screen):
        self._draw_blur_background(screen)
        self._draw_menu_background(screen)
        self._draw_menu_title(screen)
        self._draw_progress_bar(screen)
        self._draw_extra_info(screen)
        for i, button in enumerate(self.buttons):
            self._draw_menu_button(screen, self._button_rect(i), button["text"], i)
        if self.show_confirm:
            self._draw_confirm_dialog(screen)

    def _draw_blur_background(self, screen):
        if self.background_surface is None:
            self.background_surface = screen.copy()
            darken = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
            for i in range(self.game.height):
                alpha = 150 + (i / self.game.height) * 50
                pygame.draw.line(darken, (0, 0, 0, int(alpha)), (0, i), (self.game.width, i))
            self.background_surface.blit(darken, (0, 0))

        screen.blit(self.background_surface, (0, 0))

    def _draw_menu_background(self, screen):
        gradient_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(gradient_surface, (40, 40, 80, 220), (0, 0, self.WIDTH, self.HEIGHT), border_radius=25)

        for i in range(self.HEIGHT):
            color = (30 + i // 10, 30 + i // 10, 60 + i // 5)
            pygame.draw.line(gradient_surface, color, (0, i), (self.WIDTH, i))

        screen.blit(gradient_surface, (self.x, self.y))

        menu_rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        pygame.draw.rect(screen, (100, 150, 220, 150), menu_rect.inflate(4, 4), width=5, border_radius=25)
        pygame.draw.rect(screen, (80, 140, 200), menu_rect, width=4, border_radius=25)

    def _draw_menu_title(self, screen):
        title = get_translation(self.TITLE_KEY)
        title_text = self.title_font.render(title, True, (255, 255, 100))
        shadow_text = self.title_font.render(title, True, (100, 100, 0))
        title_rect = title_text.get_rect(center=(self.game.width // 2, self.y + 40))
        shadow_rect = shadow_text.get_rect(center=(title_rect.centerx + 2, title_rect.centery + 2))

        screen.blit(shadow_text, shadow_rect)
        screen.blit(title_text, title_rect)

    def _draw_outlined_text(self, screen, text, color, pos):
        """Vẽ chữ có viền đen để dễ đọc trên nền bất kỳ."""
        border = self.progress_font.render(text, True, (0, 0, 0))
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    screen.blit(border, (pos[0] + dx, pos[1] + dy))
        screen.blit(self.progress_font.render(text, True, color), pos)

    def _draw_progress_bar(self, screen):
        total_pellets = self.game.level.initial_pellets
        if total_pellets > 0:
            collected_pellets = total_pellets - self.game.level.remaining_pellets
            percent_complete = collected_pellets / total_pellets
        else:
            total_pellets = 1
            collected_pellets = 0
            percent_complete = 0

        bar_width = 340
        bar_height = 25
        bar_x = self.x + (self.WIDTH - bar_width) // 2
        bar_y = self.y + 100

        pygame.draw.rect(screen, (30, 30, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=12)
        if percent_complete > 0:
            self._draw_progress_fill(screen, bar_x, bar_y, max(12, int(bar_width * percent_complete)), bar_height)
        pygame.draw.rect(screen, (147, 112, 219), (bar_x, bar_y, bar_width, bar_height), width=2, border_radius=12)

        self._draw_progress_fairy(screen, bar_x + int(bar_width * percent_complete) - 15, bar_y - 10)

        percent_text = f"{percent_complete * 100:.1f}%"
        text_w, text_h = self.progress_font.size(percent_text)
        text_y = bar_y + (bar_height - text_h) // 2
        self._draw_outlined_text(screen, percent_text, (255, 255, 255), (bar_x + bar_width - text_w - 5, text_y))
        self._draw_outlined_text(screen, f"{collected_pellets}/{total_pellets}", (144, 238, 144), (bar_x + 5, text_y))
        self._draw_outlined_text(screen, "PROGRESS", (255, 165, 0), (bar_x, bar_y - 25))

    def _draw_progress_fill(self, screen, x, y, width, height):
        """Phần đã hoàn thành: gradient từ tím sang hồng, bo góc."""
        fill = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(width):
            ratio = i / width
            color = (
                int(138 + (255 - 138) * ratio),
                int(43 + (105 - 43) * ratio),
                int(226 + (180 - 226) * ratio)
            )
            pygame.draw.rect(fill, color, (i, 0, 1, height))

        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, width, height), border_radius=12)
        fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(fill, (x, y))

    def _draw_progress_fairy(self, screen, x, y):
        glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        for r in range(8, 0, -2):
            pygame.draw.circle(glow_surface, (255, 105, 180, 30 - r * 3), (20, 20), 15 + r)
        screen.blit(glow_surface, (x - 5, y - 5))

        if self.fairy_icon:
            screen.blit(self.fairy_icon, (x, y))
        else:
            pygame.draw.circle(screen, (255, 255, 0), (x + 15, y + 15), 12)

    def _draw_menu_button(self, screen, rect, text, index):
        is_highlighted = self.hover_states[index] or index == self.selected_index
        colors = self._get_button_colors(is_highlighted)

        if is_highlighted:
            glow_rect = rect.inflate(12, 12)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 200, 100, 80), (0, 0, glow_rect.width, glow_rect.height),
                             border_radius=15)
            screen.blit(glow_surface, glow_rect.topleft)

        button_surface = pygame.Surface((self.BUTTON_WIDTH, self.BUTTON_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, colors['bg'], (0, 0, self.BUTTON_WIDTH, self.BUTTON_HEIGHT), border_radius=12)
        pygame.draw.rect(button_surface, colors['bg_dark'],
                         (0, self.BUTTON_HEIGHT // 2, self.BUTTON_WIDTH, self.BUTTON_HEIGHT // 2), border_radius=12)
        screen.blit(button_surface, rect.topleft)

        pygame.draw.rect(screen, colors['border'], rect, width=3, border_radius=12)

        text_surface = self.button_font.render(text, True, colors['text'])
        shadow_surface = self.button_font.render(text, True, colors['shadow'])
        shadow_surface.set_alpha(colors['shadow_alpha'])

        text_rect = text_surface.get_rect(center=rect.center)
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))

        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

    @staticmethod
    def _get_button_colors(is_highlighted):
        if is_highlighted:
            return {
                'bg': (240, 180, 60),
                'bg_dark': (210, 150, 30),
                'border': (255, 230, 120),
                'text': (20, 20, 20),
                'shadow': (0, 0, 0),
                'shadow_alpha': 100
            }
        return {
            'bg': (60, 120, 200),
            'bg_dark': (30, 90, 170),
            'border': (100, 160, 240),
            'text': (240, 240, 240),
            'shadow': (255, 255, 255),
            'shadow_alpha': 50
        }

    def _draw_confirm_dialog(self, screen):
        dialog_bg = pygame.Rect(self.game.width // 4, self.game.height // 2 - 80, self.game.width // 2, 160)

        for y in range(dialog_bg.height):
            ratio = y / dialog_bg.height
            color = (
                int(40 + (80 - 40) * ratio),
                int(40 + (80 - 40) * ratio),
                int(80 + (120 - 80) * ratio)
            )
            pygame.draw.line(screen, color, (dialog_bg.x, dialog_bg.y + y), (dialog_bg.right, dialog_bg.y + y))

        pygame.draw.rect(screen, (150, 150, 255), dialog_bg.inflate(4, 4), width=3, border_radius=20)
        pygame.draw.rect(screen, (100, 100, 200), dialog_bg, width=3, border_radius=15)

        y = dialog_bg.y + 20
        for line in self._wrap_text(self._confirm_question(), self.small_font, dialog_bg.width - 40):
            text_surface = self.small_font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, text_surface.get_rect(centerx=self.game.width // 2, top=y))
            y += text_surface.get_height() + 5

        for i, option in enumerate([get_translation("yes"), get_translation("no")]):
            button_rect = self._confirm_button_rect(i)
            is_yes = i == 0
            is_highlighted = self.confirm_hover[i] or i == self.confirm_selected
            colors = self._get_confirm_button_colors(is_highlighted, is_yes)

            if is_highlighted:
                glow_color = (150, 255, 150) if is_yes else (255, 150, 150)
                pygame.draw.rect(screen, glow_color, button_rect.inflate(6, 6), border_radius=10)

            pygame.draw.rect(screen, colors['bg'], button_rect, border_radius=8)
            pygame.draw.rect(screen, colors['border'], button_rect, width=2, border_radius=8)

            text_surface = self.button_font.render(option, True, colors['text'])
            screen.blit(text_surface, text_surface.get_rect(center=button_rect.center))

    @staticmethod
    def _wrap_text(text, font, max_width):
        lines = []
        current_line = []
        for word in text.split(' '):
            if font.size(' '.join(current_line + [word]))[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    @staticmethod
    def _get_confirm_button_colors(is_highlighted, is_yes):
        if is_yes:
            if is_highlighted:
                return {'bg': (0, 200, 0), 'border': (100, 255, 100), 'text': (0, 0, 0)}
            return {'bg': (0, 150, 0), 'border': (50, 200, 50), 'text': (255, 255, 255)}
        if is_highlighted:
            return {'bg': (200, 0, 0), 'border': (255, 100, 100), 'text': (0, 0, 0)}
        return {'bg': (150, 0, 0), 'border': (200, 50, 50), 'text': (255, 255, 255)}

    # --- Hover ---

    def _update_overlay_hover(self, mouse_pos):
        if self.show_confirm:
            self._update_confirm_hover(mouse_pos)
        else:
            self._update_menu_hover(mouse_pos)

    def _update_menu_hover(self, mouse_pos):
        for i in range(len(self.buttons)):
            current_hover = self._button_rect(i).collidepoint(mouse_pos)
            if current_hover and not self.prev_hover_states[i]:
                self.game.sound_manager.button_hover_sound.play()
            self.hover_states[i] = current_hover
            self.prev_hover_states[i] = current_hover
            if current_hover:
                self.selected_index = i

    def _update_confirm_hover(self, mouse_pos):
        new_hover = [self._confirm_button_rect(i).collidepoint(mouse_pos) for i in range(2)]
        for i in range(2):
            if new_hover[i] and not self.prev_confirm_hover[i]:
                self.game.sound_manager.button_hover_sound.play()
                self.confirm_selected = i
            self.prev_confirm_hover[i] = new_hover[i]
        self.confirm_hover = new_hover

    # --- Sự kiện ---

    def _handle_confirm_keydown(self, event):
        if event.key == pygame.K_LEFT:
            self.confirm_selected = 0
            self.game.sound_manager.button_hover_sound.play()
            return True
        if event.key == pygame.K_RIGHT:
            self.confirm_selected = 1
            self.game.sound_manager.button_hover_sound.play()
            return True
        if event.key == pygame.K_RETURN:
            return self._execute_confirm_action()
        return False

    def _handle_menu_keydown(self, event):
        if event.key in [pygame.K_UP, pygame.K_w]:
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
            self.game.sound_manager.button_hover_sound.play()
            return True
        if event.key in [pygame.K_DOWN, pygame.K_s]:
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            self.game.sound_manager.button_hover_sound.play()
            return True
        if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.game.sound_manager.button_click_sound.play()
            self.buttons[self.selected_index]["action"]()
            return True
        return False

    def _handle_overlay_click(self, mouse_pos):
        if self.show_confirm:
            if self._confirm_button_rect(0).collidepoint(mouse_pos):
                self.game.sound_manager.button_click_sound.play()
                return self._execute_confirm_action()
            if self._confirm_button_rect(1).collidepoint(mouse_pos):
                self.game.sound_manager.button_click_sound.play()
                self.show_confirm = False
                return True
            return False

        for i, button in enumerate(self.buttons):
            if self._button_rect(i).collidepoint(mouse_pos):
                self.game.sound_manager.button_click_sound.play()
                button["action"]()
                return True
        return False

    def _ask_confirm(self, action):
        self.show_confirm = True
        self.confirm_action = action
        self.confirm_selected = 0
