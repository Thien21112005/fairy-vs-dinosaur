import json
import os

from fairy_vs_dinosaur.config import SETTINGS_FILE

DEFAULT_SETTINGS = {
    "music_volume": 0.8,
    "sfx_volume": 0.8,
    "music_enabled": True,
    "sfx_enabled": True,
    "control_scheme": "Arrow Keys",
    "language": "English",
}


def load_settings():
    """Đọc settings từ file, gộp với giá trị mặc định rồi ghi lại để bổ sung key còn thiếu."""
    settings = DEFAULT_SETTINGS.copy()
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings.update(json.load(f))
    except (OSError, ValueError) as e:
        print(f"Lỗi khi load settings: {e}")
    save_settings(settings)
    return settings


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    except OSError as e:
        print(f"Không thể lưu settings: {e}")
