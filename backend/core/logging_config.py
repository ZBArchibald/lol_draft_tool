import logging

# choose INFO level for player sync start/finish with match count, patch check result, challenger ladder update, DB init path
# choose DEBUG level for per-match skip reasons (already in DB, patch mismatch) and per-match processing
def setup_logging(level: int = logging.DEBUG) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
