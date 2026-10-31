"""Dựng sẵn nền mê cung từ các tile đã vẽ: lối đi sáng, lõi khối tường tối, tường đá cùng màu tiêu đề."""
import random

import pygame

from fairy_vs_dinosaur.ui.widgets import scale_pixel_art

WALLS = {3, 4, 5, 6, 7, 8, 9}
GHOST_HOUSE_CELL = (15, 15)
PLAYER_START_CELL = (24, 15)

# Dải màu đá từ tối tới sáng, lấy từ chữ FAIRY trên tranh nền
STONE_RAMP = [(0.0, (34, 28, 40)), (0.35, (96, 80, 90)), (0.7, (168, 146, 142)), (1.0, (236, 216, 192))]
FLOOR_TINT = (112, 214, 208)
FLOOR_LIFT = (6, 30, 36)
VOID_TINT = (30, 52, 60)
HOUSE_TINT = (120, 72, 62)
SHADOW_ALPHA = 170

MUSHROOM = ["..bbbb..", ".bbwbbb.", "bwbbbbwb", "bbbbwbbb", "..ssss..", "...ss...", "...ss..."]
CRYSTAL_SHARD = ["...w...", "..wcw..", "..ccc.w", ".wccwcc", ".cccccc", "..cccc."]
SPRITE_COLORS = {'b': (66, 118, 255), 'w': (176, 226, 255), 's': (150, 196, 224), 'c': (116, 230, 238)}
MOSS_COLORS = [(96, 136, 58), (136, 174, 72), (70, 104, 50)]
MOSS_CHANCE = 0.22


def _ramp_color(value):
    for (low, low_color), (high, high_color) in zip(STONE_RAMP, STONE_RAMP[1:]):
        if value <= high:
            ratio = (value - low) / (high - low)
            return [int(low_color[i] + (high_color[i] - low_color[i]) * ratio) for i in range(3)]
    return list(STONE_RAMP[-1][1])


def stone_tile(tile):
    """Tô lại tile tường theo dải màu đá, giữ nguyên hình pixel đã vẽ."""
    result = tile.copy()
    for x in range(tile.get_width()):
        for y in range(tile.get_height()):
            r, g, b, a = tile.get_at((x, y))
            if a:
                result.set_at((x, y), (*_ramp_color((r * 0.3 + g * 0.59 + b * 0.11) / 255), a))
    return result


def _reachable(board, start):
    """Các ô đi được từ start, có tính đường hầm hai bên mép."""
    rows, cols = len(board), len(board[0])
    seen = {start}
    stack = [start]
    while stack:
        r, c = stack.pop()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, (c + 1) % cols), (r, (c - 1) % cols)):
            if 0 <= nr < rows and (nr, nc) not in seen and board[nr][nc] not in WALLS:
                seen.add((nr, nc))
                stack.append((nr, nc))
    return seen


def _radial(size, color, strength):
    """Quầng sáng tròn dùng với BLEND_RGB_ADD."""
    small = pygame.Surface((64, 64))
    for radius in range(32, 0, -1):
        level = strength * (1 - radius / 32) ** 2
        pygame.draw.circle(small, [int(c * level) for c in color], (32, 32), radius)
    return pygame.transform.smoothscale(small, size)


