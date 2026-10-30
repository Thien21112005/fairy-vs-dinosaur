import pygame

LINE_WIDTH = 2


def blit_wrapped(screen, image, x, y):
    """Vẽ nhân vật, và vẽ thêm phần tràn sang mép đối diện để trượt dần qua đường hầm."""
    screen.blit(image, (x, y))
    width = screen.get_width()
    if x < 0:
        screen.blit(image, (x + width, y))
    elif x + image.get_width() > width:
        screen.blit(image, (x - width, y))


def draw_arrow_head(screen, color, tip, udx, udy, size):
    """Vẽ đầu mũi tên tại tip, hướng theo vector (udx, udy)."""
    perp_x = -udy
    perp_y = udx
    base1 = (tip[0] - size * udx + (size / 2) * perp_x, tip[1] - size * udy + (size / 2) * perp_y)
    base2 = (tip[0] - size * udx - (size / 2) * perp_x, tip[1] - size * udy - (size / 2) * perp_y)
    pygame.draw.line(screen, color, tip, base1, LINE_WIDTH)
    pygame.draw.line(screen, color, tip, base2, LINE_WIDTH)
