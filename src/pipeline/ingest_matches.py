from src.db.queries import get_challenger_puuids, get_metadata_value, match_in_db
from src.external.riot_api import get_match_data, get_match_ids
from src.pipeline.process_match import process_match
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

def is_on_current_patch(match_data: dict) -> bool:
    current_patch = get_metadata_value("current_patch")
    match_patch = truncate_patch_id(match_data["info"]["gameVersion"])
    return match_patch == current_patch