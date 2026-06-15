# lol_draft_tool

League of Legends draft data tooling for collecting challenger match data and
building champion relationship statistics.

## Project Structure

```text
lol_draft_tool/
|-- .env
|-- .gitignore
|-- db/
|   `-- lol_draft.sqlite3
|-- pyproject.toml
|-- README.md
|-- requirements.txt
|-- todo
-- (compatibility wrappers removed)
|-- src/
|   `-- lol_draft_tool/
|       |-- cli/
|       |   |-- daily_maintenance.py
|       |   |-- init_db.py
|       |   |-- run_match_sync.py
|       |   `-- update_challengers.py
|       |-- core/
|       |   `-- config.py
|       |-- db/
|       |   |-- connection.py
|       |   |-- queries.py
|       |   `-- schema.py
|       |-- domain/
|       |   `-- draft_state.py
|       |-- external/
|       |   `-- riot_api.py
|       |-- pipeline/
|       |   |-- ingest_and_process_matches.py
|       |   |-- patch_maintenance.py
|       |   `-- update_ladder.py
|       |-- services/
|       |   `-- draft_service.py
|       `-- utils/
|           `-- helpers.py
`-- tests/
```

## Setup

```powershell
python -m pip install -e .
lol-init-db
```

On Windows, if `lol-init-db` is not recognized after installation, your Python
Scripts directory is not on `PATH`. Either add the Scripts directory reported by
pip to `PATH`, or use the module form:

```powershell
python -m lol_draft_tool.cli.init_db
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
lol-init-db
lol-update-challengers
lol-run-match-sync
lol-daily-maintenance
```

## Development

This repository uses a `src/` layout with the installable package in
`src/lol_draft_tool/`. Install it in editable mode while developing:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

Compatibility wrappers that used to live in `scripts/` have been removed.
Use the installed CLI commands (see `pyproject.toml` `project.scripts`) or
run the package modules directly:

```powershell
python -m lol_draft_tool.cli.init_db
python -m lol_draft_tool.cli.update_challengers
python -m lol_draft_tool.cli.run_match_sync
python -m lol_draft_tool.cli.daily_maintenance
```

## Notes

- `src/lol_draft_tool/` contains the application logic.
- `src/lol_draft_tool/cli/` contains CLI entrypoints for database initialization
  and scheduled update tasks.
 - (compatibility wrappers removed)
- `db/lol_draft.sqlite3` is the local SQLite database file used by the project.
- `LOL_DRAFT_DB_PATH` can override the database location for hosted jobs.
- `tests/` is available for future test coverage.
