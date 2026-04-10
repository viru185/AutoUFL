# AutoUFL

AutoUFL watches a drop folder for Excel workbooks, normalizes them with client-specific rules, and emits PI/AVEVA UFL-ready CSV files. It is packaged as a Windows-friendly CLI so operators can keep it running beside the data source or bake it into a PyInstaller executable.

## Highlights

- File watcher built on `watchdog` that can run continuously or process existing files once and exit with `--run-once`.
- Pluggable client processors under `src/clients/*` so each customer gets bespoke cleaning, tag mapping, and export logic without touching the core watcher.
- Structured logging via `loguru` with mirrored console + file sinks, rotation/retention controls, and enriched events for filesystem activity.
- `.env`-driven configuration for directories, timestamps, watchdog tuning, and default client selection.
- Dynamic client loading that works in both development runs and packaged EXE builds.

## Requirements & Setup

1. Install [uv](https://github.com/astral-sh/uv) (or use an existing Python 3.13 environment; `.python-version` pins 3.13).

2. Clone the repository and install dependencies:

```powershell
uv sync --group dev
```

3. Copy `.env.example` to `.env` and update any values (see [Configuration](#configuration-env)).

## Running the Watcher

AutoUFL exposes a single CLI entrypoint:

```powershell
uv run python main.py                 # start the watcher with the default client
uv run python main.py --client utkal  # override the client explicitly
uv run python main.py --run-once      # process existing files once and exit
uv run python main.py --version       # prints version sourced from pyproject.toml
uv run python main.py --author        # prints maintainer & contact info
```

Behavior notes:

- The watcher creates (if missing) `Client Input/` and `CSV UFL Input/` directories alongside the executable or repo root. Drop Excel files into `Client Input/`; CSV output lands in `CSV UFL Input/`.
- Existing files are processed before the observer starts, so you can seed the folder and then launch the watcher.
- With `--run-once`, AutoUFL processes the current files and exits without starting the folder observer.
- Each processed file is either deleted (`delete_source=True` when instantiating `FolderWatcher`) or renamed using `_done`/`_error` plus an ISO timestamp. Errors stay nearby for inspection.
- Stop the watcher with `Ctrl+C`. A friendly shutdown message is logged and the observer is closed cleanly.

## Client Selection Hierarchy

When you build or run AutoUFL, the client is resolved in this order:

1. `--client` on the CLI, when provided.
2. The baked-in manifest from the build (`build/client_manifest.json` in dev or the embedded manifest in the EXE).
3. `AUTO_UFL_CLIENT_ENV` only when no manifest is available, which is mainly the development fallback path.
4. The first discovered client if nothing else is available.

In packaged builds, the manifest usually defines the available clients and the default client for that build. That means a single-client EXE will stay fixed to that client, while the `all` build can expose multiple bundled clients.

## Logging & Diagnostics

- Logging is centralized in `src/logger.py` and powered by `loguru`.
- Console output is colorized and synchronized when `AUTO_UFL_LOG_CONSOLE=true`.
- File logging defaults to `autoUFL.log` in the project root. Use `AUTO_UFL_LOG_PATH` to relocate it; rotation/retention are controlled via Loguru-friendly strings (for example `50 MB`, `1 week`, `10 files`).
- Watcher events now surface why files are skipped, how long stabilization took, whether processors returned zero rows, and which client was selected.

## Configuration (.env)

All runtime knobs live in `.env`. Every variable is optional; defaults appear in parentheses.

| Variable                     | Default                     | Purpose                                                                        |
| ---------------------------- | --------------------------- | ------------------------------------------------------------------------------ |
| `AUTO_UFL_LOG_LEVEL`         | `INFO`                      | Global log level passed to loguru sinks.                                       |
| `AUTO_UFL_LOG_CONSOLE`       | `false`                     | Mirror logs to stdout; accepts `true/false/1/0/yes/no`.                        |
| `AUTO_UFL_LOG_PATH`          | `<project>/autoUFL.log`     | Absolute path for the file sink; created automatically.                        |
| `AUTO_UFL_LOG_ROTATION`      | `5 MB`                      | Loguru rotation expression (`"10 MB"`, `"1 week"`, etc.).                      |
| `AUTO_UFL_LOG_RETENTION`     | `0`                         | Loguru retention expression. Use `0` to keep everything or e.g. `"14 days"`.   |
| `AUTO_UFL_DEFAULT_TIMESTAMP` | `05:00:00`                  | Time-of-day appended to normalized month starts when emitting CSV rows.        |
| `AUTO_UFL_INPUT_DIR`         | `<project>/Client Input`    | Override input drop folder.                                                    |
| `AUTO_UFL_OUTPUT_DIR`        | `<project>/CSV UFL Input`   | Override output folder.                                                        |
| `AUTO_UFL_WATCH_INTERVAL`    | `1.0`                       | Seconds between watchdog polling loops.                                        |
| `AUTO_UFL_FILE_STABILIZE`    | `1.0`                       | Seconds to wait between size checks before a file is considered stable.        |
| `AUTO_UFL_CLIENT_ENV`        | _(first discovered client)_ | Forces a default client when no client is passed and no manifest is available. |

> Tip: Changes require restarting the watcher. Keep `.env` beside the executable (PyInstaller build) or alongside the repo root for development.

## Adding a New Client

Client logic lives under `src/clients/<slug>/`. Adding another customer means supplying configuration plus an `ExcelProcessor` subclass. Follow these steps:

1. **Create the package skeleton**

```
src/clients/
  └── myclient/
      ├── __init__.py          # can stay empty
      ├── client_config.py     # schemas, regexes, mappings
      └── processor.py         # ExcelProcessor implementation
```

2. **Author `client_config.py`**

- Declare `SHEETS_TO_PROCESS` or `SHEETS_TO_PROCESS_REGEX` to target worksheets.
- Provide `COLUMNS_TO_DROP_RE_EXPRESSION`, `COLUMN_RENAME_MAP`, and `TAG_MAPPING` dictionaries similar to the existing clients.

3. **Implement `ExcelProcessor`**

- Subclass `baseExcelProcessor` from `src/clients/base_processor.py`.
- Override `process_file(self, file_path, output_dir)` and call the shared helpers (`_set_header`, `_drop_columns_by_regex`, `_map_description_to_tag`, `_prepare_ufl_csv_df`, `_save_ufl_csv`).
- Add any client-specific cleanup in `_clean_df`.
- Wrap the body in `try/except` exactly like the existing processors so watcher error handling stays consistent.

4. **Test locally**

- Drop representative workbooks into `Client Input/`.
- Run `uv run python main.py --client myclient`.
- Inspect logs for warnings (missing tags, zero rows) and verify CSV output.

5. **Run one time**

- Use `uv run python main.py --run-once` to process the current folder contents once and exit.

6. **Set the default client (optional)**

- Add `AUTO_UFL_CLIENT_ENV=myclient` to `.env` for development fallback runs where no manifest is present.

7. **Package for distribution**

- Run `uv run python build.py`. The script discovers every client directory, writes `build/client_manifest.json`, and produces per-client `.exe` files under `dist/` (plus an `all` build that contains every processor).

Because discovery is dynamic, no registry edits are required—just ensure the `processor.py` file exports a class named `ExcelProcessor`.

## Project Structure

```
AutoUFL/
├── main.py                 # argparse CLI entrypoint
├── src/
│   ├── config.py           # .env loading, path resolution, runtime constants
│   ├── logger.py           # loguru configuration (console/file sinks)
│   ├── meta.py             # version/author helpers sourced from pyproject
│   ├── watcher.py          # watchdog observer + processing loop
│   └── clients/
│       ├── base_processor.py   # shared dataframe utilities + ProcessResult
│       ├── registry.py         # dynamic client discovery/manifest loader
│       └── <client>/           # client-specific processors & configs
├── Client Input/           # default ingest location (auto-created)
├── CSV UFL Input/          # default export target (auto-created)
├── build.py                # PyInstaller helper that writes client manifests
├── autoUFL.spec            # PyInstaller spec consumed by build.py
├── README.md
└── pyproject.toml
```

## Building a Standalone `.exe`

```powershell
uv sync --group dev
uv run python build.py             # writes build/client_manifest.json
# Dist executables live under dist/autoUFL_<client>.exe (plus autoUFL_all.exe)
```

## Release Workflow

- A push to `main` triggers the release workflow.
- `googleapis/release-please-action@v4` creates or updates the release PR and publishes a GitHub release when a new version is ready.
- When a release is created, a Windows build job runs on `windows-latest`.
- The build job installs `uv`, syncs dependencies, runs `uv run python build.py`, and collects every `.exe` from `dist/`.
- The workflow generates a download table for the release body and uploads all installers to the GitHub Release using the release tag.

## Dev Build & Test Workflow

- A push to `dev` or a manual `workflow_dispatch` run triggers the dev build workflow.
- It builds the installers on `windows-latest`, then uploads them as a prerelease with a fixed test tag.
- This is useful for validating packaging changes before merging to `main`.

## Contribution Guidelines

1. Create a feature branch from `main`.
2. Run `uv run python -m compileall src main.py` (and any data-quality checks relevant to your client) before committing.
3. Follow conventional commits so the automated changelog stays tidy.
4. Open a PR that describes the change, configuration updates, and any new client assumptions or sample data needs.
5. For sizeable enhancements, open an issue first to align on expectations.
