import time
from datetime import datetime
from pathlib import Path

from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.clients.base_processor import ProcessingError
from src.config import (
    ARCHIVE_SUFFIX_ERROR,
    ARCHIVE_SUFFIX_SUCCESS,
    SUPPORTED_EXTENSIONS,
    WATCH_POLLING_INTERVAL,
    WATCH_STABILIZATION_SECONDS,
)
from src.runtime import processed_timestamp


class ExcelEventHandler(FileSystemEventHandler):
    def __init__(self, processor, output_dir: Path, delete_source: bool):
        self.processor = processor
        self.output_dir = output_dir
        self.delete_source = delete_source
        self._in_progress = set()

    # ---------------- Events ----------------
    def _handle_event(self, event):
        if event.is_directory:
            return

        path = Path(getattr(event, "dest_path", event.src_path))
        self.process_file(path)

    def on_created(self, event):
        self._handle_event(event)

    def on_modified(self, event):
        self._handle_event(event)

    def on_moved(self, event):
        self._handle_event(event)

    # ---------------- Core ----------------
    def process_existing_files(self, folder: Path):
        for path in folder.iterdir():
            if path.is_file():
                self.process_file(path)

    def process_file(self, path: Path):
        if not self._is_valid(path):
            return

        logger.info(f"Processing file: {path}")
        self._in_progress.add(path)

        try:
            self._wait_stable(path)
            self._run_processor(path)
        finally:
            self._in_progress.discard(path)

    # ---------------- Helpers ----------------
    def _run_processor(self, path: Path):
        try:
            result = self.processor.process_file(path, self.output_dir)

            logger.success(f"{path.name} -> {result.rows_written} rows -> {result.output_file.name}")

            if self.delete_source:
                path.unlink(missing_ok=True)
            else:
                self._rename(path, ARCHIVE_SUFFIX_SUCCESS)

        except ProcessingError:
            logger.exception(f"Processing failed: {path.name}")
            self._rename(path, ARCHIVE_SUFFIX_ERROR)

        except Exception:
            logger.exception(f"Unexpected error: {path.name}")
            self._rename(path, ARCHIVE_SUFFIX_ERROR)

    def _wait_stable(self, path: Path):
        last_size = -1

        while True:
            try:
                size = path.stat().st_size
            except FileNotFoundError:
                return

            if size == last_size:
                return

            last_size = size
            time.sleep(WATCH_STABILIZATION_SECONDS)

    def _is_valid(self, path: Path):
        return (
            path.exists()
            and path not in self._in_progress
            and not path.stem.endswith((ARCHIVE_SUFFIX_SUCCESS, ARCHIVE_SUFFIX_ERROR))
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    def _rename(self, path: Path, suffix: str):
        base = path.stem

        if suffix == ARCHIVE_SUFFIX_SUCCESS:
            timestamp = processed_timestamp().strftime("%Y-%m-%d_%H-%M-%S")
            new_name = f"{base}_{timestamp}{suffix}{path.suffix}"
        else:
            new_name = f"{base}{suffix}{path.suffix}"

        new_path = path.with_name(new_name)

        try:
            path.rename(new_path)
            logger.info(f"Renamed: {path.name} -> {new_path.name}")
        except Exception as e:
            logger.error(f"Rename failed for {path.name}: {e}")


class FolderWatcher:
    def __init__(self, folder: Path, output_dir: Path, processor, delete_source=False):
        self.folder = folder
        self.output_dir = output_dir
        self.processor = processor
        self.delete_source = delete_source

    def start(self):
        self.folder.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        handler = ExcelEventHandler(
            self.processor,
            self.output_dir,
            self.delete_source,
        )

        # Process existing files first
        handler.process_existing_files(self.folder)

        observer = Observer()
        observer.schedule(handler, str(self.folder), recursive=False)
        observer.start()

        logger.info(f"Watching folder: {self.folder}")

        try:
            while True:
                time.sleep(WATCH_POLLING_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Stopping watcher...")
        finally:
            observer.stop()
            observer.join()
