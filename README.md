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
|-- setup.cfg
|-- todo
|-- scripts/
|   |-- daily_maintenance.py
|   |-- init_db.py
|   |-- run_match_sync.py
|   `-- update_challengers.py
|-- src/
|   |-- __init__.py
|   |-- core/
|   |   |-- __init__.py
|   |   `-- config.py
|   |-- db/
|   |   |-- __init__.py
|   |   |-- connection.py
|   |   |-- queries.py
|   |   `-- schema.py
|   |-- domain/
|   |   `-- draft_state.py
|   |-- external/
|   |   |-- __init__.py
|   |   `-- riot_api.py
|   |-- pipeline/
|   |   |-- __init__.py
|   |   |-- challenger_update.py
|   |   |-- ingest_matches.py
|   |   |-- patch_maintenance.py
|   |   `-- process_match.py
|   |-- services/
|   |   |-- __init__.py
|   |   `-- draft_service.py
|   `-- utils/
|       |-- __init__.py
|       `-- helpers.py
`-- tests/
```

## Setup

```powershell
pip install -r requirements.txt
python scripts/init_db.py
```

Create a `.env` file with your Riot API key:

```text
RIOT_API_KEY=your-api-key
```

## Commands

```powershell
python scripts/init_db.py
python scripts/update_challengers.py
python scripts/run_match_sync.py
python scripts/daily_maintenance.py
```

## Install in editable mode

This repository is packaged so you can install it in editable mode and keep
`src/` on the import path.

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Once installed, the same scripts continue to work with top-level imports:

```bash
python scripts/run_match_sync.py
python scripts/update_challengers.py
```

## Notes

- `src/` contains the application logic.
- `scripts/` contains CLI entrypoints for database initialization and scheduled
  update tasks.
- `db/lol_draft.sqlite3` is the local SQLite database file used by the project.
- `tests/` is available for future test coverage.
