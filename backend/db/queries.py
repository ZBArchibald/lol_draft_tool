import sqlite3

from backend.db.connection import db_connection


def get_metadata_value(key: str) -> str:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        row = cursor.fetchone()
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
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT puuid FROM challenger_players")
        return [row[0] for row in cursor.fetchall()]


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
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM processed_matches WHERE match_id = ?", (match_id,))
        return cursor.fetchone() is not None


def insert_processed_match(conn: sqlite3.Connection, match_id: str) -> None:
    conn.execute(
        "INSERT INTO processed_matches (match_id) VALUES (?)",
        [match_id],
    )


def clear_processed_matches(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM processed_matches")


def clear_champion_relationships(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM champion_relationships")


def clear_challenger_players(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM challenger_players")


def clear_all_match_data(conn: sqlite3.Connection) -> None:
    clear_processed_matches(conn)
    clear_champion_relationships(conn)
    clear_challenger_players(conn)


def update_champion_relationships(conn, participants: list[dict]) -> None:
    cursor = conn.cursor()

    for participant_a in participants:
        for participant_b in participants:
            if participant_a == participant_b:
                continue

            champion_a = participant_a["championName"]
            champion_b = participant_b["championName"]
            ally = participant_a["teamId"] == participant_b["teamId"]
            won = participant_a["win"]

            if ally:
                win_column = "wins_as_ally"
                game_column = "games_as_ally"
            else:
                win_column = "wins_as_opponent"
                game_column = "games_as_opponent"

            cursor.execute(
                f"""
                INSERT INTO champion_relationships (
                    champion_name,
                    other_champion_name,
                    {win_column},
                    {game_column}
                )
                VALUES (?, ?, ?, 1)
                ON CONFLICT(champion_name, other_champion_name)
                DO UPDATE SET
                    {game_column} = {game_column} + 1,
                    {win_column} = {win_column} + excluded.{win_column}
                """,
                (champion_a, champion_b, int(won)),
            )


def update_champion_stats(conn, participants: list[dict]) -> None:
    cursor = conn.cursor()

    for participant in participants:
        champion = participant["championName"]
        position = participant["teamPosition"]
        won = participant["win"]

        position_map = {
            "TOP": "games_top",
            "JUNGLE": "games_jungle",
            "MIDDLE": "games_mid",
            "BOTTOM": "games_bot",
            "UTILITY": "games_support",
        }

        position_column = position_map.get(position)
        if not position_column:
            continue

        cursor.execute(
            f"""
            INSERT INTO champion_stats (champion_name, wins, games, {position_column})
            VALUES (?, ?, 1, 1)
            ON CONFLICT(champion_name)
            DO UPDATE SET
                games = games + 1,
                wins = wins + excluded.wins,
                {position_column} = {position_column} + 1
            """,
            (champion, int(won)),
        )
