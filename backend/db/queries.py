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


def upsert_champions(conn: psycopg.Connection, rows: list[tuple[int, str]]) -> None:
    """rows: (champ_id, name)"""
    if not rows:
        return
    conn.cursor().executemany(
        """
        INSERT INTO champions (champ_id, name)
        VALUES (%s, %s)
        ON CONFLICT (champ_id) DO UPDATE SET name = excluded.name
        """,
        rows,
    )


def get_all_champions() -> dict[int, str]:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT champ_id, name FROM champions")
        return {row[0]: row[1] for row in cursor.fetchall()}


def get_challenger_puuids() -> list[str]:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT puuid FROM challenger_players")
        return [row[0] for row in cursor.fetchall()]


def replace_challenger_players(puuids: list[str]) -> None:
    with db_connection() as conn:
        cursor = conn.cursor()
        # drop players who fell off the ladder; anyone still on it keeps their row
        # (and last_synced_match_id) via the upsert below instead of being recreated
        cursor.execute(
            "DELETE FROM challenger_players WHERE NOT (puuid = ANY(%s))",
            (puuids,),
        )

        cursor.executemany(
            """
            INSERT INTO challenger_players (puuid, currently_challenger)
            VALUES (%s, TRUE)
            ON CONFLICT (puuid) DO UPDATE SET currently_challenger = TRUE
            """,
            [(puuid,) for puuid in puuids],
        )


def get_last_synced_match_id(puuid: str) -> str | None:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_synced_match_id FROM challenger_players WHERE puuid = %s",
            (puuid,),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def update_last_synced_match_id(conn: psycopg.Connection, puuid: str, match_id: str) -> None:
    conn.execute(
        "UPDATE challenger_players SET last_synced_match_id = %s WHERE puuid = %s",
        (match_id, puuid),
    )


def get_processed_match_ids(match_ids: list[str]) -> set[str]:
    if not match_ids:
        return set()
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT match_id FROM matches WHERE match_id = ANY(%s)",
            (match_ids,),
        )
        return {row[0] for row in cursor.fetchall()}


def clear_matches(conn: psycopg.Connection) -> None:
    conn.execute("DELETE FROM matches")


def clear_champion_relationships(conn: psycopg.Connection) -> None:
    conn.execute("DELETE FROM champion_relationships")


def clear_champion_stats(conn: psycopg.Connection) -> None:
    conn.execute("DELETE FROM champion_stats")


def clear_challenger_players(conn: psycopg.Connection) -> None:
    conn.execute("DELETE FROM challenger_players")


def insert_matches(conn: psycopg.Connection, rows: list[dict]) -> None:
    """rows: dicts with keys match_id, blueside_win, and
    {blueside,redside}_{top,jungle,middle,bottom,support}_champ_id"""
    if not rows:
        return
    conn.cursor().executemany(
        """
        INSERT INTO matches (
            match_id, blueside_win,
            blueside_top_champ_id, blueside_jungle_champ_id, blueside_middle_champ_id,
            blueside_bottom_champ_id, blueside_support_champ_id,
            redside_top_champ_id, redside_jungle_champ_id, redside_middle_champ_id,
            redside_bottom_champ_id, redside_support_champ_id
        )
        VALUES (
            %(match_id)s, %(blueside_win)s,
            %(blueside_top_champ_id)s, %(blueside_jungle_champ_id)s, %(blueside_middle_champ_id)s,
            %(blueside_bottom_champ_id)s, %(blueside_support_champ_id)s,
            %(redside_top_champ_id)s, %(redside_jungle_champ_id)s, %(redside_middle_champ_id)s,
            %(redside_bottom_champ_id)s, %(redside_support_champ_id)s
        )
        ON CONFLICT (match_id) DO NOTHING
        """,
        rows,
    )


def clear_player_data(conn: psycopg.Connection) -> None:
    clear_matches(conn)
    clear_champion_relationships(conn)
    clear_champion_stats(conn)
    clear_challenger_players(conn)


def upsert_champion_relationships(
    conn: psycopg.Connection,
    rows: list[tuple[int, int, int, int, int, int]],
) -> None:
    """rows: (champ_id, other_champ_id, wins_as_ally, games_as_ally, wins_as_opponent, games_as_opponent)"""
    if not rows:
        return
    conn.cursor().executemany(
        """
        INSERT INTO champion_relationships (
            champ_id,
            other_champ_id,
            wins_as_ally,
            games_as_ally,
            wins_as_opponent,
            games_as_opponent
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT(champ_id, other_champ_id)
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
    rows: list[tuple[int, int, int, int, int, int, int, int]],
) -> None:
    """rows: (champ_id, wins, games, games_top, games_jungle, games_mid, games_bot, games_support)"""
    if not rows:
        return
    conn.cursor().executemany(
        """
        INSERT INTO champion_stats (
            champ_id, wins, games,
            games_top, games_jungle, games_mid, games_bot, games_support
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(champ_id)
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

def get_candidate_champions(position: str, minimum_rolerate: float) -> list[int]:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT champ_id FROM champion_stats
            WHERE (games_{position} + 0.0) / games >= %s
            """,
            (minimum_rolerate,),
        )
        rows = cursor.fetchall()
        return [row[0] for row in rows]


def get_winrates(champions: list[int]) -> dict[int, float]:
    """Returns champ_id -> winrate for every champion in `champions` that has games played.
    Champions absent from the result (not found, or 0 games) should be treated as a 0.5 baseline by the caller."""
    if not champions:
        return {}
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT champ_id, wins, games FROM champion_stats WHERE champ_id = ANY(%s)",
            (champions,),
        )
        return {
            row[0]: row[1] / row[2]
            for row in cursor.fetchall()
            if row[2] > 0
        }


def get_champion_relationships_bulk(
    champions: list[int], other_champions: list[int]
) -> dict[int, dict[int, dict]]:
    """Returns champ_id -> other_champ_id -> relationship stats, for every (champ_id, other_champ_id)
    pair in the cross product of `champions` and `other_champions` that has recorded games."""
    if not champions or not other_champions:
        return {}
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT champ_id, other_champ_id, wins_as_ally, games_as_ally, wins_as_opponent, games_as_opponent
            FROM champion_relationships
            WHERE champ_id = ANY(%s)
            AND other_champ_id = ANY(%s)
            """,
            (champions, other_champions),
        )
        relationships: dict[int, dict[int, dict]] = {}
        for row in cursor.fetchall():
            relationships.setdefault(row[0], {})[row[1]] = {
                "wins_as_ally": row[2],
                "games_as_ally": row[3],
                "wins_as_opponent": row[4],
                "games_as_opponent": row[5],
            }
        return relationships

