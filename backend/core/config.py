import os
from pathlib import Path

from dotenv import load_dotenv


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# override=True: the project .env is the source of truth locally, beating any
# stale shell/system environment variables of the same name
load_dotenv(_PROJECT_ROOT / ".env", override=True)

API_KEY = os.getenv("RIOT_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Extra CORS origins for the deployed frontend, comma-separated, e.g.
# FRONTEND_ORIGINS="https://myapp.vercel.app,https://www.mydomain.com".
# The localhost dev origins are always allowed (see backend/main.py); this only
# adds production origins so they don't have to be hardcoded in the image.
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
    if origin.strip()
]

# Per-client cap on API requests: at most RATE_LIMIT_REQUESTS in any rolling
# RATE_LIMIT_WINDOW_SECONDS. Enforced in backend/api/rate_limit.py.
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW_SECONDS = 5 * 60

QUEUE_ID = 420
REGION = "na1"
MATCH_REGION = "americas"
