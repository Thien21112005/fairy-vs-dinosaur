import json
import os

from fairy_vs_dinosaur.config import SETTINGS_FILE

CONTROL_SCHEMES = ["Arrow Keys", "WASD", "Mixed"]
LANGUAGES = ["English", "Vietnamese", "French", "Spanish"]

DEFAULT_SETTINGS = {
    "music_volume": 0.8,
    "sfx_volume": 0.8,
    "music_enabled": True,
    "sfx_enabled": True,
    "control_scheme": "Arrow Keys",
    "language": "English",
}


_current_language = None


def get_language():
    """Ngôn ngữ đang dùng, chỉ đọc file ở lần đầu để có thể gọi trong mỗi khung hình."""
    if _current_language is None:
        load_settings()
    return _current_language


def load_settings():
    """Đọc settings từ file, gộp với giá trị mặc định rồi ghi lại để bổ sung key còn thiếu."""
    settings = DEFAULT_SETTINGS.copy()
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings.update(json.load(f))
    except (OSError, ValueError) as e:
        print(f"Lỗi khi load settings: {e}")
    # File cũ hoặc sửa tay có thể chứa giá trị menu không hỗ trợ
    if settings["control_scheme"] not in CONTROL_SCHEMES:
        settings["control_scheme"] = DEFAULT_SETTINGS["control_scheme"]
    if settings["language"] not in LANGUAGES:
        settings["language"] = DEFAULT_SETTINGS["language"]
    save_settings(settings)
    return settings


def save_settings(settings):
    global _current_language
    _current_language = settings["language"]
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    except OSError as e:
        print(f"Không thể lưu settings: {e}")
