import io

import matplotlib
import pygame

# Backend giao diện (TkAgg) đổi DPI awareness của cả tiến trình, làm cửa sổ game nhảy vị trí và đổi kích thước
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

METRICS = ['execution_time', 'expanded_nodes', 'path_length', 'success_rate']
METRIC_NAMES = ['Execution Time (s)', 'Expanded Nodes', 'Path Length', 'Success Rate (%)']
BAR_COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54a0ff']


def _bar_label(metric, value):
    if metric == 'success_rate':
        return f'{value:.1f}%'
    if metric == 'execution_time':
        return f'{value:.3f}'
    return f'{value:.0f}'


def render_comparison_chart(df):
    """Vẽ biểu đồ so sánh các thuật toán, trả về pygame Surface."""
    plt.style.use('dark_background')
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor='#1a1a2e')
    fig.suptitle('Algorithm Performance', color='white', fontsize=16, fontweight='bold', y=0.95)

    grouped = df.groupby('algorithm')[METRICS].mean().reset_index()
    algorithms = grouped['algorithm'].tolist()

    for i, (metric, metric_name) in enumerate(zip(METRICS, METRIC_NAMES)):
        ax = axes[i // 2, i % 2]
        bars = ax.bar(algorithms, grouped[metric], color=BAR_COLORS[:len(algorithms)], alpha=0.8)

        ax.set_title(metric_name, color='white', fontweight='bold', fontsize=12)
        ax.set_ylabel(metric_name, color='white', fontsize=10)
        ax.tick_params(axis='x', rotation=45, colors='white', labelsize=9)
        ax.tick_params(axis='y', colors='white', labelsize=9)
        ax.grid(True, alpha=0.3, color='gray')
        ax.set_facecolor('#2a2a4a')

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2., height, _bar_label(metric, height),
                        ha='center', va='bottom', fontsize=8, color='white', fontweight='bold')

    plt.tight_layout(rect=[0, 0, 1, 0.93])

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e', edgecolor='none')
    buf.seek(0)
    image = pygame.image.load(buf)
    plt.close()
    return image
