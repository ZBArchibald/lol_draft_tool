import sqlite3

from src.db.connection import db_connection, get_connection


def get_metadata_value(key: str) -> str:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        raise KeyError(f"Metadata key '{key}' not found")
    return row[0]


def update_metadata(key: str, value: str) -> None:
    with db_connection() as conn:
        conn.execute(
            """
            INSERT INTO metadata (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (key, value),
        )


def get_challenger_puuids() -> list[str]:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT puuid FROM challenger_players")
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()


def replace_challenger_players(puuids: list[str]) -> None:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM challenger_players")

        for puuid in puuids:
            cursor.execute(
                "INSERT INTO challenger_players (puuid, currently_challenger) VALUES (?, 1)",
                [puuid],
            )


def match_in_db(match_id: str) -> bool:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM processed_matches WHERE match_id = ?", (match_id,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def insert_processed_match(conn: sqlite3.Connection, match_id: str) -> None:
    conn.execute(
        "INSERT INTO processed_matches (match_id) VALUES (?)",
        [match_id],
    )