def _pixel_sprite(rows, scale):
    sprite = pygame.Surface((len(rows[0]) * scale, len(rows) * scale), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, key in enumerate(row):
            if key != '.':
                sprite.fill(SPRITE_COLORS[key], (x * scale, y * scale, scale, scale))
    return sprite


def _lit_floor(brick, size):
    floor = pygame.transform.smoothscale(brick, size)
    floor.fill(FLOOR_TINT, special_flags=pygame.BLEND_RGB_MULT)
    floor.fill(FLOOR_LIFT, special_flags=pygame.BLEND_RGB_ADD)
    # Vệt sáng từ trên xuống ở giữa, như khoảng rừng sáng trong tranh nền
    shaft = _radial((size[0] * 3 // 2, size[1] * 3 // 2), (46, 118, 118), 1.0)
    floor.blit(shaft, shaft.get_rect(center=(size[0] // 2, size[1] // 4)), special_flags=pygame.BLEND_RGB_ADD)
    return floor


def _paint_cell_groups(floor, board, cell_w, cell_h):
    """Lõi khối tường và nhà khủng long tối hẳn đi, để nhìn vào là phân biệt được lối đi."""
    walkable = _reachable(board, PLAYER_START_CELL)
    house = _reachable(board, GHOST_HOUSE_CELL) - walkable
    voids = []
    for r, row in enumerate(board):
        for c, value in enumerate(row):
            rect = pygame.Rect(c * cell_w, r * cell_h, cell_w, cell_h)
            if (r, c) in house:
                floor.fill(HOUSE_TINT, rect, special_flags=pygame.BLEND_RGB_MULT)
            elif (r, c) not in walkable:
                floor.fill(VOID_TINT, rect, special_flags=pygame.BLEND_RGB_MULT)
                if value == 0:
                    voids.append((r, c))
    return voids


def _plant_voids(floor, voids, cell_w, cell_h, rng):
    """Nấm và pha lê phát sáng ở các khoảng trống lớn, lấy từ khu rừng trong tranh nền."""
    open_cells = set(voids)
    wide = [cell for cell in voids if all((cell[0], cell[1] + i) in open_cells for i in range(3))]
    rng.shuffle(wide)
    taken = []
    for r, c in wide:
        if len(taken) >= 10:
            break
        if any(abs(r - other_r) < 2 and abs(c - other_c) < 3 for other_r, other_c in taken):
            continue
        taken.append((r, c))
        rows = MUSHROOM if rng.random() < 0.6 else CRYSTAL_SHARD
        sprite = _pixel_sprite(rows, 2)
        x = c * cell_w + rng.randint(4, 2 * cell_w)
        y = r * cell_h + cell_h - sprite.get_height() // 2
        glow = _radial((sprite.get_width() * 3, sprite.get_height() * 3), SPRITE_COLORS['c'], 0.34)
        floor.blit(glow, glow.get_rect(center=sprite.get_rect(topleft=(x, y)).center),
                   special_flags=pygame.BLEND_RGB_ADD)
        floor.blit(sprite, (x, y))


def _wall_layer(board, tiles, size, cell_w, cell_h, rng):
    layer = pygame.Surface(size, pygame.SRCALPHA)
    for r, row in enumerate(board):
        for c, value in enumerate(row):
            if value in WALLS:
                x, y = c * cell_w, r * cell_h
                layer.blit(tiles[value - 1], (x, y))
                if value != 9 and rng.random() < MOSS_CHANCE:
                    _moss_tuft(layer, x, y, cell_w, cell_h, rng)
    return layer


def _moss_tuft(layer, x, y, cell_w, cell_h, rng):
    """Vài chấm rêu trên phần đá có sẵn của tile, như dây leo bám quanh chữ tiêu đề."""
    for _ in range(rng.randint(3, 6)):
        px, py = x + rng.randrange(cell_w - 2), y + rng.randrange(cell_h - 2)
        if layer.get_at((px, py))[3] > 128:
            layer.fill(rng.choice(MOSS_COLORS), (px, py, 2, 2))


def _drop_shadow(wall_layer):
    """Bóng tường đổ xuống lối đi, làm tường nổi khối so với sàn."""
    mask = pygame.mask.from_surface(wall_layer).to_surface(setcolor=(0, 0, 0, SHADOW_ALPHA), unsetcolor=(0, 0, 0, 0))
    width, height = mask.get_size()
    small = pygame.transform.smoothscale(mask, (width // 3, height // 3))
    return pygame.transform.smoothscale(small, (width, height))


def build_board_surface(brick, board, tiles, size, cell_w, cell_h):
    """Sàn, lõi khối, bóng đổ và tường gộp thành một ảnh tĩnh, chỉ dựng một lần."""
    rng = random.Random(11)  # Trang trí cố định, không đổi giữa các lần chơi
    floor = _lit_floor(brick, size)
    voids = _paint_cell_groups(floor, board, cell_w, cell_h)
    _plant_voids(floor, voids, cell_w, cell_h, rng)
    walls = _wall_layer(board, tiles, size, cell_w, cell_h, rng)
    floor.blit(_drop_shadow(walls), (2, 4))
    floor.blit(walls, (0, 0))
    return floor


def build_glow_frames(size, color, count=8):
    """Các mức sáng của quầng hạt năng lượng, để nhịp đập không phải dựng lại mỗi khung hình."""
    return [_radial(size, color, 0.45 + 0.55 * i / (count - 1)) for i in range(count)]


def scale_tiles(raw_tiles, size):
    """Tile hạt và cổng giữ màu gốc, tile tường đổi sang màu đá."""
    return [scale_pixel_art(stone_tile(tile) if i + 1 in WALLS and i + 1 != 9 else tile, size)
            for i, tile in enumerate(raw_tiles)]
