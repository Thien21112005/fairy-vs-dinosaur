import ast
import builtins
import json
import os
import unittest

import pygame

from fairy_vs_dinosaur import settings_store
from fairy_vs_dinosaur.config import PROJECT_ROOT, SETTINGS_FILE
from fairy_vs_dinosaur.i18n import get_translation
from fairy_vs_dinosaur.i18n.translations import translations
from fairy_vs_dinosaur.ui.screens.about import AboutMenu
from fairy_vs_dinosaur.ui.screens.history import HistoryMenu
from fairy_vs_dinosaur.ui.screens.main_menu import MainMenu
from fairy_vs_dinosaur.ui.screens.settings import SettingsMenu


class TranslationTest(unittest.TestCase):
    def test_every_language_has_every_key(self):
        english = set(translations["English"])
        for language, table in translations.items():
            self.assertEqual(set(table) ^ english, set(), language)

    def test_every_key_used_in_code_exists(self):
        used = set()
        for root, _, files in os.walk(os.path.join(PROJECT_ROOT, "fairy_vs_dinosaur")):
            for name in files:
                if name.endswith(".py"):
                    with open(os.path.join(root, name), encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "get_translation" \
                                and isinstance(node.args[0], ast.Constant):
                            used.add(node.args[0].value)
                        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "TITLE_KEY" \
                                and node.value.value:
                            used.add(node.value.value)
        self.assertEqual(used - set(translations["English"]), set())

    def test_lookup_does_not_read_the_disk(self):
        get_translation("ready")
        real_open = builtins.open

        def fail(*args, **kwargs):
            raise AssertionError("get_translation must not open files")

        builtins.open = fail
        try:
            get_translation("ready")
        finally:
            builtins.open = real_open


class SettingsStoreTest(unittest.TestCase):
    def test_missing_keys_get_defaults(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"music_volume": 0.1}, f)
        settings = settings_store.load_settings()
        self.assertEqual(settings["music_volume"], 0.1)
        self.assertEqual(settings["control_scheme"], "Arrow Keys")

    def test_corrupt_file_falls_back_to_defaults(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            f.write("{not json")
        self.assertEqual(settings_store.load_settings(), settings_store.DEFAULT_SETTINGS)

    def test_unsupported_values_are_replaced(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"language": "Japanese", "control_scheme": "Mouse"}, f)
        settings = settings_store.load_settings()
        self.assertEqual(settings["language"], "English")
        self.assertEqual(settings["control_scheme"], "Arrow Keys")

    def test_saving_changes_the_language_in_use(self):
        settings = settings_store.load_settings()
        settings["language"] = "Vietnamese"
        settings_store.save_settings(settings)
        self.assertEqual(get_translation("yes"), translations["Vietnamese"]["yes"])
        settings["language"] = "English"
        settings_store.save_settings(settings)


class ScreensTest(unittest.TestCase):
    def test_all_screens_draw(self):
        menu = MainMenu()
        menu._draw()
        about = AboutMenu(menu.screen, menu.sound_manager, menu.background)
        about.draw_content()
        about.draw_back_button()
        history = HistoryMenu(menu.screen, menu.sound_manager, menu.background)
        history.draw_title()
        history.draw_table()
        history.draw_buttons()
        SettingsMenu(menu.screen, menu.sound_manager, menu.background).draw()

    def test_menu_loop_exits_cleanly_on_quit(self):
        menu = MainMenu()
        pygame.event.clear()
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.assertFalse(menu.handle_events())


class ProjectLayoutTest(unittest.TestCase):
    def test_works_from_another_working_directory(self):
        previous = os.getcwd()
        os.chdir(os.path.dirname(PROJECT_ROOT))
        try:
            MainMenu()
        finally:
            os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
