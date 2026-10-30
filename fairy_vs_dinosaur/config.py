import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "game_settings.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

os.makedirs(DATA_DIR, exist_ok=True)


def asset(relative_path):
    """Absolute path of a file inside assets/, independent of the working directory."""
    return os.path.join(ASSETS_DIR, relative_path)
