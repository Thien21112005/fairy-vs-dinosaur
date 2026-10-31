"""Bảng màu và font của giao diện, lấy từ tranh nền menu: đá chạm viền đồng trong rừng đêm xanh ngọc."""
import pygame

from fairy_vs_dinosaur.config import asset

# Rừng đêm
NIGHT = (5, 20, 26)
SLAB_TOP = (22, 62, 68)
SLAB_BOTTOM = (10, 38, 45)
PANEL_TOP = (15, 49, 56)
PANEL_BOTTOM = (7, 28, 35)
HAIRLINE = (46, 94, 98)

# Chữ khắc đá và viền đồng của tiêu đề
STONE = (232, 216, 196)
COPPER_LIGHT = (232, 158, 92)
COPPER = (208, 124, 62)
COPPER_DARK = (122, 66, 32)

# Lửa của khủng long, pha lê của nàng tiên
FLAME_LIGHT = (255, 214, 104)
FLAME = (255, 188, 62)
EMBER = (232, 126, 38)
EMBER_DARK = (150, 64, 22)
CRYSTAL = (124, 236, 240)
MOSS = (146, 184, 78)
BLOOD = (150, 38, 30)
BLOOD_DARK = (92, 22, 18)

# Chữ
PARCHMENT = (248, 240, 222)
MIST = (178, 212, 210)

# Màu đường đi gợi ý: khớp với màu nhân vật đã vẽ và nổi trên nền đá
PATH_FAIRY = CRYSTAL
PATH_BLINKY = (255, 92, 70)
PATH_PINKY = (255, 158, 236)
PATH_INKY = (116, 170, 255)
PATH_CLYDE = (255, 196, 98)

_fonts = {}


def _font(filename, size):
    key = (filename, size)
    if key not in _fonts:
        _fonts[key] = pygame.font.Font(asset(f"fonts/{filename}"), size)
    return _fonts[key]


def display_font(size):
    """Tiêu đề."""
    return _font("AlegreyaSC-ExtraBold.ttf", size)


def label_font(size):
    """Nút và nhãn."""
    return _font("AlegreyaSC-Bold.ttf", size)


def strong_font(size):
    """Điểm số và phần nhấn mạnh. Chữ số dạng lining cùng độ rộng: mọi con số đều dùng font này hoặc body_font."""
    return _font("AlegreyaSans-Bold.ttf", size)


def body_font(size):
    """Văn bản và bảng số liệu."""
    return _font("AlegreyaSans-Medium.ttf", size)


def fit_font(font_for, text, max_width, size, min_size=10):
    """Font lớn nhất từ size trở xuống mà chữ vừa max_width, để mọi ngôn ngữ đều nằm trong khung."""
    font = font_for(size)
    while size > min_size and font.size(text)[0] > max_width:
        size -= 1
        font = font_for(size)
    return font
