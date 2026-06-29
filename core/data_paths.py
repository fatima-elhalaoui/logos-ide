"""
Resolve where Logos IDE reads and writes data.

The dictionary database is ~300 MB, far too large to live inside the git
repository (GitHub rejects files over 100 MB). It is therefore distributed
either bundled inside the packaged application or as a downloadable data pack
placed in the per-user data directory. A small *seed* database ships with the
source so the app is usable immediately after a `git clone`.

Resolution order for the main dictionary DB:
    1. $LOGOS_DB                                  (explicit override)
    2. <user data dir>/logos_dict.db              (downloaded full pack)
    3. <source>/db/logos_dict.db                  (dev checkout / bundled)
    4. <source>/db/logos_dict.seed.db             (tiny seed, always present)

User-writable data (settings, study DB, logs) always lives in the per-user
data directory so packaged builds never write inside Program Files.
"""

import os
import sys

try:
    from platformdirs import user_data_dir as _pd_user_data_dir
    from platformdirs import user_log_dir as _pd_user_log_dir
except Exception:  # pragma: no cover - platformdirs is a hard dependency
    _pd_user_data_dir = None
    _pd_user_log_dir = None

APP_NAME = "LogosIDE"
APP_AUTHOR = "LogosIDE"

# Directory that contains this source tree (…/LogosIDE).
_SOURCE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def source_root() -> str:
    """Root of the application source / bundle."""
    if getattr(sys, "frozen", False):
        # PyInstaller: bundled data sits next to the executable / in _MEIPASS.
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return _SOURCE_ROOT


def user_data_dir() -> str:
    if _pd_user_data_dir:
        d = _pd_user_data_dir(APP_NAME, APP_AUTHOR)
    else:
        d = os.path.join(os.path.expanduser("~"), ".logos_ide")
    os.makedirs(d, exist_ok=True)
    return d


def user_log_dir() -> str:
    if _pd_user_log_dir:
        return _pd_user_log_dir(APP_NAME, APP_AUTHOR)
    return os.path.join(user_data_dir(), "logs")


def settings_path() -> str:
    """Per-user settings file (kept out of git)."""
    return os.path.join(user_data_dir(), "settings.json")


def study_db_path() -> str:
    """Per-user database holding annotations, flashcards and history."""
    return os.path.join(user_data_dir(), "logos_study.db")


def _candidate_dictionary_paths():
    env = os.environ.get("LOGOS_DB")
    if env:
        yield env
    yield os.path.join(user_data_dir(), "logos_dict.db")
    yield os.path.join(source_root(), "db", "logos_dict.db")
    yield os.path.join(source_root(), "db", "logos_dict.seed.db")


def dictionary_db_path() -> str:
    """Return the best available dictionary DB path (first that exists).

    Falls back to the seed path even if it does not yet exist, so callers always
    receive a concrete path they can report to the user.
    """
    fallback = None
    for path in _candidate_dictionary_paths():
        if fallback is None:
            fallback = path
        if path and os.path.exists(path):
            return path
    return os.path.join(source_root(), "db", "logos_dict.seed.db")


def using_seed_database() -> bool:
    """True when only the tiny seed DB is available (full pack not installed)."""
    return dictionary_db_path().endswith("logos_dict.seed.db")
