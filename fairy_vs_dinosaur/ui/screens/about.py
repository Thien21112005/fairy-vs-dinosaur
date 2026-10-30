import pygame

from fairy_vs_dinosaur.config import asset
from fairy_vs_dinosaur.i18n import get_translation


class AboutMenu:
    def __init__(self, screen, sound_manager, background, back_callback):
        self.screen = screen
        self.sound_manager = sound_manager
        self.background = background
        self.back_callback = back_callback
        self.width, self.height = screen.get_size()
        self.timer = pygame.time.Clock()
        self.fps = 60

        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.section_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 20)
        self.button_font = pygame.font.SysFont('Arial', 28, bold=True)

        # Colors
        self.text_color = (255, 255, 255)
        self.shadow_color = (0, 0, 0)  # For text shadows
        self.section_color = (220, 160, 50)
        self.bg_color = (30, 30, 50, 220)  # Adjusted for better contrast and aesthetics (darker blue-ish tone, more opaque)

        # Load images (assuming PNG files)
        self.images = []
        for i in range(1, 4):
            img_path = asset(f"images/menu/{i}.png")
            try:
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, (200, 200))  # Scale to fit
                self.images.append(img)
            except:
                print(f"Không thể load hình {img_path}")

        # Back button
        button_width = 200
        button_height = 60
        self.back_rect = pygame.Rect(self.width // 2 - button_width // 2, self.height - 100, button_width, button_height)
        self.back_hover = False
        self.prev_back_hover = False

        # Button colors (reuse from MainMenu)
        self.button_colors = {
            'normal': {
                'bg_start': (70, 130, 180, 180),
                'bg_end': (30, 80, 120, 180),
                'border': (120, 180, 220, 220),
                'text': (220, 240, 255),
                'glow': (80, 150, 200, 60)
            },
            'hover': {
                'bg_start': (220, 160, 50, 200),
                'bg_end': (180, 120, 30, 200),
                'border': (255, 215, 100, 240),
                'text': (255, 255, 240),
                'glow': (255, 200, 80, 80)
            }
        }

        # Close button
        self.close_rect = pygame.Rect(self.width - 45, 15, 35, 35)
        self.close_hover = False
        self.prev_close_hover = False

        # Close colors (reuse)
        self.close_colors = {
            'normal': {
                'bg_start': (180, 70, 70, 180),
                'bg_end': (140, 40, 40, 180),
                'border': (220, 120, 120, 220),
                'glow': (200, 100, 100, 60)
            },
            'hover': {
                'bg_start': (220, 80, 80, 200),
                'bg_end': (180, 50, 50, 200),
                'border': (255, 150, 150, 240),
                'glow': (255, 120, 120, 80)
            }
        }

        # Content text using translations
        self.content = {
            "title": get_translation("about_title"),
            "overview": [
                get_translation("overview_1"),
                get_translation("overview_2")
            ],
            "key_features_title": get_translation("key_features_title"),
            "key_features": [
                get_translation("key_feature_1"),
                get_translation("key_feature_2"),
                get_translation("key_feature_3"),
                get_translation("key_feature_4"),
                get_translation("key_feature_5"),
                get_translation("key_feature_6"),
                get_translation("key_feature_7"),
                get_translation("key_feature_8"),
                get_translation("key_feature_9")
            ],
            "team_title": get_translation("team_title"),
            "team": [
                get_translation("team_1"),
                get_translation("team_2"),
                get_translation("team_3"),
                get_translation("team_4"),
                get_translation("team_5")
            ],
            "join_title": get_translation("join_title"),
            "join": [
                get_translation("join_1")
            ]
        }

        # Scrolling vArialbles
        self.scroll_y = 0
        self.max_scroll = 0
        self.view_rect = pygame.Rect(50, 50, self.width - 100, self.height - 150)  # Fixed view area for content

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + word + ' '
            test_size = font.size(test_line)[0]
            if test_size <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + ' '
        if current_line:
            lines.append(current_line.strip())
        return lines

    def draw_text_block(self, lines, font, color, x, y, line_spacing=5):
        """Draw multi-line text with shadow"""
        current_y = y
        for line in lines:
            shadow = font.render(line, True, self.shadow_color)
            text = font.render(line, True, color)
            self.content_surface.blit(shadow, (x + 1, current_y + 1))
            self.content_surface.blit(text, (x, current_y))
            current_y += text.get_height() + line_spacing
        return current_y

    def calculate_content_height(self):
        content_width = self.view_rect.width
        y_pos = 20

        # Title
        title_lines = self.wrap_text(self.content["title"], self.title_font, content_width - 40)
        y_pos += len(title_lines) * self.title_font.get_height() + (len(title_lines) - 1) * 5 + 30

        # Overview
        for para in self.content["overview"]:
            wrapped = self.wrap_text(para, self.text_font, content_width - 40)
            y_pos += len(wrapped) * self.text_font.get_height() + (len(wrapped) - 1) * 5 + 20

        # Image 1
        if len(self.images) > 0:
            y_pos += self.images[0].get_height() + 30

        # Key Features Title
        kf_title_lines = self.wrap_text(self.content["key_features_title"], self.section_font, content_width - 40)
        y_pos += len(kf_title_lines) * self.section_font.get_height() + (len(kf_title_lines) - 1) * 5 + 10

        # Key Features
        for feature in self.content["key_features"]:
            wrapped = self.wrap_text(feature, self.text_font, content_width - 40)
            y_pos += len(wrapped) * self.text_font.get_height() + (len(wrapped) - 1) * 5 + 10

        # Image 2
        if len(self.images) > 1:
            y_pos += self.images[1].get_height() + 30

        # Team Title
        team_title_lines = self.wrap_text(self.content["team_title"], self.section_font, content_width - 40)
        y_pos += len(team_title_lines) * self.section_font.get_height() + (len(team_title_lines) - 1) * 5 + 10

        # Team
        for para in self.content["team"]:
            wrapped = self.wrap_text(para, self.text_font, content_width - 40)
            y_pos += len(wrapped) * self.text_font.get_height() + (len(wrapped) - 1) * 5 + 10

        # Image 3
        if len(self.images) > 2:
            y_pos += self.images[2].get_height() + 30

        # Join Title
        join_title_lines = self.wrap_text(self.content["join_title"], self.section_font, content_width - 40)
        y_pos += len(join_title_lines) * self.section_font.get_height() + (len(join_title_lines) - 1) * 5 + 10

        # Join
        for para in self.content["join"]:
            wrapped = self.wrap_text(para, self.text_font, content_width - 40)
            y_pos += len(wrapped) * self.text_font.get_height() + (len(wrapped) - 1) * 5 + 20

        return y_pos + 100  # Thêm margin an toàn

    def draw_gradient_rect(self, surface, rect, start_color, end_color, border_color=None, border_width=0, border_radius=0):
        """Reuse draw_gradient_rect from MainMenu"""
        bg_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            a = int(start_color[3] + (end_color[3] - start_color[3]) * ratio)
            color = (r, g, b, a)
            pygame.draw.line(bg_surface, color, (0, y), (rect.width, y))

        if border_radius > 0:
            rounded_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(rounded_surface, (255, 255, 255, 255), (0, 0, rect.width, rect.height), border_radius=border_radius)
            rounded_surface.blit(bg_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surface.blit(rounded_surface, rect.topleft)
            if border_color and border_width > 0:
                pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=border_radius)
        else:
            surface.blit(bg_surface, rect.topleft)
            if border_color and border_width > 0:
                pygame.draw.rect(surface, border_color, rect, width=border_width)

    def draw_back_button(self):
        hover = self.back_hover
        colors = self.button_colors['hover'] if hover else self.button_colors['normal']

        # Shadow
        shadow_rect = self.back_rect.move(4, 4)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=20)
        self.screen.blit(shadow_surface, shadow_rect.topleft)

        # Glow
        if hover:
            glow_rect = self.back_rect.inflate(16, 16)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, colors['glow'], (0, 0, glow_rect.width, glow_rect.height), border_radius=25)
            self.screen.blit(glow_surface, glow_rect.topleft)

        # Button bg
        self.draw_gradient_rect(
            self.screen, self.back_rect,
            colors['bg_start'], colors['bg_end'],
            border_color=colors['border'],
            border_width=3,
            border_radius=18
        )

        # Text
        text_color = colors['text']
        text = self.button_font.render(get_translation("back"), True, text_color)
        text_rect = text.get_rect(center=self.back_rect.center)

        shadow_text = self.button_font.render(get_translation("back"), True, (0, 0, 0, 100))
        self.screen.blit(shadow_text, (text_rect.x + 2, text_rect.y + 2))
        self.screen.blit(text, text_rect)

    def draw_close_button(self):
        colors = self.close_colors['hover'] if self.close_hover else self.close_colors['normal']

        # Shadow
        shadow_rect = self.close_rect.move(2, 2)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=8)
        self.screen.blit(shadow_surface, shadow_rect.topleft)

        # Glow
        if self.close_hover:
            glow_rect = self.close_rect.inflate(10, 10)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, colors['glow'], (0, 0, glow_rect.width, glow_rect.height), border_radius=12)
            self.screen.blit(glow_surface, glow_rect.topleft)

        # Button bg
        self.draw_gradient_rect(
            self.screen, self.close_rect,
            colors['bg_start'], colors['bg_end'],
            border_color=colors['border'],
            border_width=2,
            border_radius=10
        )

        # X text
        close_font = pygame.font.SysFont('Arial', 20, bold=True)
        close_text = close_font.render("×", True, (255, 255, 255))
        text_rect = close_text.get_rect(center=self.close_rect.center)
        self.screen.blit(close_text, text_rect)

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.back_rect.collidepoint(mouse_pos) or self.close_rect.collidepoint(mouse_pos):
                    self.sound_manager.button_click_sound.play()
                    return False
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_y -= event.y * 20  # Scroll speed
                self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
        return True

    def draw_content(self):
        content_width = self.view_rect.width
        content_height = self.calculate_content_height()  # Dynamic calculation

        # Tạo surface với chiều cao được tính toán, thêm margin an toàn
        safe_height = content_height + 100
        self.content_surface = pygame.Surface((content_width, safe_height), pygame.SRCALPHA)
        self.content_surface.fill((0, 0, 0, 0))

        y_pos = 20

        # Title with shadow
        title_lines = self.wrap_text(self.content["title"], self.title_font, content_width - 40)
        for i, line in enumerate(title_lines):
            shadow = self.title_font.render(line, True, self.shadow_color)
            title = self.title_font.render(line, True, self.section_color)
            x = content_width // 2 - title.get_width() // 2
            self.content_surface.blit(shadow, (x + 2, y_pos + 2 + i * (self.title_font.get_height() + 5)))
            self.content_surface.blit(title, (x, y_pos + i * (self.title_font.get_height() + 5)))
        y_pos += len(title_lines) * self.title_font.get_height() + (len(title_lines) - 1) * 5 + 30

        # Overview
        for para in self.content["overview"]:
            wrapped = self.wrap_text(para, self.text_font, content_width - 40)
            y_pos = self.draw_text_block(wrapped, self.text_font, self.text_color, 20, y_pos, 5)
            y_pos += 20  # Paragraph spacing

        # Insert image 1 after overview
        if len(self.images) > 0:
            img = self.images[0]
            self.content_surface.blit(img, (content_width // 2 - img.get_width() // 2, y_pos))
            y_pos += img.get_height() + 30

        # Key Features Title with shadow
        kf_title_lines = self.wrap_text(self.content["key_features_title"], self.section_font, content_width - 40)
        for i, line in enumerate(kf_title_lines):
            shadow = self.section_font.render(line, True, self.shadow_color)
            kf_title = self.section_font.render(line, True, self.section_color)
            self.content_surface.blit(shadow, (21, y_pos + 1 + i * (self.section_font.get_height() + 5)))
            self.content_surface.blit(kf_title, (20, y_pos + i * (self.section_font.get_height() + 5)))
        y_pos += len(kf_title_lines) * self.section_font.get_height() + (len(kf_title_lines) - 1) * 5 + 10

        # Key Features
        for feature in self.content["key_features"]:
            wrapped = self.wrap_text(feature, self.text_font, content_width - 40)
            y_pos = self.draw_text_block(wrapped, self.text_font, self.text_color, 20, y_pos, 5)
            y_pos += 10

        # Insert image 2 after key features
        if len(self.images) > 1:
            img = self.images[1]
            self.content_surface.blit(img, (content_width // 2 - img.get_width() // 2, y_pos))
            y_pos += img.get_height() + 30

        # Team Title with shadow
        team_title_lines = self.wrap_text(self.content["team_title"], self.section_font, content_width - 40)
        for i, line in enumerate(team_title_lines):
            shadow = self.section_font.render(line, True, self.shadow_color)
            team_title = self.section_font.render(line, True, self.section_color)
            self.content_surface.blit(shadow, (21, y_pos + 1 + i * (self.section_font.get_height() + 5)))
            self.content_surface.blit(team_title, (20, y_pos + i * (self.section_font.get_height() + 5)))
        y_pos += len(team_title_lines) * self.section_font.get_height() + (len(team_title_lines) - 1) * 5 + 10

        # Team
        for para in self.content["team"]:
            wrapped = self.wrap_text(para, self.text_font, content_width - 40)
            y_pos = self.draw_text_block(wrapped, self.text_font, self.text_color, 20, y_pos, 5)
            y_pos += 10

        # Insert image 3 after team
        if len(self.images) > 2:
            img = self.images[2]
            self.content_surface.blit(img, (content_width // 2 - img.get_width() // 2, y_pos))
            y_pos += img.get_height() + 30

        # Join Title with shadow
        join_title_lines = self.wrap_text(self.content["join_title"], self.section_font, content_width - 40)
        for i, line in enumerate(join_title_lines):
            shadow = self.section_font.render(line, True, self.shadow_color)
            join_title = self.section_font.render(line, True, self.section_color)
            self.content_surface.blit(shadow, (21, y_pos + 1 + i * (self.section_font.get_height() + 5)))
            self.content_surface.blit(join_title, (20, y_pos + i * (self.section_font.get_height() + 5)))
        y_pos += len(join_title_lines) * self.section_font.get_height() + (len(join_title_lines) - 1) * 5 + 10

        # Join
        for para in self.content["join"]:
            wrapped = self.wrap_text(para, self.text_font, content_width - 40)
            y_pos = self.draw_text_block(wrapped, self.text_font, self.text_color, 20, y_pos, 5)
            y_pos += 20

        # Calculate max scroll
        actual_height = y_pos + 20
        self.max_scroll = max(0, actual_height - self.view_rect.height)

        # Draw semi-transparent bg for view
        view_bg = pygame.Surface(self.view_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(view_bg, self.bg_color, (0, 0, self.view_rect.width, self.view_rect.height), border_radius=20)
        self.screen.blit(view_bg, self.view_rect.topleft)

        # Blit content subsection based on scroll
        blit_area = pygame.Rect(0, self.scroll_y, self.view_rect.width, self.view_rect.height)
        self.screen.blit(self.content_surface, self.view_rect.topleft, area=blit_area)

    def run(self):
        running = True
        while running:
            self.timer.tick(self.fps)
            running = self.handle_events()
            mouse_pos = pygame.mouse.get_pos()
            self.update_hover(mouse_pos)

            # Draw
            self.screen.blit(self.background, (0, 0))
            self.draw_content()
            self.draw_back_button()
            self.draw_close_button()
            pygame.display.flip()
        # Call back callback when exiting
        self.back_callback()
