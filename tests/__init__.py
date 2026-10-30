"""Test setup: run pygame without a window or audio device, and keep test data out of the real data/ folder."""
import os
import tempfile
import warnings

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["FAIRY_DATA_DIR"] = tempfile.mkdtemp(prefix="fairy_tests_")

warnings.filterwarnings("ignore", category=UserWarning, module="pygame")
