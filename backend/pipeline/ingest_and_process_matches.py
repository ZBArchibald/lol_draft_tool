import logging

from backend.db.connection import db_connection
from backend.db.queries import (
    get_challenger_puuids,
    get_metadata_value,
    get_processed_match_ids,
    insert_processed_matches,
    upsert_champion_relationships,
    upsert_champion_stats,
)
from backend.external.riot_api import get_match_data, get_match_ids

LOG = logging.getLogger(__name__)

# index into the stats row [wins, games, games_top, games_jungle, games_mid, games_bot, games_support]
_POSITION_INDEX = {
    "TOP": 2,
    "JUNGLE": 3,
    "MIDDLE": 4,
    "BOTTOM": 5,
    "UTILITY": 6,
}


def sync_all_challenger_matches(batch_size: int = 20) -> None:
    puuids = get_challenger_puuids()
    LOG.info("Starting match sync for %d challenger players", len(puuids))

    for count, puuid in enumerate(puuids, start=1):
        sync_player_matches(puuid, batch_size)
        LOG.info("Player %d/%d synced", count, len(puuids))
    LOG.info("Match sync complete")


def sync_player_matches(puuid: str, batch_size: int = 20) -> None:
    current_patch = get_metadata_value("current_patch")
    LOG.info("Syncing player %s (patch: %s)", puuid, current_patch)
    start_index = 0
    stop_sync = False

    match_ids: list[str] = []
    stats: dict[str, list[int]] = {}
    relationships: dict[tuple[str, str], list[int]] = {}

    while not stop_sync:
        match_batch = get_match_ids(puuid, start_index, batch_size)

        if not match_batch:
            break

        already_processed = get_processed_match_ids(match_batch)

        for match_id in match_batch:
            if match_id in already_processed:
                LOG.debug("Stopping sync for %s: match %s already in DB", puuid, match_id)
                stop_sync = True
                break

            match_data = get_match_data(match_id)
            if not is_on_current_patch(match_data, current_patch):
                LOG.debug("Stopping sync for %s: match %s not on current patch", puuid, match_id)
                stop_sync = True
                break

            LOG.debug("Aggregating match %s", match_id)
            match_ids.append(match_id)
            aggregate_match(match_data, stats, relationships)
            if len(match_ids) % 10 == 0:
                LOG.info("Fetched %d matches for %s", len(match_ids), puuid)

        start_index += batch_size

    flush_player_data(match_ids, stats, relationships)
    LOG.info("Finished player %s: %d new matches processed", puuid, len(match_ids))


def is_on_current_patch(match_data: dict, current_patch: str) -> bool:
    #retrive and build truncated patch from match_data
    major, minor, *_ = match_data["info"]["gameVersion"].split(".")
    match_patch = f"{major}.{minor}"

    return match_patch == current_patch


def aggregate_match(
    match_data: dict,
    stats: dict[str, list[int]],
    relationships: dict[tuple[str, str], list[int]],
) -> None:
    participants = match_data["info"]["participants"]

    for participant in participants:
        position_index = _POSITION_INDEX.get(participant["teamPosition"])
        if position_index is None:
            continue
        row = stats.setdefault(participant["championName"], [0] * 7)
        row[0] += int(participant["win"])
        row[1] += 1
        row[position_index] += 1

    for participant_a in participants:
        for participant_b in participants:
            if participant_a is participant_b:
                continue
            key = (participant_a["championName"], participant_b["championName"])
            # [wins_as_ally, games_as_ally, wins_as_opponent, games_as_opponent]
            row = relationships.setdefault(key, [0] * 4)
            if participant_a["teamId"] == participant_b["teamId"]:
                row[0] += int(participant_a["win"])
                row[1] += 1
            else:
                row[2] += int(participant_a["win"])
                row[3] += 1


def flush_player_data(
    match_ids: list[str],
    stats: dict[str, list[int]],
    relationships: dict[tuple[str, str], list[int]],
) -> None:
    if not match_ids:
        return
    with db_connection() as conn:
        with conn.pipeline():
            insert_processed_matches(conn, match_ids)
            upsert_champion_stats(
                conn,
                [(champion, *row) for champion, row in stats.items()],
            )
            upsert_champion_relationships(
                conn,
                [(champion, other, *row) for (champion, other), row in relationships.items()],
            )
