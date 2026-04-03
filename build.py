import os
import shutil
import subprocess

clients = ["utkal", "renukoot", "all"]

for client in clients:
    print(f"Building for {client}...")

    os.environ["AUTO_UFL_CLIENT_ENV"] = client

    subprocess.run(["uv", "run", "pyinstaller", "autoUFL.spec", "--clean"])

    shutil.move("dist/autoUFL.exe", f"dist/autoUFL_{client}.exe")

