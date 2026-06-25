import logging

from backend.core.config import DB_PATH
from backend.db.connection import db_connection

LOG = logging.getLogger(__name__)


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS challenger_players (
        puuid TEXT PRIMARY KEY,
        currently_challenger BOOLEAN DEFAULT 1,
        last_processed_match_retrieval_time TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS processed_matches (
        match_id TEXT PRIMARY KEY
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS champion_stats (
        champion_name TEXT PRIMARY KEY,
        wins INTEGER DEFAULT 0,
        games INTEGER DEFAULT 0,
        games_top INTEGER DEFAULT 0,
        games_jungle INTEGER DEFAULT 0,
        games_mid INTEGER DEFAULT 0,
        games_bot INTEGER DEFAULT 0,
        games_support INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS champion_relationships (
        champion_name TEXT,
        other_champion_name TEXT,
        wins_as_ally INTEGER DEFAULT 0,
        games_as_ally INTEGER DEFAULT 0,
        wins_as_opponent INTEGER DEFAULT 0,
        games_as_opponent INTEGER DEFAULT 0,
        PRIMARY KEY (champion_name, other_champion_name)
    )
    """
    
)


def initialize_database() -> None:
    with db_connection() as conn:
        cursor = conn.cursor()
        for statement in SCHEMA_STATEMENTS:
            cursor.execute(statement)
    LOG.info("Database initialized at %s", DB_PATH)
