import os
from pathlib import Path

from dotenv import load_dotenv


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

load_dotenv(_PROJECT_ROOT / ".env")

API_KEY = os.getenv("RIOT_API_KEY")
DB_PATH = Path(os.getenv("LOL_DRAFT_DB_PATH", str(_PROJECT_ROOT / "db" / "lol_draft.sqlite3"))).resolve()

QUEUE_ID = 420
REGION = "na1"
MATCH_REGION = "americas"
