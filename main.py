from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

from src.config import ARCHIVE_SUFFIX_SUCCESS, DEFAULT_INPUT_FOLDER, DEFAULT_OUTPUT_FOLDER, SUPPORTED_EXTENSIONS
from src.logger import logger
from src.processor import ExcelProcessor, ProcessingError
from src.watcher import FolderWatcher, rename_with_suffix

app = typer.Typer(
    add_completion=False,
    no_args_is_help=False,
    help="Convert structured Excel sheets into normalized CSV files.",
)


@app.callback(invoke_without_command=True)
def cli(  # noqa: D401
    ctx: typer.Context,
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        help="Process a single Excel file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    auto: bool = typer.Option(
        False,
        "--auto",
        help="Watch a folder and process new Excel files automatically.",
    ),
    folder: Optional[Path] = typer.Option(
        None,
        "--folder",
        help="Override the default watch folder when --auto is used.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        help="Directory for generated CSV files.",
        file_okay=False,
    ),
    delete: bool = typer.Option(
        False,
        "--delete",
        help="Delete successfully processed Excel files instead of renaming.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable verbose debug logging to stderr.",
    ),
) -> None:
    if ctx.invoked_subcommand:
        return

    if file and auto:
        raise typer.BadParameter("Cannot combine --file and --auto.")

    if debug:
        logger.add(sys.stderr, level="DEBUG")

    processor = ExcelProcessor()

    if not file and not auto:
        _run_default_batch(processor)
        return

    if file:
        if _is_marked_done(file):
            logger.info(f"Skipping '{file}' because it is already marked as processed.")
            raise typer.Exit(code=0)
        if folder is not None:
            raise typer.BadParameter("--folder can only be used with --auto mode.")
        _run_file_mode(
            processor=processor,
            file_path=file,
            output_dir=output,
            delete_source=delete,
        )
    else:
        watch_folder = folder or DEFAULT_INPUT_FOLDER
        destination = output or DEFAULT_OUTPUT_FOLDER
        _run_auto_mode(
            processor=processor,
            watch_folder=watch_folder,
            output_dir=destination,
            delete_source=delete,
        )


def _run_file_mode(
    processor: ExcelProcessor,
    file_path: Path,
    output_dir: Optional[Path],
    delete_source: bool,
) -> None:
    target_file = file_path.resolve()
    destination = (output_dir or target_file.parent).resolve()
    try:
        result = processor.process_file(target_file, destination)
    except ProcessingError:
        logger.exception(f"Failed to process '{target_file.name}'")
        raise typer.Exit(code=1)
    except Exception as exc:  # noqa: BLE001
        logger.exception(f"Unexpected failure while processing '{target_file}'")
        raise typer.Exit(code=1) from exc

    logger.success(
        f"Processed '{target_file.name}' -> {result.output_file} ({result.rows_written} rows)",
    )
    if delete_source:
        target_file.unlink(missing_ok=True)
    typer.echo(str(result.output_file))


def _run_auto_mode(
    processor: ExcelProcessor,
    watch_folder: Path,
    output_dir: Path,
    delete_source: bool,
) -> None:
    watcher = FolderWatcher(
        folder=watch_folder,
        output_dir=output_dir,
        processor=processor,
        delete_source=delete_source,
    )
    watcher.start()


def _run_default_batch(processor: ExcelProcessor) -> None:
    base_dir = _resolve_base_directory()
    dotenv_path = base_dir / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=True)
        logger.info(f"Loaded configuration from '{dotenv_path}'")
    else:
        logger.info(f"No .env file found at '{dotenv_path}'; using defaults.")

    input_dir = base_dir / os.getenv("AUTO_UFL_INPUT_DIR", "Client Input")
    output_dir = base_dir / os.getenv("AUTO_UFL_OUTPUT_DIR", "CSV UFL Input")
    try:
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.exception(f"Unable to prepare working folders inside '{base_dir}'")
        return

    log_file = base_dir / "autoUFL.log"
    log_sink_id = logger.add(log_file, level="INFO", enqueue=True, mode="a")
    logger.info(f"Auto UFL batch run started in '{base_dir}'")

    try:
        try:
            files = sorted(path for path in input_dir.iterdir() if _should_process_input_file(path))
        except OSError:
            logger.exception(f"Unable to scan input folder '{input_dir}'")
            return

        if not files:
            logger.info(f"No supported Excel files found in '{input_dir}'.")

        for path in files:
            logger.info(f"Processing '{path.name}'")
            try:
                result = processor.process_file(path, output_dir)
            except ProcessingError:
                logger.exception(f"Processing failed for '{path.name}'")
                continue
            except Exception:  # noqa: BLE001
                logger.exception(f"Unexpected error while processing '{path.name}'")
                continue
            logger.info(f"Finished '{path.name}' -> {result.output_file.name} ({result.rows_written} rows)")
            rename_with_suffix(path, ARCHIVE_SUFFIX_SUCCESS, timestamp=datetime.now())
        logger.info("Auto UFL batch run completed.")
    finally:
        logger.remove(log_sink_id)


def _should_process_input_file(path: Path) -> bool:
    if not path.is_file():
        logger.info(f"Skipping '{path.name}' because file is not valid.")
        return False
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        logger.info(f"Skipping '{path.name}' because file extension is not supported.")
        return False
    if _is_marked_done(path):
        logger.info(f"Skipping '{path.name}' because it is already marked as processed.")
        return False
    return True


def _is_marked_done(path: Path) -> bool:
    return ARCHIVE_SUFFIX_SUCCESS in path.stem


def _resolve_base_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(sys.argv[0]).resolve().parent


if __name__ == "__main__":
    app()
