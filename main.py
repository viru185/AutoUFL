from __future__ import annotations

import argparse

from src.clients import get_processor_class, list_available_clients
from src.clients.base_processor import ProcessResult
from src.config import DEFAULT_INPUT_FOLDER, DEFAULT_OUTPUT_FOLDER
from src.meta import get_authot_details, get_version
from src.watcher import FolderWatcher


def app(client_override: str | None = None, run_once: bool = False):
    processor_cls = get_processor_class(client_override)
    processor = processor_cls()

    watcher = FolderWatcher(
        folder=DEFAULT_INPUT_FOLDER,
        output_dir=DEFAULT_OUTPUT_FOLDER,
        processor=processor,
        run_once=run_once,
    )

    watcher.start()


def main():
    parser = argparse.ArgumentParser(description="My Simple CLI Tool")

    # version handled by argparse
    parser.add_argument("--version", action="version", version=f"{get_version()}")

    parser.add_argument("--author", action="store_true", help="Show author information")

    parser.add_argument(
        "--client",
        choices=list_available_clients(),
        help="Override the default client bundled with this build",
    )

    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Process existing files once and exit (no folder watching)",
    )

    args = parser.parse_args()

    # If --author is passed
    if args.author:
        details = get_authot_details()
        for key, value in details.items():
            print(f"{key:<10} : {value}")
        return

    # Default behavior
    app(
        client_override=args.client,
        run_once=args.run_once,
    )


if __name__ == "__main__":
    main()
