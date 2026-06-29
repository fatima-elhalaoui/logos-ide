#!/usr/bin/env python3
"""Launch Logos IDE.

This is the friendly entry point. From a checkout:

    python run_logos.py

It makes sure the application package is importable and starts the GUI.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main  # noqa: E402

if __name__ == "__main__":
    main()
