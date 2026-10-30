from fairy_vs_dinosaur.i18n.translations import translations
from fairy_vs_dinosaur.settings_store import get_language


def get_translation(key):
    return translations.get(get_language(), translations["English"]).get(key, key)
