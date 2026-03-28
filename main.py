
from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Optional

import typer
from dotenv import load_dotenv

from src.config import (
    ARCHIVE_SUFFIX_SUCCESS,
    DEFAULT_INPUT_FOLDER,
    DEFAULT_OUTPUT_FOLDER,
    SUPPORTED_EXTENSIONS,
)
from src.logger import logger
from src.meta import get_author_record, get_project_urls, get_version
from src.processor import ExcelProcessor, ProcessingError
from src.runtime import processed_timestamp
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
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the application version and exit.",
        is_eager=True,
    ),
    author: bool = typer.Option(
        False,
        "--author",
        help="Show author & profile links and exit.",
        is_eager=True,
    ),
) -> None:
    if ctx.invoked_subcommand:
        return

    if version:
        _print_version()
        raise typer.Exit(code=0)
    if author:
        _print_author_metadata()
        raise typer.Exit(code=0)

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
        watch_folder: Path
        destination: Path
        if folder:
            watch_folder = folder
            destination = (output or DEFAULT_OUTPUT_FOLDER).resolve()
        else:
            watch_folder, destination = _prepare_executable_folders(load_env_vars=True)
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
    input_dir, output_dir = _prepare_executable_folders(load_env_vars=True)

    log_file = input_dir.parent / "autoUFL.log"
    log_sink_id = logger.add(log_file, level="INFO", enqueue=True, mode="a")
    logger.info(f"Auto UFL batch run started in '{input_dir.parent}'")

    try:
        try:
            files = sorted(
                path
                for path in input_dir.iterdir()
                if _should_process_input_file(path)
            )
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
            logger.info(
                f"Finished '{path.name}' -> {result.output_file.name} ({result.rows_written} rows)"
            )
            rename_with_suffix(path, ARCHIVE_SUFFIX_SUCCESS, timestamp=processed_timestamp())
        logger.info("Auto UFL batch run completed.")
    finally:
        logger.remove(log_sink_id)


def _prepare_executable_folders(load_env_vars: bool) -> tuple[Path, Path]:
    base_dir = _resolve_base_directory()
    dotenv_path = base_dir / ".env"
    if load_env_vars and dotenv_path.exists():
        load_dotenv(dotenv_path, override=True)
    input_dir = base_dir / os.getenv("AUTO_UFL_INPUT_DIR", "Client Input")
    output_dir = base_dir / os.getenv("AUTO_UFL_OUTPUT_DIR", "CSV UFL Input")
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    return input_dir, output_dir


def _should_process_input_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False
    if _is_marked_done(path):
        logger.info(f"Skipping '{path.name}' because it is already marked as processed.")
        return False
    return True


def _is_marked_done(path: Path) -> bool:
    return ARCHIVE_SUFFIX_SUCCESS in path.stem


def _print_author_metadata() -> None:
    author = get_author_record()
    urls = get_project_urls()
    header = typer.style("Author", fg="cyan", bold=True)
    typer.echo(header, color=True)
    _echo_metadata_line("Name", author.get("name", "N/A"))
    _echo_metadata_line("Portfolio", urls.get("Portfolio", "N/A"))
    _echo_metadata_line("GitHub", urls.get("GitHub", "N/A"))
    _echo_metadata_line("LinkedIn", urls.get("LinkedIn", "N/A"))


def _print_version() -> None:
    name = typer.style("AutoUFL", fg="cyan", bold=True)
    version = typer.style(get_version(), fg="green", bold=True)
    typer.echo(f"{name} {version}", color=True)


def _echo_metadata_line(label: str, value: str) -> None:
    styled_label = typer.style(f"{label}:", bold=True, fg="magenta")
    styled_value = typer.style(value, fg="yellow")
    typer.echo(f"  {styled_label} {styled_value}", color=True)


def _resolve_base_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(sys.argv[0]).resolve().parent


if __name__ == "__main__":
    app()
