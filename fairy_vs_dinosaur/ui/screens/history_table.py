import pygame

HEADERS = ['ALGORITHM', 'TIME(s)', 'NODES', 'PATH', 'MEMORY', 'SUCCESS%', 'TOTAL(s)']
METRICS = ['execution_time', 'expanded_nodes', 'path_length', 'memory_usage', 'success_rate', 'total_time']
ROW_HEIGHT = 36


def _format_cell(column, value, colors):
    if column == 'algorithm':
        return str(value), colors['accent_light']
    if column == 'success_rate':
        if value >= 80:
            color = colors['success']
        elif value >= 50:
            color = colors['warning']
        else:
            color = colors['error']
        return f"{value:.1f}%", color
    if column in ['execution_time', 'total_time']:
        return f"{value:.3f}", colors['text_primary']
    return f"{value:.0f}", colors['text_primary']


def _draw_headers(screen, x, y, col_width, font, colors):
    for i, header in enumerate(HEADERS):
        cell = pygame.Rect(x + i * col_width, y, col_width, ROW_HEIGHT)
        for y_pos in range(ROW_HEIGHT):
            ratio = y_pos / ROW_HEIGHT
            color = (int(70 + (40 - 70) * ratio), int(130 + (60 - 130) * ratio), int(255 + (80 - 255) * ratio))
            pygame.draw.line(screen, color, (cell.x, cell.y + y_pos), (cell.right, cell.y + y_pos))
        pygame.draw.rect(screen, colors['border'], cell, 1)
        text = font.render(header, True, colors['text_primary'])
        screen.blit(text, text.get_rect(center=cell.center))


def _draw_rows(screen, grouped, x, y, col_width, font, colors):
    for row_idx, (_, row) in enumerate(grouped.iterrows()):
        y_pos = y + (row_idx + 1) * ROW_HEIGHT
        row_color = colors['row_even'] if row_idx % 2 == 0 else colors['row_odd']
        pygame.draw.rect(screen, row_color, pygame.Rect(x, y_pos, col_width * len(HEADERS), ROW_HEIGHT))

        for col_idx, column in enumerate(['algorithm'] + METRICS):
            cell = pygame.Rect(x + col_idx * col_width, y_pos, col_width, ROW_HEIGHT)
            pygame.draw.rect(screen, colors['border'], cell, 1)
            value, color = _format_cell(column, row[column], colors)
            text = font.render(value, True, color)
            screen.blit(text, text.get_rect(center=cell.center))


def draw_summary_table(screen, panel, df, table_font, stats_font, colors):
    """Bảng trung bình theo thuật toán và dòng thống kê tổng quan bên dưới."""
    grouped = df.groupby('algorithm')[METRICS].mean().reset_index()
    x = panel.x + 15
    y = panel.y + 70
    col_width = (panel.width - 30) // len(HEADERS)

    _draw_headers(screen, x, y, col_width, table_font, colors)
    _draw_rows(screen, grouped, x, y, col_width, table_font, colors)

    best_algorithm = grouped.loc[grouped['success_rate'].idxmax(), 'algorithm']
    stats = [
        f"Games: {len(df)}",
        f"Algorithms: {df['algorithm'].nunique()}",
        f"Best: {best_algorithm} ({grouped['success_rate'].max():.1f}%)"
    ]
    for i, text in enumerate(stats):
        screen.blit(stats_font.render(text, True, colors['accent_light']), (x + i * 220, panel.bottom - 45))
