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
|   |-- api/
|   |   |-- __init__.py
|   |   |-- routes.py
|   |   `-- schemas.py
|   |-- cli.py
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py
|   |   `-- logging_config.py
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
|   `-- main.py
|-- client/          # reserved for future frontend, currently empty
|-- pyproject.toml
|-- README.md
|-- TODO.md
`-- tests/           # reserved for future test coverage, currently empty
```

## Setup

```powershell
python -m pip install -e .
ldt init-db
```

On Windows, if `ldt` is not recognized after installation, your Python
Scripts directory is not on `PATH`. Add it permanently with:

```powershell
$scripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$scripts", "User")
```

Then restart your terminal. Alternatively, invoke via module:

```powershell
python -m backend.cli init-db
```

Create a `.env` file with your Riot API key and Postgres connection string:

```text
RIOT_API_KEY=your-api-key
DATABASE_URL=postgresql://user:password@your-project.neon.tech/dbname?sslmode=require
```

The database is hosted Postgres on [Neon](https://neon.tech) (free tier).
Create a Neon project, copy its connection string into `DATABASE_URL`, then run
`ldt init-db` to create the schema.

## Commands

```powershell
ldt init-db
ldt update-challengers
ldt run-match-sync
ldt daily-maintenance
```

## Development

This repository uses a `backend/` layout with the installable package in
`backend/`. Install it in editable mode while developing:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

Use the installed `ldt` command (see `pyproject.toml` `project.scripts`) or run
the module directly with a subcommand:

```powershell
python -m backend.cli init-db
python -m backend.cli update-challengers
python -m backend.cli run-match-sync
python -m backend.cli daily-maintenance
```

## Notes

- `backend/` contains the application logic.
- `backend/cli.py` is the single `ldt` console-script entry point; it dispatches to
  `init-db`, `update-challengers`, `run-match-sync`, and `daily-maintenance`
  subcommands.
- `backend/api/` exposes `draft_service.recommend_champions()` over HTTP via
  FastAPI (`backend/main.py` is the app entrypoint; run with `fastapi dev backend/main.py`
  or `uvicorn backend.main:app`).
- The database is Postgres hosted on Neon; `DATABASE_URL` in `.env` points at it.
- `tests/` is available for future test coverage.
