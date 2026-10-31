import pygame

from fairy_vs_dinosaur.ui import theme
from fairy_vs_dinosaur.ui.theme import display_font, fit_font, label_font

SUPERSAMPLE = 3  # pygame không khử răng cưa đa giác: vẽ lớn rồi thu nhỏ
BUTTON_CHAMFER = 9
PANEL_CHAMFER = 16

BUTTON_STYLES = {
    'normal': {'fill': (theme.SLAB_TOP, theme.SLAB_BOTTOM), 'edge': (theme.COPPER_LIGHT, theme.COPPER_DARK),
               'text': theme.PARCHMENT},
    'primary': {'fill': ((178, 88, 34), (116, 50, 20)), 'edge': (theme.FLAME_LIGHT, theme.EMBER_DARK),
                'text': theme.PARCHMENT},
    'danger': {'fill': (theme.BLOOD, theme.BLOOD_DARK), 'edge': (theme.COPPER_LIGHT, theme.COPPER_DARK),
               'text': theme.PARCHMENT},
    'active': {'fill': (theme.FLAME_LIGHT, theme.EMBER), 'edge': ((255, 240, 186), theme.EMBER_DARK),
               'text': theme.NIGHT},
    'off': {'fill': ((30, 46, 50), (18, 30, 34)), 'edge': ((96, 110, 110), (52, 62, 64)), 'text': theme.MIST},
}

_slabs = {}
_shadows = {}
_titles = {}
_backdrops = {}


