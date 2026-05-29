from src.db.queries import get_challenger_puuids, match_in_db, get_metadata_value, insert_processed_match
from src.external.riot_api import get_match_data, get_match_ids
from src.db.connection import db_connection
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


def sync_all_challenger_matches(batch_size: int = 20) -> None:
    for puuid in get_challenger_puuids():
        sync_player_matches(puuid, batch_size)


def sync_player_matches(puuid: str, batch_size: int = 20) -> None:
    start_index = 0
    stop_sync = False

    while not stop_sync:
        match_batch = get_match_ids(puuid, start_index, batch_size)
        
        # if there are no more matches to fetch, break the loop
        if not match_batch:
            break

        for match_id in match_batch:
            # stop syncing if we encounter a match that's already in the database
            if match_in_db(match_id):
                stop_sync = True
                break
            
            # stop syncing if we encounter a match that's not on the current patch
            match_data = get_match_data(match_id)
            if not is_on_current_patch(match_data):
                stop_sync = True
                break

            process_match(match_data)

        start_index += batch_size
