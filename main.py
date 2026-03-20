from __future__ import annotations

from pathlib import Path
import sys
from typing import Optional

import typer

from src.config import DEFAULT_INPUT_FOLDER, DEFAULT_OUTPUT_FOLDER
from src.logger import logger
from src.processor import ExcelProcessor, ProcessingError
from src.watcher import FolderWatcher

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
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
    if not file and not auto:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)

    if debug:
        logger.add(sys.stderr, level="DEBUG")

    processor = ExcelProcessor()

    if file:
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


if __name__ == "__main__":
    app()
