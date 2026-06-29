"""Centralised, rotating logging for Logos IDE.

Logs go to the per-user data directory so a packaged (PyInstaller) build can
write them without needing write access to its install folder.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from core.data_paths import user_log_dir

_CONFIGURED = False


def setup_logging(level: int = logging.INFO) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True

    log_dir = user_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "logos.log")

    handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s  %(levelname)-7s  %(name)s: %(message)s")
    )

    root = logging.getLogger("logos")
    root.setLevel(level)
    root.addHandler(handler)
    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``logos`` namespace."""
    setup_logging()
    short = name.split(".")[-1]
    return logging.getLogger(f"logos.{short}")
