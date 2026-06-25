# lol_draft_tool

League of Legends draft data tooling for collecting challenger match data and
building champion relationship statistics.

## Project Structure

```text
lol_draft_tool/
|-- .env
|-- .gitignore
|-- backend/
|   |-- __init__.py
|   |-- cli/
|   |   |-- daily_maintenance.py
|   |   |-- init_db.py
|   |   |-- run_match_sync.py
|   |   `-- update_challengers.py
|   |-- core/
|   |   |-- __init__.py
|   |   `-- config.py
|   |-- db/
|   |   |-- __init__.py
|   |   |-- connection.py
|   |   |-- queries.py
|   |   `-- schema.py
|   |-- domain/
|   |   |-- __init__.py
|   |   `-- draft_state.py
|   |-- external/
|   |   |-- __init__.py
|   |   `-- riot_api.py
|   |-- pipeline/
|   |   |-- __init__.py
|   |   |-- ingest_and_process_matches.py
|   |   |-- patch_maintenance.py
|   |   `-- update_ladder.py
|   |-- services/
|   |   |-- __init__.py
|   |   `-- draft_service.py
|   |-- utils/
|   |   |-- __init__.py
|   |   `-- helpers.py
|   `-- __init__.py
|-- db/
|   `-- lol_draft.sqlite3
|-- pyproject.toml
|-- README.md
|-- requirements.txt
|-- todo
`-- tests/
```

## Setup

```powershell
python -m pip install -e .
ldt-init-db
```

On Windows, if `ldt-init-db` is not recognized after installation, your Python
Scripts directory is not on `PATH`. Add it permanently with:

```powershell
$scripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$scripts", "User")
```

Then restart your terminal. Alternatively, invoke via module:

```powershell
python -m backend.cli.init_db
```

Create a `.env` file with your Riot API key:

```text
RIOT_API_KEY=your-api-key
```

By default, the SQLite database is read from `db/lol_draft.sqlite3` relative to
the current working directory. For hosted jobs, set an explicit database path:

```text
LOL_DRAFT_DB_PATH=/absolute/path/to/lol_draft.sqlite3
```

## Commands

```powershell
ldt-init-db
ldt-update-challengers
ldt-run-match-sync
ldt-daily-maintenance
```

## Development

This repository uses a `backend/` layout with the installable package in
`backend/`. Install it in editable mode while developing:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

Use the installed CLI commands (see `pyproject.toml` `project.scripts`) or run
these package modules directly:

```powershell
python -m backend.cli.init_db
python -m backend.cli.update_challengers
python -m backend.cli.run_match_sync
python -m backend.cli.daily_maintenance
```

## Notes

- `backend/` contains the application logic.
- `backend/cli/` contains CLI entrypoints for database initialization
  and scheduled update tasks.
- `db/lol_draft.sqlite3` is the local SQLite database file used by the project.
- `LOL_DRAFT_DB_PATH` can override the database location for hosted jobs.
- `tests/` is available for future test coverage.
