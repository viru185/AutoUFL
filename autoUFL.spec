# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

CLIENT = os.getenv("AUTO_UFL_BUILD_TARGET", "all").lower()
MANIFEST_FILE = Path("build") / "client_manifest.json"

if not MANIFEST_FILE.exists():
    raise SystemExit("Missing build/client_manifest.json. Run build.py before invoking PyInstaller.")


def collect_client_modules():
    base = Path("src/clients")
    modules = []

    for client_dir in base.iterdir():
        if client_dir.is_dir() and not client_dir.name.startswith("__"):
            modules.append(f"src.clients.{client_dir.name}.processor")

    return sorted(modules)


all_client_modules = collect_client_modules()

if CLIENT == "all":
    hiddenimports = all_client_modules
else:
    target_module = f"src.clients.{CLIENT}.processor"
    if target_module not in all_client_modules:
        raise SystemExit(f"Client '{CLIENT}' does not exist or lacks a processor.py")
    hiddenimports = [target_module]


a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        ('pyproject.toml', '.'),
        (str(MANIFEST_FILE), 'src'),
    ],
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
