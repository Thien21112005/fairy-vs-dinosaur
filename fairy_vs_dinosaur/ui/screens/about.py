import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui import theme
from fairy_vs_dinosaur.ui.theme import body_font, display_font
from fairy_vs_dinosaur.ui.widgets import (dimmed_backdrop, draw_close_button, draw_divider, draw_menu_button,
                                          draw_panel, draw_scrollbar, draw_text, outlined_text)

PANEL_WIDTH = 800
PANEL_TOP = 22
BOTTOM_BAR_HEIGHT = 72
TEXT_WIDTH = 690  # Khoảng 70 ký tự mỗi dòng ở cỡ chữ này: dài hơn sẽ khó đọc
IMAGE_SIZE = 260
SCROLL_STEP = 40
LINE_GAP = 4


class AboutMenu:
    def __init__(self, screen, sound_manager, background):
        self.screen = screen
        self.sound_manager = sound_manager
        self.background = dimmed_backdrop(background)
        self.width, self.height = screen.get_size()
        self.timer = pygame.time.Clock()
        self.fps = 60

        self.images = []
        for i in range(1, 4):
            img_path = asset(f"images/menu/{i}.png")
            try:
                img = pygame.image.load(img_path).convert_alpha()
                self.images.append(pygame.transform.smoothscale(img, (IMAGE_SIZE, IMAGE_SIZE)))
            except (pygame.error, FileNotFoundError):
                print(f"Không thể load hình {img_path}")

        button_y = self.height - BOTTOM_BAR_HEIGHT + (BOTTOM_BAR_HEIGHT - 46) // 2
        self.back_rect = pygame.Rect(self.width // 2 - 110, button_y, 220, 46)
        self.back_hover = False
        self.prev_back_hover = False

        self.close_rect = pygame.Rect(self.width - 46, 14, 36, 36)
        self.close_hover = False
        self.prev_close_hover = False

        self.title = get_translation("about_title")
        # Mỗi phần: (tiêu đề hoặc None, các đoạn văn, khoảng cách sau đoạn, chỉ số ảnh chèn sau phần hoặc None)
        self.sections = [
            (None, self._texts("overview", 2), 16, 0),
            (get_translation("key_features_title"), self._texts("key_feature", 9), 10, 1),
            (get_translation("team_title"), self._texts("team", 5), 10, 2),
            (get_translation("join_title"), self._texts("join", 1), 16, None),
        ]

        self.panel_rect = pygame.Rect((self.width - PANEL_WIDTH) // 2, PANEL_TOP, PANEL_WIDTH,
                                      self.height - PANEL_TOP - BOTTOM_BAR_HEIGHT)
        self.view_rect = self.panel_rect.inflate(-8, -8)

        self.scroll_y = 0
        self.content = self._build_content()
        self.max_scroll = max(0, self.content.get_height() - self.view_rect.height)

    @staticmethod
    def _texts(prefix, count):
        return [get_translation(f"{prefix}_{i}") for i in range(1, count + 1)]

    @staticmethod
    def wrap_text(text, font, max_width):
        lines = []
        current_line = ''
        for word in text.split(' '):
            test_line = current_line + word + ' '
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + ' '
        if current_line:
            lines.append(current_line.strip())
        return lines

    def _layout_content(self):
        """Danh sách (Surface, x, y) và chiều cao tổng, để văn bản dài chỉ phải dàn trang một lần."""
        items = []
        center_x = self.view_rect.width // 2
        left = center_x - TEXT_WIDTH // 2

        title = outlined_text(self.title, display_font(38), theme.STONE, theme.COPPER_DARK)
        items.append((title, center_x - title.get_width() // 2, 18))
        y = 18 + title.get_height() + 40

        text_font = body_font(20)
        heading_font = display_font(27)
        for heading, paragraphs, spacing, image_index in self.sections:
            if heading:
                y += 14
                rendered = heading_font.render(heading, True, theme.COPPER_LIGHT)
                items.append((rendered, left, y))
                y += rendered.get_height() + 6
            for paragraph in paragraphs:
                for line in self.wrap_text(paragraph, text_font, TEXT_WIDTH):
                    rendered = text_font.render(line, True, theme.PARCHMENT)
                    items.append((rendered, left, y))
                    y += rendered.get_height() + LINE_GAP
                y += spacing
            if image_index is not None and image_index < len(self.images):
                image = self.images[image_index]
                items.append((self._framed(image), center_x - image.get_width() // 2 - 3, y + 6))
                y += image.get_height() + 30
        return items, y + 24

    @staticmethod
    def _framed(image):
        framed = pygame.Surface((image.get_width() + 6, image.get_height() + 6))
        framed.fill(theme.NIGHT)
        pygame.draw.rect(framed, theme.COPPER, framed.get_rect(), width=2)
        framed.blit(image, (3, 3))
        return framed

    def _build_content(self):
        items, height = self._layout_content()
        content = pygame.Surface((self.view_rect.width, height), pygame.SRCALPHA)
        for surface, x, y in items:
            content.blit(surface, (x, y))
        divider_y = 18 + display_font(38).get_height() + 16
        draw_divider(content, (self.view_rect.width // 2, divider_y), 360)
        return content

    def draw_content(self):
        draw_panel(self.screen, self.panel_rect)
        area = pygame.Rect(0, self.scroll_y, self.view_rect.width, self.view_rect.height)
        self.screen.blit(self.content, self.view_rect.topleft, area=area)
        track = pygame.Rect(self.view_rect.right - 12, self.view_rect.y + 10, 6, self.view_rect.height - 20)
        draw_scrollbar(self.screen, track, self.scroll_y, self.max_scroll,
                       self.view_rect.height / self.content.get_height())

    def draw_back_button(self):
        draw_menu_button(self.screen, self.back_rect, get_translation("back"), self.back_hover)

    def draw_close_button(self):
        draw_close_button(self.screen, self.close_rect, self.close_hover)

    def update_hover(self, mouse_pos):
        current_back_hover = self.back_rect.collidepoint(mouse_pos)
        if current_back_hover and not self.prev_back_hover:
            self.sound_manager.button_hover_sound.play()
        self.back_hover = current_back_hover
        self.prev_back_hover = current_back_hover

        current_close_hover = self.close_rect.collidepoint(mouse_pos)
        if current_close_hover and not self.prev_close_hover:
            self.sound_manager.button_hover_sound.play()
        self.close_hover = current_close_hover
        self.prev_close_hover = current_close_hover

    def _scroll_by(self, amount):
        self.scroll_y = max(0, min(self.scroll_y + amount, self.max_scroll))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_DOWN:
                    self._scroll_by(SCROLL_STEP)
                elif event.key == pygame.K_UP:
                    self._scroll_by(-SCROLL_STEP)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.back_rect.collidepoint(mouse_pos) or self.close_rect.collidepoint(mouse_pos):
                    self.sound_manager.button_click_sound.play()
                    return False
            elif event.type == pygame.MOUSEWHEEL:
                self._scroll_by(-event.y * SCROLL_STEP)
        return True

    def run(self):
        running = True
        while running:
            self.timer.tick(self.fps)
            running = self.handle_events()
            self.update_hover(pygame.mouse.get_pos())

            self.screen.blit(self.background, (0, 0))
            self.draw_content()
            self.draw_back_button()
            self.draw_close_button()
            pygame.display.flip()
