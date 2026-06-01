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
