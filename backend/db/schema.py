import logging

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
        currently_challenger BOOLEAN DEFAULT TRUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS matches (
        match_id TEXT PRIMARY KEY,

        blueside_win BOOLEAN,

        blueside_top_champ_id INTEGER,
        blueside_jungle_champ_id INTEGER,
        blueside_middle_champ_id INTEGER,
        blueside_bottom_champ_id INTEGER,
        blueside_support_champ_id INTEGER,

        redside_jungle_champ_id INTEGER,
        redside_top_champ_id INTEGER,
        redside_middle_champ_id INTEGER,
        redside_bottom_champ_id INTEGER,
        redside_support_champ_id INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS champion_stats (
        champ_id INTEGER PRIMARY KEY,
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
        champ_id TEXT,
        other_champ_id TEXT,
        wins_as_ally INTEGER DEFAULT 0,
        games_as_ally INTEGER DEFAULT 0,
        wins_as_opponent INTEGER DEFAULT 0,
        games_as_opponent INTEGER DEFAULT 0,
        PRIMARY KEY (champ_id, other_champ_id)
    )
    """
    
)


def initialize_database() -> None:
    with db_connection() as conn:
        cursor = conn.cursor()
        for statement in SCHEMA_STATEMENTS:
            cursor.execute(statement)
    LOG.info("Database schema initialized")
