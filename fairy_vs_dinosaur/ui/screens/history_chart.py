import io

import matplotlib
import pygame

# Backend giao diện (TkAgg) đổi DPI awareness của cả tiến trình, làm cửa sổ game nhảy vị trí và đổi kích thước
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

from fairy_vs_dinosaur.config import asset  # noqa: E402
from fairy_vs_dinosaur.ui import theme  # noqa: E402

METRICS = ['execution_time', 'expanded_nodes', 'path_length', 'success_rate']
METRIC_NAMES = ['Execution Time (s)', 'Expanded Nodes', 'Path Length', 'Success Rate (%)']
CHART_DPI = 100
ROW_HEIGHT_PX = 24
CHART_PADDING_PX = 76  # Tiêu đề và khoảng cách của mỗi hàng biểu đồ

_fonts_registered = False


def _hex(color):
    return '#{:02x}{:02x}{:02x}'.format(*color)


def _register_fonts():
    global _fonts_registered
    if not _fonts_registered:
        for name in ["AlegreyaSans-Medium.ttf", "AlegreyaSC-Bold.ttf"]:
            font_manager.fontManager.addfont(asset(f"fonts/{name}"))
        _fonts_registered = True


def _bar_label(metric, value):
    if metric == 'success_rate':
        return f'{value:.1f}%'
    if metric == 'execution_time':
        return f'{value:.3f}'
    return f'{value:.0f}'


def _draw_metric(ax, algorithms, metric, metric_name, values):
    """Cột ngang một màu: tên thuật toán đã nằm trên trục, màu không cần mang thêm nghĩa nào."""
    ax.barh(algorithms, values, height=0.62, color=_hex(theme.CRYSTAL))
    ax.invert_yaxis()  # Cùng thứ tự từ trên xuống ở cả bốn biểu đồ, để so sánh theo hàng

    largest = max(values) if max(values) > 0 else 1
    ax.set_xlim(0, largest * 1.22)
    for row, value in enumerate(values):
        ax.text(value + largest * 0.02, row, _bar_label(metric, value), va='center', ha='left', fontsize=11,
                color=_hex(theme.PARCHMENT), fontfamily='Alegreya Sans')

    ax.set_title(metric_name, loc='left', pad=8, fontsize=14, color=_hex(theme.COPPER_LIGHT), fontfamily='Alegreya SC',
                 fontweight='bold')
    ax.xaxis.set_visible(False)
    ax.tick_params(axis='y', length=0, labelsize=11, labelcolor=_hex(theme.MIST), pad=6)
    for label in ax.get_yticklabels():
        label.set_fontfamily('Alegreya Sans')
    for side, spine in ax.spines.items():
        spine.set_visible(side == 'left')
    ax.spines['left'].set_color(_hex(theme.HAIRLINE))
    ax.set_facecolor('none')


def render_comparison_chart(df, width=860):
    """Vẽ biểu đồ so sánh các thuật toán đúng kích thước hiển thị, trả về pygame Surface nền trong suốt."""
    _register_fonts()
    grouped = df.groupby('algorithm')[METRICS].mean().reset_index()
    algorithms = grouped['algorithm'].tolist()

    height = 2 * (len(algorithms) * ROW_HEIGHT_PX + CHART_PADDING_PX)
    fig, axes = plt.subplots(2, 2, figsize=(width / CHART_DPI, height / CHART_DPI), dpi=CHART_DPI,
                             layout='constrained')
    fig.patch.set_alpha(0)
    fig.get_layout_engine().set(w_pad=0.2, h_pad=0.14)

    for i, (metric, metric_name) in enumerate(zip(METRICS, METRIC_NAMES)):
        _draw_metric(axes[i // 2, i % 2], algorithms, metric, metric_name, grouped[metric].tolist())

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=CHART_DPI, transparent=True)
    plt.close(fig)
    buf.seek(0)
    return pygame.image.load(buf)
