# lol_draft_tool

League of Legends draft data tooling for collecting challenger match data and
building champion relationship statistics.

## Project Structure

```text
lol_draft_tool/
|-- db/
|   `-- lol_draft.sqlite3
|-- scripts/
|   |-- init_db.py
|   `-- run_match_sync.py
|-- src/
|   |-- core/
|   |   `-- config.py
|   |-- db/
|   |   |-- connection.py
|   |   |-- init_db.py
|   |   |-- queries.py
|   |   `-- schema.py
|   |-- external/
|   |   `-- riot_api.py
|   |-- pipeline/
|   |   `-- match_sync.py
|   |-- services/
|   |   `-- match_service.py
|   `-- utils/
|       `-- helpers.py
|-- tests/
|-- .env
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
python scripts/run_match_sync.py
```
