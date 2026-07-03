import os
from pathlib import Path

from dotenv import load_dotenv


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# override=True: the project .env is the source of truth locally, beating any
# stale shell/system environment variables of the same name
load_dotenv(_PROJECT_ROOT / ".env", override=True)

API_KEY = os.getenv("RIOT_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

QUEUE_ID = 420
REGION = "na1"
MATCH_REGION = "americas"
