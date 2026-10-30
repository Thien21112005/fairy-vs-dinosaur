import json
import os

from fairy_vs_dinosaur.i18n.translations import translations


def get_translation(key):
    settings_file = "game_settings.json"
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    else:
        settings = {"language": "English"}
    lang = settings.get("language", "English")
    return translations.get(lang, translations["English"]).get(key, key)
