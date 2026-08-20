from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import champions_router, recommendation_router

app = FastAPI(title="LoL Draft Tool API")

# Dev-only: the frontend runs on a different origin (e.g. localhost:5173) than
# this API (localhost:8000), so the browser needs an explicit CORS allowlist.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(champions_router)
app.include_router(recommendation_router)