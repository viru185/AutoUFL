# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

CLIENT = os.getenv("AUTO_UFL_CLIENT_ENV")

def collect_client_modules():
    base = Path("src/clients")
    modules = []

    for client_dir in base.iterdir():
        if client_dir.is_dir() and not client_dir.name.startswith("__"):
            modules.append(f"src.clients.{client_dir.name}.processor")
    return modules


if CLIENT == "all":
    hiddenimports = collect_client_modules()
else:
    hiddenimports = [
    f"src.clients.{CLIENT}.processor",
    ]


a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[('pyproject.toml', '.')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['jinja2'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='autoUFL',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)