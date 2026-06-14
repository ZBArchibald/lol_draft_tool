from src.db.connection import db_connection
from src.db.queries import (
    get_challenger_puuids,
    get_metadata_value,
    insert_processed_match,
    match_in_db,
    update_champion_relationships,
    update_champion_stats,
)
from src.external.riot_api import get_match_data, get_match_ids
from src.utils.helpers import truncate_patch_id


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


def is_on_current_patch(match_data: list) -> bool:
    current_patch = get_metadata_value("current_patch")
    match_patch = truncate_patch_id(match_data["info"]["gameVersion"])
    return match_patch == current_patch


def process_match(match_data: dict) -> None:
    with db_connection() as conn:
        insert_processed_match(conn, match_data["metadata"]["matchId"])
        participants = match_data["info"]["participants"]
        update_champion_relationships(conn, participants)
        update_champion_stats(conn, participants)
