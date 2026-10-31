import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.ui.widgets import draw_close_button, draw_menu_button


class AboutMenu:
    def __init__(self, screen, sound_manager, background):
        self.screen = screen
        self.sound_manager = sound_manager
        self.background = background
        self.width, self.height = screen.get_size()
        self.timer = pygame.time.Clock()
        self.fps = 60

        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.section_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 20)
        self.button_font = pygame.font.SysFont('Arial', 28, bold=True)

        self.text_color = (255, 255, 255)
        self.shadow_color = (0, 0, 0)
        self.section_color = (220, 160, 50)
        self.bg_color = (30, 30, 50, 220)

        self.images = []
        for i in range(1, 4):
            img_path = asset(f"images/menu/{i}.png")
            try:
                img = pygame.image.load(img_path).convert_alpha()
                self.images.append(pygame.transform.scale(img, (200, 200)))
            except (pygame.error, FileNotFoundError):
                print(f"Không thể load hình {img_path}")

        button_width = 200
        button_height = 60
        self.back_rect = pygame.Rect(self.width // 2 - button_width // 2, self.height - 100, button_width, button_height)
        self.back_hover = False
        self.prev_back_hover = False

        self.close_rect = pygame.Rect(self.width - 45, 15, 35, 35)
        self.close_hover = False
        self.prev_close_hover = False

        self.title = get_translation("about_title")
        # Mỗi phần: (tiêu đề hoặc None, các đoạn văn, khoảng cách sau đoạn, chỉ số ảnh chèn sau phần hoặc None)
        self.sections = [
            (None, self._texts("overview", 2), 20, 0),
            (get_translation("key_features_title"), self._texts("key_feature", 9), 10, 1),
            (get_translation("team_title"), self._texts("team", 5), 10, 2),
            (get_translation("join_title"), self._texts("join", 1), 20, None),
        ]

        self.scroll_y = 0
        self.max_scroll = 0
        self.view_rect = pygame.Rect(50, 50, self.width - 100, self.height - 150)

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

    def calculate_content_height(self):
        wrap_width = self.view_rect.width - 40

        def block_height(text, font, spacing):
            lines = self.wrap_text(text, font, wrap_width)
            return len(lines) * font.get_height() + (len(lines) - 1) * 5 + spacing

        y_pos = 20 + block_height(self.title, self.title_font, 30)
        for heading, paragraphs, spacing, image_index in self.sections:
            if heading:
                y_pos += block_height(heading, self.section_font, 10)
            for para in paragraphs:
                y_pos += block_height(para, self.text_font, spacing)
            if image_index is not None and image_index < len(self.images):
                y_pos += self.images[image_index].get_height() + 30
        return y_pos + 100

    def _draw_paragraph(self, surface, text, y):
        for line in self.wrap_text(text, self.text_font, self.view_rect.width - 40):
            rendered = self.text_font.render(line, True, self.text_color)
            surface.blit(self.text_font.render(line, True, self.shadow_color), (21, y + 1))
            surface.blit(rendered, (20, y))
            y += rendered.get_height() + 5
        return y

    def _draw_heading(self, surface, text, font, y, centered=False, shadow_offset=1):
        content_width = self.view_rect.width
        lines = self.wrap_text(text, font, content_width - 40)
        for i, line in enumerate(lines):
            rendered = font.render(line, True, self.section_color)
            x = content_width // 2 - rendered.get_width() // 2 if centered else 20
            line_y = y + i * (font.get_height() + 5)
            surface.blit(font.render(line, True, self.shadow_color), (x + shadow_offset, line_y + shadow_offset))
            surface.blit(rendered, (x, line_y))
        return y + len(lines) * font.get_height() + (len(lines) - 1) * 5

    def draw_content(self):
        content_width = self.view_rect.width
        surface = pygame.Surface((content_width, self.calculate_content_height() + 100), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))

        y_pos = self._draw_heading(surface, self.title, self.title_font, 20, centered=True, shadow_offset=2) + 30
        for heading, paragraphs, spacing, image_index in self.sections:
            if heading:
                y_pos = self._draw_heading(surface, heading, self.section_font, y_pos) + 10
            for para in paragraphs:
                y_pos = self._draw_paragraph(surface, para, y_pos) + spacing
            if image_index is not None and image_index < len(self.images):
                img = self.images[image_index]
                surface.blit(img, (content_width // 2 - img.get_width() // 2, y_pos))
                y_pos += img.get_height() + 30

        self.max_scroll = max(0, y_pos + 20 - self.view_rect.height)

        view_bg = pygame.Surface(self.view_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(view_bg, self.bg_color, (0, 0, self.view_rect.width, self.view_rect.height), border_radius=20)
        self.screen.blit(view_bg, self.view_rect.topleft)

        blit_area = pygame.Rect(0, self.scroll_y, self.view_rect.width, self.view_rect.height)
        self.screen.blit(surface, self.view_rect.topleft, area=blit_area)

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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.back_rect.collidepoint(mouse_pos) or self.close_rect.collidepoint(mouse_pos):
                    self.sound_manager.button_click_sound.play()
                    return False
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_y = max(0, min(self.scroll_y - event.y * 20, self.max_scroll))
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
