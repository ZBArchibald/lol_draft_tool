# lol_draft_tool

League of Legends draft recommendation tool. Ingests Challenger-ranked match
data via the Riot Games API, builds champion synergy/counter statistics in
Postgres (hosted on Neon), and serves draft recommendations over a FastAPI
backend with a React web client.

## Project Structure

```text
lol_draft_tool/
|-- .env.example
|-- .gitignore
|-- .github/
|   `-- workflows/
|       |-- daily-maintenance.yml   # cron: detect patch change, refresh ladder
|       `-- match-sync.yml           # cron: ingest new Challenger matches
|-- backend/
|   |-- __init__.py
|   |-- main.py                      # FastAPI app entrypoint (CORS + router)
|   |-- cli.py                       # single `ldt` console-script entry point
|   |-- api/
|   |   |-- __init__.py
|   |   |-- routes.py                # /api/champions, /api/recommend
|   |   `-- schemas.py               # Pydantic request/response models
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py
|   |   `-- logging_config.py
|   |-- db/
|   |   |-- __init__.py
|   |   |-- connection.py            # db_connection() pooled context manager
|   |   |-- queries.py               # all SQL lives here
|   |   `-- schema.py
|   |-- domain/
|   |   |-- __init__.py
|   |   `-- draft_state.py
|   |-- external/
|   |   |-- __init__.py
|   |   `-- riot_api.py               # rate-limited Riot API client
|   |-- pipeline/
|   |   |-- __init__.py
|   |   |-- ingest_and_process_matches.py
|   |   |-- patch_maintenance.py
|   |   `-- update_ladder.py
|   `-- services/
|       |-- __init__.py
|       `-- draft_service.py          # recommend_champions()
|-- client/                           # React + Vite + TypeScript web client
|   |-- index.html
|   |-- package.json
|   |-- vite.config.ts                # proxies /api -> backend :8000 in dev
|   |-- public/
|   `-- src/
|       |-- main.tsx
|       |-- App.tsx                    # all app state (useState)
|       |-- api.ts                     # transport layer
|       |-- types.ts                   # TS mirrors of the Pydantic schemas
|       `-- components/                # DraftBoard, ChampionGrid, etc.
|-- pyproject.toml
|-- uv.lock
|-- README.md
`-- TODO.md
```

## Setup

```powershell
python -m pip install -e .
ldt init-db
```

A `uv.lock` is checked in, so `uv sync` works as a faster/reproducible
alternative to plain pip.

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

All commands are subcommands of a single `ldt` console script:

```powershell
ldt init-db              # create Postgres schema
ldt update-challengers   # refresh Challenger player list from Riot API
ldt run-match-sync       # ingest match data for all Challenger players
ldt daily-maintenance    # detect patch changes and archive stale data
```

## Running the app

Backend (FastAPI on :8000):

```powershell
fastapi dev backend/main.py   # or: uvicorn backend.main:app
```

Frontend (React + Vite dev server on :5173; requires Node.js):

```powershell
cd client
npm install
npm run dev
```

The Vite dev server proxies `/api` to the backend on :8000, so client code uses
relative paths in development. Two HTTP endpoints back the client:

- `GET /api/champions` — full `champ_id -> {name, sprite_url}` dictionary
  (fetched once per session/patch so the client can map ids to names/icons)
- `POST /api/recommend` — deals strictly in `champ_id` ints; returns ranked
  champion suggestions with a single `win_chance` score each

## Scheduling (GitHub Actions)

Two scheduled workflows in `.github/workflows/` run the ingestion pipeline —
no manual invocation needed:

- `daily-maintenance.yml` — once a day (~3 AM PT); runs `ldt daily-maintenance`
  then `ldt update-challengers`
- `match-sync.yml` — every 12 hours; runs `ldt run-match-sync`

Both are also `workflow_dispatch`-triggerable. The runner reads `RIOT_API_KEY`
and `DATABASE_URL` from the repo's Actions secrets (no `.env` needed there).

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
- `client/` is a React + Vite + TypeScript web client for the draft flow; all
  app state lives in `src/App.tsx`.
- The database is Postgres hosted on Neon; `DATABASE_URL` in `.env` points at it.
