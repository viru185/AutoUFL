from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
CLIENTS_DIR = PROJECT_ROOT / "src" / "clients"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
MANIFEST_PATH = BUILD_DIR / "client_manifest.json"


def discover_clients() -> list[str]:
    clients = []
    for child in CLIENTS_DIR.iterdir():
        if not child.is_dir() or child.name.startswith("__"):
            continue
        if (child / "processor.py").exists():
            clients.append(child.name.lower())
    return sorted(clients)


def write_manifest(enabled_clients: list[str], default_client: str | None, multi_client: bool) -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "enabled_clients": enabled_clients,
        "default_client": default_client,
        "multi_client": multi_client,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))


def build_for_target(target: str, all_clients: list[str]) -> None:
    print(f"Building for {target}...")

    if target == "all":
        enabled = all_clients
        default = all_clients[0] if all_clients else None
        multi = True
    else:
        enabled = [target]
        default = target
        multi = False

    if not enabled:
        raise RuntimeError("No clients discovered. Cannot continue build.")

    write_manifest(enabled, default, multi)

    env = os.environ.copy()
    env["AUTO_UFL_BUILD_TARGET"] = target

    subprocess.run(["uv", "run", "pyinstaller", "autoUFL.spec", "--clean"], check=True, env=env)

    src_exe = DIST_DIR / "autoUFL.exe"
    dst_exe = DIST_DIR / f"autoUFL_{target}.exe"
    if dst_exe.exists():
        dst_exe.unlink()
    shutil.move(src_exe, dst_exe)


def main() -> None:
    clients = discover_clients()
    targets = clients + ["all"]

    for target in targets:
        build_for_target(target, clients)


if __name__ == "__main__":
    main()

