
# AutoUFL

AutoUFL is a Windows-friendly Typer CLI that watches, normalizes, and exports structured Excel workbooks into CSV files that PI/AVEVA's UFL interface can ingest. It ships with opinionated defaults, full logging, and a release pipeline so you can double-click a packaged `.exe` or keep it running in watch mode.

## Features
- Excel → CSV normalization with deterministic column mapping and PI tag resolution.
- Batch/one-shot processing that renames completed files with timestamped `_done` suffixes.
- Folder watcher built on `watchdog` that retries safely and prevents duplicate processing.
- Rich logging to console and rotating files plus optional debug sink.
- `.env`-driven configuration (sheet name, folder layout, timestamp tuning, logging).
- Versioned CLI metadata (`--version`, `--author`) backed by a single source of truth (`pyproject.toml`).
- PyInstaller build recipe with automated GitHub Releases via release-please.

## Installation
The project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```
# Clone the repo, then install dependencies
uv sync --group dev

# Run the CLI
uv run python main.py --help
```

## Usage Examples
```
# Show current version (v1.0.0) sourced from pyproject
uv run python main.py --version

# Show author metadata
uv run python main.py --author

# Process a single workbook and delete it afterward
uv run python main.py --file "C:\drops\ManualTagUpdateUtility.xlsm" --delete

# Watch folders automatically (uses executable-relative Client Input/CSV UFL Input when --folder is omitted)
uv run python main.py --auto

# Watch a custom folder, write to a custom output folder
uv run python main.py --auto --folder D:\incoming --output D:\normalized
```

## Environment Configuration
Create a `.env` (see `.env.example`) to override defaults:

| Variable | Description |
| --- | --- |
| `AUTO_UFL_LOG_LEVEL` | `INFO`, `DEBUG`, etc.
| `AUTO_UFL_LOG_CONSOLE` | `true/false` to mirror logs to stdout.
| `AUTO_UFL_LOG_PATH` | Absolute path for persistent logs.
| `AUTO_UFL_SHEET_NAME` | Worksheet tab to read (default `P&B`).
| `AUTO_UFL_DEFAULT_TIMESTAMP` | Time-of-day (`HH:MM[:SS]` or `5:00 AM`) used when stamping `_done` filenames. Default is `05:00`.
| `AUTO_UFL_INPUT_DIR` / `AUTO_UFL_OUTPUT_DIR` | Override the default `Client Input` / `CSV UFL Input` folders.
| `AUTO_UFL_WATCH_INTERVAL` | Seconds between watchdog polling loops.
| `AUTO_UFL_FILE_STABILIZE` | Seconds to wait for a file to stop growing before processing.

When you double-click the packaged `.exe` (or run `--auto` without `--folder`), AutoUFL resolves the directories relative to the executable, loads `.env` from that same directory if present, and creates `Client Input` / `CSV UFL Input` automatically.

## Project Structure
```
AutoUFL/
├── main.py                 # Typer CLI entrypoint
├── src/
│   ├── config.py           # Environment + constant management
│   ├── logger.py           # Loguru configuration
│   ├── meta.py             # Project metadata helpers (version, URLs)
│   ├── processor.py        # Excel → CSV normalization logic
│   ├── runtime.py          # Timestamp helpers sourced from .env
│   └── watcher.py          # Watchdog observer & rename helpers
├── Client Input/           # Auto-created when running without args
├── CSV UFL Input/
├── README.md
├── pyproject.toml
└── .github/workflows/
```

## Building a Standalone `.exe`
```
uv sync --group dev
uv run pyinstaller main.py --name AutoUFL --onefile --clean
# Pick up dist/AutoUFL.exe and distribute it (ships with Client Input/CSV UFL Input defaults)
```

## Release Workflow
- Create or merge commits into `main` with meaningful messages (release-please uses them for changelog entries).
- Tag a commit with `v*` (e.g., `git tag v1.0.0 && git push origin v1.0.0`).
- The `release.yml` workflow triggers on the tag, runs `google-github-actions/release-please` to draft the release & changelog, builds a fresh PyInstaller `.exe` on Windows, and uploads the artifact to the GitHub Release page.

## Contribution Guidelines
1. Fork the repo and create a feature branch.
2. Run `uv run python -m compileall src main.py` plus any relevant tests before committing.
3. Follow conventional commit messages so release-please can summarize changes automatically.
4. Submit a pull request describing the change and any configuration updates.
5. For large features, open an issue first to discuss scope/UX expectations.
