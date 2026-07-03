import psycopg

from backend.db.connection import db_connection

# metadata queries
def get_metadata_value(key: str) -> str:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = %s", (key,))
        row = cursor.fetchone()
        if not row:
            raise KeyError(f"Metadata key '{key}' not found")
        return row[0]


def update_metadata(key: str, value: str) -> None:
    with db_connection() as conn:
        conn.execute(
            """
            INSERT INTO metadata (key, value)
            VALUES (%s, %s)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (key, value),
        )


def get_challenger_puuids() -> list[str]:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT puuid FROM challenger_players")
        return [row[0] for row in cursor.fetchall()]


def replace_challenger_players(puuids: list[str]) -> None:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM challenger_players")

        cursor.executemany(
            "INSERT INTO challenger_players (puuid, currently_challenger) VALUES (%s, TRUE)",
            [(puuid,) for puuid in puuids],
        )


def get_processed_match_ids(match_ids: list[str]) -> set[str]:
    if not match_ids:
        return set()
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT match_id FROM processed_matches WHERE match_id = ANY(%s)",
            (match_ids,),
        )
        return {row[0] for row in cursor.fetchall()}


def insert_processed_matches(conn: psycopg.Connection, match_ids: list[str]) -> None:
    if not match_ids:
        return
    conn.cursor().executemany(
        "INSERT INTO processed_matches (match_id) VALUES (%s)",
        [(match_id,) for match_id in match_ids],
    )


def clear_processed_matches(conn: psycopg.Connection) -> None:
    conn.execute("DELETE FROM processed_matches")


def clear_champion_relationships(conn: psycopg.Connection) -> None:
    conn.execute("DELETE FROM champion_relationships")


def clear_challenger_players(conn: psycopg.Connection) -> None:
    conn.execute("DELETE FROM challenger_players")


def clear_all_match_data(conn: psycopg.Connection) -> None:
    clear_processed_matches(conn)
    clear_champion_relationships(conn)
    clear_challenger_players(conn)


def upsert_champion_relationships(
    conn: psycopg.Connection,
    rows: list[tuple[str, str, int, int, int, int]],
) -> None:
    """rows: (champion, other_champion, wins_as_ally, games_as_ally, wins_as_opponent, games_as_opponent)"""
    if not rows:
        return
    conn.cursor().executemany(
        """
        INSERT INTO champion_relationships (
            champion_name,
            other_champion_name,
            wins_as_ally,
            games_as_ally,
            wins_as_opponent,
            games_as_opponent
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT(champion_name, other_champion_name)
        DO UPDATE SET
            wins_as_ally = champion_relationships.wins_as_ally + excluded.wins_as_ally,
            games_as_ally = champion_relationships.games_as_ally + excluded.games_as_ally,
            wins_as_opponent = champion_relationships.wins_as_opponent + excluded.wins_as_opponent,
            games_as_opponent = champion_relationships.games_as_opponent + excluded.games_as_opponent
        """,
        rows,
    )


def upsert_champion_stats(
    conn: psycopg.Connection,
    rows: list[tuple[str, int, int, int, int, int, int, int]],
) -> None:
    """rows: (champion, wins, games, games_top, games_jungle, games_mid, games_bot, games_support)"""
    if not rows:
        return
    conn.cursor().executemany(
        """
        INSERT INTO champion_stats (
            champion_name, wins, games,
            games_top, games_jungle, games_mid, games_bot, games_support
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(champion_name)
        DO UPDATE SET
            wins = champion_stats.wins + excluded.wins,
            games = champion_stats.games + excluded.games,
            games_top = champion_stats.games_top + excluded.games_top,
            games_jungle = champion_stats.games_jungle + excluded.games_jungle,
            games_mid = champion_stats.games_mid + excluded.games_mid,
            games_bot = champion_stats.games_bot + excluded.games_bot,
            games_support = champion_stats.games_support + excluded.games_support
        """,
        rows,
    )

# draft_service queries

def get_candidate_champions(position: str, minimum_rolerate: float) -> list[str]:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT champion_name FROM champion_stats
            WHERE (games_{position} + 0.0) / games >= %s
            """,
            (minimum_rolerate,),
        )
        rows = cursor.fetchall()
        return [row[0] for row in rows]


def get_winrate(champion: str) -> float:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT wins, games FROM champion_stats WHERE champion_name = %s",
            (champion,)
        )
        row = cursor.fetchone()
        if not row or row[1] == 0:
            return 0.5
        return row[0] / row[1]


def get_champion_relationships(champion: str, other_champions: list[str]) -> dict[str, dict]:
    if not other_champions:
        return {}
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT other_champion_name, wins_as_ally, games_as_ally, wins_as_opponent, games_as_opponent
            FROM champion_relationships
            WHERE champion_name = %s
            AND other_champion_name = ANY(%s)
            """,
            (champion, other_champions),
        )
        return {
            row[0]: {
                "wins_as_ally": row[1],
                "games_as_ally": row[2],
                "wins_as_opponent": row[3],
                "games_as_opponent": row[4],
            }
            for row in cursor.fetchall()
        }

