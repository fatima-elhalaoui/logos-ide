# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller build spec for Logos IDE.

Build:
    pip install pyinstaller
    pyinstaller logos.spec

Produces dist/LogosIDE/LogosIDE(.exe). If the full dictionary
db/logos_dict.db is present at build time it is bundled into the release;
otherwise only the seed dictionary ships and the app downloads/uses the data
pack at runtime.
"""

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None
ROOT = os.path.abspath(".")

datas = [
    ("db/logos_dict.seed.db", "db"),
    ("core/data", "core/data"),
    ("docs", "docs"),
    ("README.md", "."),
    ("README.es.md", "."),
    ("LICENSE", "."),
]

# Bundle the full dictionary into the release if it has been built locally.
_full_db = os.path.join(ROOT, "db", "logos_dict.db")
if os.path.exists(_full_db):
    datas.append(("db/logos_dict.db", "db"))

# accessible_output2 ships screen-reader client DLLs as package data.
datas += collect_data_files("accessible_output2")

hiddenimports = [
    "accessible_output2",
    "accessible_output2.outputs.auto",
    "accessible_output2.outputs.nvda",
    "accessible_output2.outputs.jaws",
    "accessible_output2.outputs.sapi5",
    "accessible_output2.outputs.window_eyes",
    "accessible_output2.outputs.system_access",
    "pyttsx3.drivers",
    "pyttsx3.drivers.sapi5",
    "comtypes",
    "win32com",
    "win32com.client",
]

a = Analysis(
    ["run_logos.py"],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LogosIDE",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # GUI app: no console window
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="LogosIDE",
)
