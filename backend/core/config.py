import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")
DB_PATH = Path(os.getenv("LOL_DRAFT_DB_PATH", "db/lol_draft.sqlite3")).resolve()

QUEUE_ID = 420
REGION = "na1"
MATCH_REGION = "americas"
