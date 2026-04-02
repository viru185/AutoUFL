from __future__ import annotations

import argparse

from src.clients import ExcelProcessor
from src.clients.base_processor import ProcessResult
from src.config import DEFAULT_INPUT_FOLDER, DEFAULT_OUTPUT_FOLDER
from src.meta import get_authot_details, get_version
from src.watcher import FolderWatcher


def app():

    processor = ExcelProcessor()

    watcher = FolderWatcher(
        folder=DEFAULT_INPUT_FOLDER,
        output_dir=DEFAULT_OUTPUT_FOLDER,
        processor=processor,
    )

    watcher.start()
    # your actual app logic goes here


def main():
    parser = argparse.ArgumentParser(description="My Simple CLI Tool")

    # will be handle by the argparse
    parser.add_argument("--version", action="version", version=f"{get_version()}")

    parser.add_argument("--author", action="store_true", help="Show author information")

    args = parser.parse_args()

    # If --author is passed
    if args.author:
        details = get_authot_details()
        for key, value in details.items():
            print(f"{key:<10} : {value}")
        return

    # Default behavior (no args)
    app()


if __name__ == "__main__":
    main()
