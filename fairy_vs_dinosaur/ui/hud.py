import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui import theme
from fairy_vs_dinosaur.ui.game_over import GameOverScreen
from fairy_vs_dinosaur.ui.theme import fit_font, label_font, strong_font
from fairy_vs_dinosaur.ui.widgets import (BUTTON_STYLES, chamfered_slab, draw_slab_button, draw_text, outlined_text,
                                          scale_pixel_art)

SOLVE_OPTIONS = ["BFS", "DFS", "UCS", "ASTAR", "GREEDY", "HILL CLIMBING", "BEAM", "EXPECTIMAX", "MCTS"]
DINOSAURS = ["blinky", "pinky", "inky", "clyde"]

BAR_PADDING = 12
BUTTON_SIZE = 40
BUTTON_GAP = 6
GROUP_GAP = 12
LIFE_ICON_SIZE = 32
PORTRAIT_SIZE = 32
OPTION_HEIGHT = 30
DROPDOWN_PADDING = 7
STAT_LABEL_Y = 14
STAT_VALUE_Y = 33


class UI:
    def __init__(self, game):
        self.game = game
        lives_icon_raw = pygame.image.load(asset("images/fairy/blue/tile003.png")).convert_alpha()
        self.lives_icon = scale_pixel_art(lives_icon_raw, (LIFE_ICON_SIZE, LIFE_ICON_SIZE))
        self.hint_hover = False
        self.ghost_hover = [False] * 4  # Blinky, Pinky, Inky, Clyde
        self.show_blinky = True
        self.show_pinky = True
        self.show_inky = True
        self.show_clyde = True

        self.game_over = GameOverScreen(game)
        self.portraits, self.hidden_portraits = self._load_portraits()

        self.footer_y = game.y_offset + game.num1_r * game.row
        self.header_bar = self._build_bar(game.y_offset, hairline_y=game.y_offset - 1)
        self.footer_bar = self._build_bar(game.height - self.footer_y, hairline_y=0)

        button_y = self.footer_y + (game.height - self.footer_y - BUTTON_SIZE) // 2
        current_x = BAR_PADDING + 2 * LIFE_ICON_SIZE + GROUP_GAP + 8

        self.ghost_rects = []
        for _ in DINOSAURS:
            self.ghost_rects.append(pygame.Rect(current_x, button_y, BUTTON_SIZE, BUTTON_SIZE))
            current_x += BUTTON_SIZE + BUTTON_GAP
        current_x += GROUP_GAP - BUTTON_GAP

        self.hint_rect = pygame.Rect(current_x, button_y, 84, BUTTON_SIZE)
        current_x += self.hint_rect.width + BUTTON_GAP
        self.solve_rect = pygame.Rect(current_x, button_y, game.width - BAR_PADDING - current_x, BUTTON_SIZE)

        self.solve_hover = False
        self.solve_menu_visible = False
        self.solve_options = SOLVE_OPTIONS
        self.solve_option_hover = [False] * len(self.solve_options)
        self.dropdown_rect = self._dropdown_rect()
        self.solve_option_rects = [
            pygame.Rect(self.dropdown_rect.x + DROPDOWN_PADDING,
                        self.dropdown_rect.y + DROPDOWN_PADDING + i * OPTION_HEIGHT,
                        self.dropdown_rect.width - 2 * DROPDOWN_PADDING, OPTION_HEIGHT)
            for i in range(len(self.solve_options))
        ]
        self.selected_solve = None
        self._ready_text = {}

    @staticmethod
    def _load_portraits():
        """Sprite đã vẽ của từng khủng long làm mặt nút, bản xám khi đang ẩn con đó."""
        shown, hidden = [], []
        size = (PORTRAIT_SIZE, PORTRAIT_SIZE)
        for name in DINOSAURS:
            raw = pygame.image.load(asset(f"images/dinosaurs/{name}/normal/tile000.png")).convert_alpha()
            portrait = scale_pixel_art(raw, size)
            shown.append(portrait)
            faded = pygame.transform.grayscale(portrait)
            faded.fill((150, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
            hidden.append(faded)
        return shown, hidden

    def _build_bar(self, height, hairline_y):
        """Thanh đá trên và dưới bản đồ, ngăn với bản đồ bằng một đường đồng."""
        bar = pygame.Surface((self.game.width, height))
        for y in range(height):
            ratio = y / max(1, height - 1)
            color = [int(theme.PANEL_TOP[i] + (theme.PANEL_BOTTOM[i] - theme.PANEL_TOP[i]) * ratio) for i in range(3)]
            pygame.draw.line(bar, color, (0, y), (self.game.width, y))
        pygame.draw.line(bar, theme.COPPER, (0, hairline_y), (self.game.width, hairline_y))
        return bar

    def _dropdown_rect(self):
        height = len(SOLVE_OPTIONS) * OPTION_HEIGHT + 2 * DROPDOWN_PADDING
        return pygame.Rect(self.solve_rect.x, self.solve_rect.y - height - BUTTON_GAP, self.solve_rect.width, height)

    def visible_ghost_flags(self):
        return [self.show_blinky, self.show_pinky, self.show_inky, self.show_clyde]

    def _draw_stat(self, center_x, label, value):
        screen = self.game.screen
        max_width = self.game.width // 3 - 24
        draw_text(screen, label, fit_font(label_font, label, max_width, 15), theme.COPPER_LIGHT,
                  center=(center_x, STAT_LABEL_Y))
        draw_text(screen, value, strong_font(23), theme.PARCHMENT, center=(center_x, STAT_VALUE_Y))

    def draw_header(self):
        screen = self.game.screen
        screen.blit(self.header_bar, (0, 0))

        minutes = int(self.game.play_time // 60000)
        seconds = int((self.game.play_time // 1000) % 60)
        milliseconds = int(self.game.play_time % 1000)
        column = (self.game.width - 56) // 3
        self._draw_stat(column // 2, get_translation("1up"), f"{self.game.score:06d}")
        self._draw_stat(column + column // 2, get_translation("high_score"), f"{self.game.high_score:06d}")
        self._draw_stat(2 * column + column // 2, get_translation("time"),
                        f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}")

        self.game.pause_menu.draw_pause_button(screen)

    def draw_footer(self):
        self.game.screen.blit(self.footer_bar, (0, self.footer_y))

    def draw_ready(self):
        if self.game.show_ready:
            text = get_translation("ready")
            if text not in self._ready_text:
                self._ready_text[text] = outlined_text(text, theme.display_font(26), theme.FLAME, theme.NIGHT)
            ready_y = 18 * self.game.num1_r + self.game.y_offset + self.game.num1_r // 2
            image = self._ready_text[text]
            self.game.screen.blit(image, image.get_rect(center=(self.game.width // 2, ready_y)))

    def draw_lives(self):
        icon_y = self.footer_y + (self.game.height - self.footer_y - LIFE_ICON_SIZE) // 2
        for i in range(self.game.lives - 1):
            self.game.screen.blit(self.lives_icon, (BAR_PADDING + i * LIFE_ICON_SIZE, icon_y))

    def draw_hint_button(self):
        style = 'active' if self.game.show_hint or self.hint_hover else 'normal'
        colors = draw_slab_button(self.game.screen, self.hint_rect, style)
        draw_text(self.game.screen, "HINT", label_font(21), colors['text'], center=self.hint_rect.center)

    def draw_ghost_toggle_buttons(self):
        screen = self.game.screen
        for i, rect in enumerate(self.ghost_rects):
            shown = self.visible_ghost_flags()[i]
            if self.ghost_hover[i]:
                style = 'active'
            else:
                style = 'normal' if shown else 'off'
            draw_slab_button(screen, rect, style)
            portrait = self.portraits[i] if shown else self.hidden_portraits[i]
            screen.blit(portrait, portrait.get_rect(center=rect.center))
            if not shown:
                pygame.draw.line(screen, theme.PARCHMENT, (rect.x + 9, rect.bottom - 10), (rect.right - 10, rect.y + 9), 2)

    def _solve_style(self):
        if self.solve_menu_visible or (self.solve_hover and not self.game.solve_locked):
            return 'active'
        if self.game.solve_locked and not self.selected_solve:
            return 'off'  # Đang chơi tay: nút giải đã khóa cho ván này
        return 'normal'

    def draw_solve_button(self):
        screen = self.game.screen
        colors = draw_slab_button(screen, self.solve_rect, self._solve_style())

        label = self.selected_solve.upper() if self.selected_solve else "SOLVE"
        can_open = not self.game.solve_locked
        text_area = self.solve_rect.width - (44 if can_open else 24)
        font = fit_font(label_font, label, text_area, 21)
        draw_text(screen, label, font, colors['text'], center=self.solve_rect.center)
        if can_open:
            self._draw_chevron(colors['text'])

        if self.solve_menu_visible:
            self._draw_solve_dropdown()

    def _draw_chevron(self, color):
        x, y = self.solve_rect.right - 20, self.solve_rect.centery
        pygame.draw.lines(self.game.screen, color, False, [(x - 5, y + 3), (x, y - 3), (x + 5, y + 3)], 2)

    def _draw_solve_dropdown(self):
        screen = self.game.screen
        slab = chamfered_slab(self.dropdown_rect.size, (theme.PANEL_TOP, theme.PANEL_BOTTOM),
                              (theme.COPPER_LIGHT, theme.COPPER_DARK))
        screen.blit(slab, self.dropdown_rect.topleft)

        active = BUTTON_STYLES['active']
        for i, option in enumerate(self.solve_options):
            rect = self.solve_option_rects[i]
            if self.solve_option_hover[i]:
                screen.blit(chamfered_slab(rect.size, active['fill'], active['edge'], chamfer=5, edge_width=1), rect)
            color = active['text'] if self.solve_option_hover[i] else theme.PARCHMENT
            draw_text(screen, option, label_font(19), color, center=rect.center)

    def update_hover(self, mouse_pos):
        hover_sound = self.game.sound_manager.button_hover_sound

        prev_hint_hover = self.hint_hover
        prev_solve_hover = self.solve_hover
        prev_ghost_hover = self.ghost_hover.copy()
        prev_option_hover = self.solve_option_hover.copy()

        self.hint_hover = self.hint_rect.collidepoint(mouse_pos)
        self.solve_hover = self.solve_rect.collidepoint(mouse_pos)
        self.ghost_hover = [rect.collidepoint(mouse_pos) for rect in self.ghost_rects]
        self.solve_option_hover = [False] * len(self.solve_options)
        if self.solve_menu_visible:
            self.solve_option_hover = [rect.collidepoint(mouse_pos) for rect in self.solve_option_rects]

        if (self.hint_hover and not prev_hint_hover) or (self.solve_hover and not prev_solve_hover):
            hover_sound.play()
        for i in range(4):
            if self.ghost_hover[i] and not prev_ghost_hover[i]:
                hover_sound.play()
        if self.solve_menu_visible:
            for i in range(len(self.solve_options)):
                if self.solve_option_hover[i] and not prev_option_hover[i]:
                    hover_sound.play()
