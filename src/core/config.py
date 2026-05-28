import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_DIR = ROOT_DIR / "db"

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")

QUEUE_ID = 420
REGION = "na1"
MATCH_REGION = "americas"
DB_PATH = DB_DIR / "lol_draft.sqlite3"
