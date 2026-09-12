# Cloud Run serves the FastAPI API only. Ingestion (ldt run-match-sync etc.)
# runs on GitHub Actions, so this image never needs RIOT_API_KEY.
FROM python:3.12-slim

# Faster, quieter, no .pyc clutter in the layer.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install deps first (own layer) so code edits don't re-run the dependency solve.
# psycopg[binary] ships its own libpq wheel, so no system postgres client needed.
COPY pyproject.toml ./
COPY backend ./backend
RUN pip install --upgrade pip && pip install .

# Cloud Run injects $PORT (8080 by default) and expects the app to listen on it.
# Shell form so $PORT expands at runtime; fastapi run binds 0.0.0.0 in prod mode.
EXPOSE 8080
CMD fastapi run backend/main.py --port ${PORT:-8080}
