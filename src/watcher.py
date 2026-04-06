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
    ISO_TIMESTAMP_FORMAT,
    SUPPORTED_EXTENSIONS,
    WATCH_POLLING_INTERVAL,
    WATCH_STABILIZATION_SECONDS,
)


class ExcelEventHandler(FileSystemEventHandler):
    def __init__(self, processor, output_dir: Path, delete_source: bool):
        self.processor = processor
        self.output_dir = output_dir
        self.delete_source = delete_source
        self._in_progress = set()

    # ---------------- Events ----------------
    def _handle_event(self, event) -> None:
        if event.is_directory:
            logger.debug(f"Ignoring directory event at {event.src_path}")
            return

        path = Path(getattr(event, "dest_path", event.src_path))
        logger.debug(f"Received filesystem event for {path}")
        self.process_file(path)

    def on_created(self, event):
        self._handle_event(event)

    def on_modified(self, event):
        self._handle_event(event)

    def on_moved(self, event):
        self._handle_event(event)

    # ---------------- Core ----------------
    def process_existing_files(self, folder: Path) -> None:
        files = [path for path in folder.iterdir() if path.is_file()]
        if not files:
            logger.info(f"No pre-existing files detected in {folder}")
            return

        logger.info(f"Found {len(files)} pre-existing file(s) in {folder}, processing now")
        for path in files:
            self.process_file(path)

    def process_file(self, path: Path) -> None:
        is_valid, reason = self._validate_path(path)
        if not is_valid:
            logger.debug(f"Skipping {path.name}: {reason}")
            return

        logger.info(f"Processing file: {path}")
        self._in_progress.add(path)

        try:
            self._wait_stable(path)
            self._run_processor(path)
        finally:
            self._in_progress.discard(path)

    # ---------------- Helpers ----------------
    def _run_processor(self, path: Path) -> None:
        try:
            result = self.processor.process_file(path, self.output_dir)

            logger.success(f"{path.name} -> {result.rows_written} rows -> {result.output_file.name}")

            if result.rows_written == 0:
                logger.warning(f"{path.name} produced zero rows; inspect source data")

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

    def _wait_stable(self, path: Path) -> None:
        last_size = -1
        start = time.time()

        while True:
            try:
                size = path.stat().st_size
            except FileNotFoundError:
                return

            if size == last_size:
                elapsed = time.time() - start
                logger.debug(f"{path.name} stabilized after {elapsed:.2f}s")
                return

            last_size = size
            time.sleep(WATCH_STABILIZATION_SECONDS)

    def _validate_path(self, path: Path) -> tuple[bool, str | None]:
        if not path.exists():
            return False, "file no longer exists"
        if path in self._in_progress:
            return False, "processing already in progress"
        if path.stem.endswith((ARCHIVE_SUFFIX_SUCCESS, ARCHIVE_SUFFIX_ERROR)):
            return False, "file already archived"
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return False, f"unsupported extension '{path.suffix}'"
        return True, None

    def _rename(self, path: Path, suffix: str) -> None:
        base = path.stem

        if suffix == ARCHIVE_SUFFIX_SUCCESS:
            timestamp = datetime.now().strftime(ISO_TIMESTAMP_FORMAT)
            new_name = f"{base}_{timestamp}{suffix}{path.suffix}"
        else:
            new_name = f"{base}{suffix}{path.suffix}"

        new_path = path.with_name(new_name)

        try:
            path.rename(new_path)
            logger.info(f"Renamed: {path.name} -> {new_path.name}")
        except Exception as e:
            logger.exception(f"Rename failed for {path.name}: {e}")


class FolderWatcher:
    def __init__(self, folder: Path, output_dir: Path, processor, delete_source=False):
        self.folder = folder
        self.output_dir = output_dir
        self.processor = processor
        self.delete_source = delete_source

    def start(self) -> None:
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

        logger.info(
            f"Watching folder: input={self.folder} | output={self.output_dir} | "
            f"delete_source={self.delete_source} | processor={self.processor.__class__.__name__}"
        )

        try:
            while True:
                time.sleep(WATCH_POLLING_INTERVAL)
        except KeyboardInterrupt:
            logger.info(f"Stopping watcher...")
        finally:
            observer.stop()
            observer.join()
            logger.info(f"Watcher stopped for {self.folder}")
