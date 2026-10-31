import pygame

from fairy_vs_dinosaur.ui import theme
from fairy_vs_dinosaur.ui.theme import body_font, label_font, strong_font
from fairy_vs_dinosaur.ui.widgets import draw_text

HEADERS = ['ALGORITHM', 'TIME(s)', 'NODES', 'PATH', 'MEMORY', 'SUCCESS%', 'TOTAL(s)']
METRICS = ['execution_time', 'expanded_nodes', 'path_length', 'memory_usage', 'success_rate', 'total_time']
ROW_HEIGHT = 32
STATS_HEIGHT = 44
TOP_OFFSET = 62
SIDE_PADDING = 24
FIRST_COLUMN_WIDTH = 216

SUCCESS_GOOD = (176, 222, 104)
SUCCESS_MIXED = theme.FLAME
SUCCESS_POOR = (255, 138, 116)


def table_height(row_count):
    return TOP_OFFSET + (1 + row_count) * ROW_HEIGHT + STATS_HEIGHT


def _format_cell(column, value):
    if column == 'success_rate':
        if value >= 80:
            color = SUCCESS_GOOD
        elif value >= 50:
            color = SUCCESS_MIXED
        else:
            color = SUCCESS_POOR
        return f"{value:.1f}%", color
    if column in ['execution_time', 'total_time']:
        return f"{value:.3f}", theme.PARCHMENT
    return f"{value:.0f}", theme.PARCHMENT


def _column_right(index, x, width):
    """Mép phải của cột số. Số canh phải để so sánh theo hàng đơn vị."""
    column_width = (width - FIRST_COLUMN_WIDTH) // (len(HEADERS) - 1)
    return x + FIRST_COLUMN_WIDTH + index * column_width


def _draw_headers(screen, x, y, width):
    center_y = y + ROW_HEIGHT // 2
    draw_text(screen, HEADERS[0], label_font(16), theme.COPPER_LIGHT, midleft=(x, center_y))
    for i, header in enumerate(HEADERS[1:], start=1):
        draw_text(screen, header, label_font(16), theme.COPPER_LIGHT, midright=(_column_right(i, x, width), center_y))
    pygame.draw.line(screen, theme.COPPER, (x, y + ROW_HEIGHT - 1), (x + width, y + ROW_HEIGHT - 1))


def _draw_rows(screen, grouped, x, y, width):
    font = body_font(18)
    for row_idx, (_, row) in enumerate(grouped.iterrows()):
        top = y + (row_idx + 1) * ROW_HEIGHT
        center_y = top + ROW_HEIGHT // 2
        draw_text(screen, str(row['algorithm']), strong_font(17), theme.CRYSTAL, midleft=(x, center_y))
        for col_idx, column in enumerate(METRICS, start=1):
            value, color = _format_cell(column, row[column])
            draw_text(screen, value, font, color, midright=(_column_right(col_idx, x, width), center_y))
        pygame.draw.line(screen, theme.HAIRLINE, (x, top + ROW_HEIGHT - 1), (x + width, top + ROW_HEIGHT - 1))


def draw_summary_table(screen, panel, df):
    """Bảng trung bình theo thuật toán và dòng thống kê tổng quan bên dưới."""
    grouped = df.groupby('algorithm')[METRICS].mean().reset_index()
    x = panel.x + SIDE_PADDING
    y = panel.y + TOP_OFFSET
    width = panel.width - 2 * SIDE_PADDING

    _draw_headers(screen, x, y, width)
    _draw_rows(screen, grouped, x, y, width)

    best_algorithm = grouped.loc[grouped['success_rate'].idxmax(), 'algorithm']
    stats = (f"Games: {len(df)}     Algorithms: {df['algorithm'].nunique()}     "
             f"Best: {best_algorithm} ({grouped['success_rate'].max():.1f}%)")
    draw_text(screen, stats, body_font(18), theme.MIST, midleft=(x, panel.bottom - STATS_HEIGHT // 2 - 2))