def scale_pixel_art(image, size):
    """Phóng pixel art mà không nhòe: phóng nguyên lần cho sắc cạnh rồi thu nhỏ về đúng cỡ."""
    width, height = image.get_size()
    factor = max(2, 2 * max(size[0] // width, size[1] // height) + 2)
    return pygame.transform.smoothscale(pygame.transform.scale(image, (width * factor, height * factor)), size)


def _gradient(size, top, bottom):
    gradient = pygame.Surface(size, pygame.SRCALPHA)
    height = max(1, size[1] - 1)
    for y in range(size[1]):
        ratio = y / height
        color = [int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3)]
        pygame.draw.line(gradient, color, (0, y), (size[0], y))
    return gradient


def _chamfer_points(width, height, chamfer, inset=0):
    left, top, right, bottom = inset, inset, width - inset - 1, height - inset - 1
    c = max(1, chamfer - inset // 2)
    return [(left + c, top), (right - c, top), (right, top + c), (right, bottom - c),
            (right - c, bottom), (left + c, bottom), (left, bottom - c), (left, top + c)]


def _masked(gradient, points):
    mask = pygame.Surface(gradient.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), points)
    gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return gradient


def chamfered_slab(size, fill, edge, chamfer=BUTTON_CHAMFER, edge_width=2):
    """Phiến đá vát góc viền đồng. Có cache, an toàn khi gọi trong mỗi khung hình."""
    key = (size, fill, edge, chamfer, edge_width)
    if key not in _slabs:
        big = (size[0] * SUPERSAMPLE, size[1] * SUPERSAMPLE)
        big_chamfer = chamfer * SUPERSAMPLE
        surface = pygame.Surface(big, pygame.SRCALPHA)
        pygame.draw.polygon(surface, (*theme.NIGHT, 255), _chamfer_points(*big, big_chamfer))
        frame = _masked(_gradient(big, *edge), _chamfer_points(*big, big_chamfer, SUPERSAMPLE))
        surface.blit(frame, (0, 0))
        inset = (1 + edge_width) * SUPERSAMPLE
        surface.blit(_masked(_gradient(big, *fill), _chamfer_points(*big, big_chamfer, inset)), (0, 0))
        _slabs[key] = pygame.transform.smoothscale(surface, size)
    return _slabs[key]


def draw_soft_shadow(surface, rect, offset=(0, 4), spread=6, alpha=150):
    """Bóng đổ mềm, có độ lệch: dựng từ khối tối được làm mờ bằng cách thu nhỏ rồi phóng lại."""
    key = (rect.size, spread, alpha)
    if key not in _shadows:
        size = (rect.width + spread * 4, rect.height + spread * 4)
        solid = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(solid, (0, 0, 0, alpha), (spread * 2, spread * 2, rect.width, rect.height),
                         border_radius=spread)
        factor = max(2, spread)
        small = pygame.transform.smoothscale(solid, (max(1, size[0] // factor), max(1, size[1] // factor)))
        _shadows[key] = pygame.transform.smoothscale(small, size)
    surface.blit(_shadows[key], (rect.x - spread * 2 + offset[0], rect.y - spread * 2 + offset[1]))


def draw_text(surface, text, font, color, shadow=False, **anchor):
    """Vẽ chữ theo neo của Rect, ví dụ center=(x, y). Trả về Rect đã vẽ."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(**anchor)
    if shadow:
        surface.blit(font.render(text, True, theme.NIGHT), rect.move(0, 2))
    surface.blit(rendered, rect)
    return rect


def outlined_text(text, font, color, edge, width=2, shadow=True):
    """Chữ viền kiểu chữ khắc trên tiêu đề. Trả về Surface."""
    body = font.render(text, True, color)
    rim = font.render(text, True, edge)
    drop = 3 if shadow else 0
    result = pygame.Surface((body.get_width() + width * 2, body.get_height() + width * 2 + drop), pygame.SRCALPHA)
    if shadow:
        dark = font.render(text, True, theme.NIGHT)
        for dx in range(-width, width + 1):
            result.blit(dark, (width + dx, width + drop))
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx * dx + dy * dy <= width * width + 1:
                result.blit(rim, (width + dx, width + dy))
    result.blit(body, (width, width))
    return result


def draw_title(surface, text, center, size, max_width, color=theme.STONE, edge=theme.COPPER_DARK):
    """Tiêu đề chữ đá viền đồng, tự giảm cỡ để luôn nằm trong max_width."""
    key = (text, size, max_width, color, edge)
    if key not in _titles:
        _titles[key] = outlined_text(text, fit_font(display_font, text, max_width - 8, size), color, edge)
    title = _titles[key]
    rect = title.get_rect(center=center)
    surface.blit(title, rect)
    return rect


def draw_divider(surface, center, width):
    """Đường kẻ đồng hai đầu mũi tên, lặp lại nét trang trí quanh chữ VS trên tranh nền."""
    x, y = center
    half = width // 2
    gap = 9
    for sign in (-1, 1):
        start, end = x + sign * gap, x + sign * half
        pygame.draw.line(surface, theme.COPPER, (start, y), (end, y), 2)
        tip = [(end + sign * 7, y), (end - sign * 1, y - 4), (end + sign * 2, y), (end - sign * 1, y + 4)]
        pygame.draw.polygon(surface, theme.COPPER_LIGHT, tip)
    pygame.draw.polygon(surface, theme.CRYSTAL, [(x, y - 5), (x + 5, y), (x, y + 5), (x - 5, y)])


def draw_panel(surface, rect, chamfer=PANEL_CHAMFER):
    """Tấm đá đặc: chữ bên trên không bao giờ đọc xuyên ra hình nền."""
    draw_soft_shadow(surface, rect, offset=(0, 8), spread=12, alpha=170)
    slab = chamfered_slab(rect.size, (theme.PANEL_TOP, theme.PANEL_BOTTOM), (theme.COPPER_LIGHT, theme.COPPER_DARK),
                          chamfer)
    surface.blit(slab, rect.topleft)


def draw_slab_button(surface, rect, style):
    draw_soft_shadow(surface, rect, offset=(0, 3), spread=4, alpha=120)
    colors = BUTTON_STYLES[style]
    surface.blit(chamfered_slab(rect.size, colors['fill'], colors['edge']), rect.topleft)
    return colors


def draw_menu_button(surface, rect, text, hover, size=24, style='normal'):
    colors = draw_slab_button(surface, rect, 'active' if hover else style)
    font = fit_font(label_font, text, rect.width - 24, size)
    draw_text(surface, text, font, colors['text'], center=rect.center)


def _draw_cross(surface, center, reach, color, width=3):
    x, y = center
    pygame.draw.line(surface, color, (x - reach, y - reach), (x + reach, y + reach), width)
    pygame.draw.line(surface, color, (x - reach, y + reach), (x + reach, y - reach), width)


def draw_close_button(surface, rect, hover):
    colors = draw_slab_button(surface, rect, 'danger' if hover else 'normal')
    _draw_cross(surface, rect.center, rect.width // 6, colors['text'])


def draw_scrollbar(surface, track, offset, max_offset, visible_ratio):
    """Thanh cuộn cho biết còn nội dung bên dưới. Không cần khi nội dung vừa khung."""
    if max_offset <= 0:
        return
    pygame.draw.rect(surface, theme.NIGHT, track, border_radius=3)
    thumb_height = max(32, int(track.height * visible_ratio))
    thumb_y = track.y + int((track.height - thumb_height) * (offset / max_offset))
    pygame.draw.rect(surface, theme.COPPER, (track.x, thumb_y, track.width, thumb_height), border_radius=3)


def dimmed_backdrop(background):
    """Tranh nền làm mờ và tối đi, để các màn hình chữ không phải tranh chỗ với chi tiết của tranh."""
    key = id(background)
    if key not in _backdrops:
        width, height = background.get_size()
        small = pygame.transform.smoothscale(background, (width // 8, height // 8))
        blurred = pygame.transform.smoothscale(small, (width, height))
        blurred.fill((96, 128, 132), special_flags=pygame.BLEND_RGB_MULT)
        _backdrops[key] = blurred
    return _backdrops[key]


# --- Sẽ bỏ khi mọi màn hình đã chuyển sang các khối dựng ở trên ---

_legacy_fonts = {}


def get_font(name, size, bold=False):
    key = (name, size, bold)
    if key not in _legacy_fonts:
        _legacy_fonts[key] = pygame.font.SysFont(name, size, bold=bold)
    return _legacy_fonts[key]


def draw_gradient_rect(surface, rect, start_color, end_color, border_color=None, border_width=0, border_radius=0):
    start_alpha = start_color[3] if len(start_color) > 3 else 255
    end_alpha = end_color[3] if len(end_color) > 3 else 255
    gradient = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        ratio = y / rect.height
        color = (int(start_color[0] + (end_color[0] - start_color[0]) * ratio),
                 int(start_color[1] + (end_color[1] - start_color[1]) * ratio),
                 int(start_color[2] + (end_color[2] - start_color[2]) * ratio),
                 int(start_alpha + (end_alpha - start_alpha) * ratio))
        pygame.draw.line(gradient, color, (0, y), (rect.width, y))
    if border_radius > 0:
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.width, rect.height), border_radius=border_radius)
        gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(gradient, rect.topleft)
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=border_radius)


def draw_soft_rect(surface, rect, color, border_radius=0):
    temp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(temp, color, (0, 0, rect.width, rect.height), border_radius=border_radius)
    surface.blit(temp, rect.topleft)
