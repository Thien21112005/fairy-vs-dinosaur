import pygame

LINE_WIDTH = 2


def draw_arrow_head(screen, color, tip, udx, udy, size):
    """Vẽ đầu mũi tên tại tip, hướng theo vector (udx, udy)."""
    perp_x = -udy
    perp_y = udx
    base1 = (tip[0] - size * udx + (size / 2) * perp_x, tip[1] - size * udy + (size / 2) * perp_y)
    base2 = (tip[0] - size * udx - (size / 2) * perp_x, tip[1] - size * udy - (size / 2) * perp_y)
    pygame.draw.line(screen, color, tip, base1, LINE_WIDTH)
    pygame.draw.line(screen, color, tip, base2, LINE_WIDTH)
