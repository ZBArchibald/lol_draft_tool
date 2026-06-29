import logging

from backend.db.connection import db_connection
from backend.db.queries import (
    get_challenger_puuids,
    get_metadata_value,
    insert_processed_match,
    match_in_db,
    update_champion_relationships,
    update_champion_stats,
)
from backend.external.riot_api import get_match_data, get_match_ids
from backend.utils.helpers import truncate_patch_id

LOG = logging.getLogger(__name__)


def sync_all_challenger_matches(batch_size: int = 20) -> None:
    puuids = get_challenger_puuids()
    LOG.info("Starting match sync for %d challenger players", len(puuids))
    
    count = 1
    for puuid in puuids:
        sync_player_matches(puuid, batch_size)
        LOG.info("Player %d synced", count)
    LOG.info("Match sync complete")


def sync_player_matches(puuid: str, batch_size: int = 20) -> None:
    current_patch = get_metadata_value("current_patch")
    LOG.info("Syncing player %s (patch: %s)", puuid, current_patch)
    start_index = 0
    stop_sync = False
    processed = 0

    while not stop_sync:
        match_batch = get_match_ids(puuid, start_index, batch_size)

        if not match_batch:
            break

        for match_id in match_batch:
            if match_in_db(match_id):
                LOG.debug("Stopping sync for %s: match %s already in DB", puuid, match_id)
                stop_sync = True
                break

            match_data = get_match_data(match_id)
            if not is_on_current_patch(match_data, current_patch):
                LOG.debug("Stopping sync for %s: match %s not on current patch", puuid, match_id)
                stop_sync = True
                break

            LOG.debug("Processing match %s", match_id)
            process_match(match_data)
            processed += 1

        start_index += batch_size

    LOG.info("Finished player %s: %d new matches processed", puuid, processed)


def is_on_current_patch(match_data: dict, current_patch: str) -> bool:
    match_patch = truncate_patch_id(match_data["info"]["gameVersion"])
    return match_patch == current_patch


def process_match(match_data: dict) -> None:
    with db_connection() as conn:
        insert_processed_match(conn, match_data["metadata"]["matchId"])
        participants = match_data["info"]["participants"]
        update_champion_relationships(conn, participants)
        update_champion_stats(conn, participants)
