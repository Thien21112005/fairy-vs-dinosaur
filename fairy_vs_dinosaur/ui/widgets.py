import pygame

MENU_BUTTON_COLORS = {
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

CLOSE_BUTTON_COLORS = {
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

_fonts = {}


def get_font(name, size, bold=False):
    """SysFont có cache, an toàn khi gọi trong mỗi khung hình."""
    key = (name, size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont(name, size, bold=bold)
    return _fonts[key]


def draw_gradient_rect(surface, rect, start_color, end_color, border_color=None, border_width=0, border_radius=0):
    """Vẽ hình chữ nhật gradient dọc, có thể bo góc và có viền. Màu RGB hoặc RGBA."""
    start_alpha = start_color[3] if len(start_color) > 3 else 255
    end_alpha = end_color[3] if len(end_color) > 3 else 255

    gradient = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        ratio = y / rect.height
        color = (
            int(start_color[0] + (end_color[0] - start_color[0]) * ratio),
            int(start_color[1] + (end_color[1] - start_color[1]) * ratio),
            int(start_color[2] + (end_color[2] - start_color[2]) * ratio),
            int(start_alpha + (end_alpha - start_alpha) * ratio)
        )
        pygame.draw.line(gradient, color, (0, y), (rect.width, y))

    if border_radius > 0:
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.width, rect.height), border_radius=border_radius)
        gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(gradient, rect.topleft)

    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=border_radius)


def draw_soft_rect(surface, rect, color, border_radius=0):
    """Vẽ hình chữ nhật bán trong suốt, dùng cho bóng đổ và glow."""
    temp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(temp, color, (0, 0, rect.width, rect.height), border_radius=border_radius)
    surface.blit(temp, rect.topleft)


def draw_menu_button(surface, rect, text, font, hover):
    colors = MENU_BUTTON_COLORS['hover' if hover else 'normal']
    draw_soft_rect(surface, rect.move(4, 4), (0, 0, 0, 40), border_radius=20)
    if hover:
        draw_soft_rect(surface, rect.inflate(16, 16), colors['glow'], border_radius=25)
    draw_gradient_rect(surface, rect, colors['bg_start'], colors['bg_end'],
                       border_color=colors['border'], border_width=3, border_radius=18)

    text_surface = font.render(text, True, colors['text'])
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(font.render(text, True, (0, 0, 0, 100)), (text_rect.x + 2, text_rect.y + 2))
    surface.blit(text_surface, text_rect)


def draw_close_button(surface, rect, hover):
    colors = CLOSE_BUTTON_COLORS['hover' if hover else 'normal']
    draw_soft_rect(surface, rect.move(2, 2), (0, 0, 0, 40), border_radius=8)
    if hover:
        draw_soft_rect(surface, rect.inflate(10, 10), colors['glow'], border_radius=12)
    draw_gradient_rect(surface, rect, colors['bg_start'], colors['bg_end'],
                       border_color=colors['border'], border_width=2, border_radius=10)

    close_text = get_font('arial', 20, bold=True).render("×", True, (255, 255, 255))
    surface.blit(close_text, close_text.get_rect(center=rect.center))
