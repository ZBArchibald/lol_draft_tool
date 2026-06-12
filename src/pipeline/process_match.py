from src.db.connection import db_connection
from src.db.queries import insert_processed_match


def process_match(match_data: dict) -> None:
    with db_connection() as conn:
        insert_processed_match(conn, match_data["metadata"]["matchId"])
        update_champion_relationships(conn, match_data)
        update_champion_stats(conn, match_data)


def update_champion_relationships(conn, match_data: dict) -> None:
    cursor = conn.cursor()
    participants = match_data["info"]["participants"]

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


def update_champion_stats(conn, match_data: dict) -> None:
    cursor = conn.cursor()
    participants = match_data["info"]["participants"]

    for participant in participants:
        champion = participant["championName"]
        won = participant["win"]

        cursor.execute(
            """
            INSERT INTO champion_stats (champion_name, wins, games)
            VALUES (?, ?, 1)
            ON CONFLICT(champion_name)
            DO UPDATE SET
                games = games + 1,
                wins = wins + excluded.wins
            """,
            (champion, int(won)),
        )
