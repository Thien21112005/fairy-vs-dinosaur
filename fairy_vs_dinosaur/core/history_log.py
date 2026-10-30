import json
import os
from datetime import datetime

from fairy_vs_dinosaur.config import HISTORY_FILE


def new_metrics():
    return {
        'execution_time': 0.0,  # Tổng thời gian tìm đường (giây)
        'expanded_nodes': 0,  # Tổng số nút đã mở rộng
        'path_length': 0,  # Số ô nhân vật thực sự đã đi
        'memory_usage': 0,  # Ước lượng cao nhất (KB)
        'calls': 0
    }


def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (OSError, ValueError) as e:
        print(f"Error loading history: {e}")
    return []


def append_history(algorithm, level, metrics, success, play_time_ms, score):
    entry = {
        'timestamp': datetime.now().isoformat(),
        'algorithm': algorithm,
        'level': level,
        'execution_time': metrics['execution_time'],
        'expanded_nodes': metrics['expanded_nodes'],
        'path_length': metrics['path_length'],
        'memory_usage': metrics['memory_usage'],
        'success_rate': 100 if success else 0,
        'total_time': play_time_ms / 1000.0,
        'score': score
    }

    history = load_history()
    history.append(entry)
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
    except OSError as e:
        print(f"Error saving history: {e}")


def clear_history():
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
    except OSError as e:
        print(f"Error clearing history: {e}")
