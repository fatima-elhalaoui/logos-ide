"""
User configuration: load / save / defaults.

Settings live in the per-user data directory (not in the source tree) so they
persist across upgrades and packaged builds. The i18n string tables now live in
:mod:`core.i18n`; this module re-exports :data:`UI_STRINGS` for backward
compatibility.
"""

import json

from core.data_paths import settings_path
from core.i18n import UI_STRINGS, get_strings  # noqa: F401 (re-exported)
from core.logger import get_logger

log = get_logger(__name__)

DEFAULT_SETTINGS = {
    "language": "es",                 # "es" or "en"
    "pronunciation_scheme": "erasmian",  # erasmian | modern | restored-attic
    "speech_rate": None,              # None = use screen reader's own rate
    "auto_speak_words": False,        # speak phonetics on word completion
    "exam_mode": False,               # disables study aids (ethical exam use)
    "font_point_size": 14,            # editor font size (low-vision support)
    "show_dictionary_panel": True,
}


def load_settings():
    path = settings_path()
    settings = DEFAULT_SETTINGS.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            user = json.load(f)
        if isinstance(user, dict):
            for k, v in user.items():
                settings[k] = v
    except FileNotFoundError:
        pass
    except Exception as e:
        log.warning("Could not load settings (%s); using defaults.", e)
    # Ensure every default key exists.
    for k, v in DEFAULT_SETTINGS.items():
        settings.setdefault(k, v)
    return settings


def save_settings(settings):
    try:
        with open(settings_path(), "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log.error("Could not save settings: %s", e)
