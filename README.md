# lol_draft_tool

League of Legends draft data tooling for collecting challenger match data and
building champion relationship statistics.

## Project Structure

```text
lol_draft_tool/
|-- db/
|   `-- lol_draft.sqlite3
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
|   |   |-- init_db.py
|   |   |-- queries.py
|   |   `-- schema.py
|   |-- external/
|   |   |-- __init__.py
|   |   `-- riot_api.py
|   |-- pipeline/
|   |   |-- __init__.py
|   |   |-- challenger_update.py
|   |   |-- match_ingest.py
|   |   |-- match_process.py
|   |   |-- match_sync.py
|   |   `-- patch_maintenance.py
|   |-- services/
|   |   |-- __init__.py
|   `-- utils/
|       |-- __init__.py
|       `-- helpers.py
|-- tests/
|-- .env
|-- .gitignore
|-- README.md
`-- requirements.txt
```

## Setup

```powershell
pip install -r requirements.txt
python scripts/init_db.py
```

Add your Riot API key to `.env`:

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

## Packaging (recommended)

This project now includes minimal packaging so you can install it in editable
mode and avoid `sys.path` hacks in the `scripts/` files.

Install editable:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

After installing editable you can run the scripts directly (they use
top-level imports):

```bash
python scripts/run_match_sync.py
python scripts/update_challengers.py
```

Files added/changed in this refactor:
- `pyproject.toml` (minimal build-system)
- `setup.cfg` (package metadata / dependencies)
- `scripts/*` — cleaned `sys.path` insertion and use top-level imports
- split `src/pipeline/match_sync.py` into `src/pipeline/match_ingest.py` and
  `src/pipeline/match_process.py`, with `src/pipeline/match_sync.py` kept as a
  thin re-export shim

If you'd like, I can add a short `pytest` example and CI config next.
