"""
Watchdog-powered folder monitoring.
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

from loguru import logger
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from src.config import (
    ARCHIVE_SUFFIX_ERROR,
    ARCHIVE_SUFFIX_SUCCESS,
    SUPPORTED_EXTENSIONS,
    WATCH_POLLING_INTERVAL,
    WATCH_STABILIZATION_SECONDS,
)
from src.processor import ExcelProcessor, ProcessingError


class _ExcelEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        processor: ExcelProcessor,
        output_dir: Path,
        delete_source: bool,
    ) -> None:
        self.processor = processor
        self.output_dir = output_dir
        self.delete_source = delete_source
        self._in_progress: set[Path] = set()

    def on_created(self, event: FileSystemEvent) -> None:  # noqa: D401
        self._handle_event(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        self._handle_event(event)

    def on_moved(self, event: FileSystemEvent) -> None:
        if getattr(event, "dest_path", None):
            event_src = Path(event.dest_path)
        else:
            event_src = Path(event.src_path)
        self._process_path(event_src)

    def process_existing_files(self, folder: Path) -> None:
        for path in sorted(folder.iterdir()):
            if path.is_file():
                self._process_path(path)

    # ------------------------------------------------------------------ helpers
    def _handle_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        self._process_path(Path(event.src_path))

    def _process_path(self, path: Path) -> None:
        if not self._is_supported(path):
            return
        if path in self._in_progress:
            return

        logger.info(f"New file detected: {path}")
        logger.debug(f"Output path: {self.output_dir / f'{path.stem}.csv'}")
        self._in_progress.add(path)
        try:
            self._wait_until_stable(path)
            self._process_file(path)
        finally:
            self._in_progress.discard(path)

    def _process_file(self, path: Path) -> None:
        try:
            result = self.processor.process_file(path, self.output_dir)
            logger.success(
                f"Processed '{path.name}' -> {result.rows_written} rows into {result.output_file.name}",
            )
            if self.delete_source:
                path.unlink(missing_ok=True)
            else:
                rename_with_suffix(path, ARCHIVE_SUFFIX_SUCCESS, timestamp=datetime.now())
        except ProcessingError:
            logger.exception(f"Processing failed for '{path}'")
            rename_with_suffix(path, ARCHIVE_SUFFIX_ERROR)
        except Exception:  # noqa: BLE001
            logger.exception(f"Unexpected failure while handling '{path.name}'")
            rename_with_suffix(path, ARCHIVE_SUFFIX_ERROR)

    def _wait_until_stable(self, path: Path) -> None:
        last_size = -1
        while True:
            try:
                current_size = path.stat().st_size
            except FileNotFoundError:
                return
            if current_size == last_size:
                break
            last_size = current_size
            time.sleep(WATCH_STABILIZATION_SECONDS)

    @staticmethod
    def _is_supported(path: Path) -> bool:
        if not path.exists():
            return False
        name = path.stem
        if name.endswith(ARCHIVE_SUFFIX_SUCCESS) or name.endswith(ARCHIVE_SUFFIX_ERROR):
            return False
        return path.suffix.lower() in SUPPORTED_EXTENSIONS


class FolderWatcher:
    """Runs a watchdog observer for Excel drops."""

    def __init__(
        self,
        folder: Path,
        output_dir: Path,
        processor: ExcelProcessor,
        delete_source: bool = False,
    ) -> None:
        self.folder = folder
        self.output_dir = output_dir
        self.processor = processor
        self.delete_source = delete_source

    def start(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        handler = _ExcelEventHandler(
            processor=self.processor,
            output_dir=self.output_dir,
            delete_source=self.delete_source,
        )
        handler.process_existing_files(self.folder)

        observer = Observer()
        observer.schedule(handler, str(self.folder), recursive=False)
        observer.start()

        logger.info(f"Watching folder {self.folder} for Excel files -> {self.output_dir}")
        try:
            while True:
                time.sleep(WATCH_POLLING_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Stopping folder watcher...")
        finally:
            observer.stop()
            observer.join()


def rename_with_suffix(path: Path, suffix: str, *, timestamp: datetime | None = None) -> Path:
    base_stem = path.stem
    composed = None
    if timestamp and suffix == ARCHIVE_SUFFIX_SUCCESS:
        stamp = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        if base_stem.endswith(suffix):
            base_stem = base_stem[: -len(suffix)]
        composed = f"{base_stem}_{stamp}{suffix}"
    if composed is None:
        composed = f"{base_stem}{suffix}"

    candidate = path.with_name(f"{composed}{path.suffix}")
    counter = 1
    while candidate.exists():
        candidate = path.with_name(f"{composed}_{counter}{path.suffix}")
        counter += 1

    logger.info(f"Renaming file '{path.name}' to suffix '{suffix}'")
    try:
        path.rename(candidate)
        return candidate
    except FileNotFoundError:
        return path
    except OSError as exc:
        logger.error(f"Failed to rename '{path}': {exc}")
        return path
