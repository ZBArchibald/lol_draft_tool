from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import champions_router, recommendation_router
from backend.core.config import FRONTEND_ORIGINS

app = FastAPI(title="LoL Draft Tool API")

# The frontend runs on a different origin than this API, so the browser needs an
# explicit CORS allowlist. The localhost origins cover local dev; deployed
# frontend origins come from the FRONTEND_ORIGINS env var (see config.py) so the
# production URL isn't baked into the image.
_DEV_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_DEV_ORIGINS + FRONTEND_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(champions_router)
app.include_router(recommendation_router)