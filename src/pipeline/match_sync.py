from src.db.queries import (
    get_challenger_puuids,
    match_in_db,
    replace_challenger_players,
    update_metadata,
)
from src.external.riot_api import (
    get_challenger_league_puuids,
    get_current_patch,
    get_match_data,
    get_match_ids,
)
from src.services.match_service import is_on_current_patch, process_match


def update_current_patch() -> str:
    current_patch = get_current_patch()
    update_metadata("current_patch", current_patch)
    return current_patch


def update_challenger_players() -> None:
    puuids = get_challenger_league_puuids()
    replace_challenger_players(puuids)


def sync_all_challenger_matches(batch_size: int = 20) -> None:
    for puuid in get_challenger_puuids():
        sync_player_matches(puuid, batch_size)


def sync_player_matches(puuid: str, batch_size: int = 20) -> None:
    start_index = 0
    stop_sync = False

    while not stop_sync:
        match_batch = get_match_ids(puuid, start_index, batch_size)
        if not match_batch:
            break

        for match_id in match_batch:
            if match_in_db(match_id):
                stop_sync = True
                break

            match_data = get_match_data(match_id)
            if not is_on_current_patch(match_data):
                stop_sync = True
                break

            process_match(match_data)

        start_index += batch_size
