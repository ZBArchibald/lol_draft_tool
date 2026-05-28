from src.db.connection import db_connection
from src.db.queries import get_metadata_value, insert_processed_match
from src.utils.helpers import truncate_patch_id


def is_on_current_patch(match_data: dict) -> bool:
    current_patch = get_metadata_value("current_patch")
    match_patch = truncate_patch_id(match_data["info"]["gameVersion"])
    return match_patch == current_patch


def process_match(match_data: dict) -> None:
    with db_connection() as conn:
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

    insert_processed_match(match_data["metadata"]["matchId"])
