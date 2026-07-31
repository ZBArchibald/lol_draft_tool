import logging

from backend.db.connection import db_connection
from backend.db.queries import (
    get_challenger_puuids,
    get_last_synced_match_id,
    get_metadata_value,
    get_processed_match_ids,
    insert_matches,
    update_last_synced_match_id,
    upsert_champion_relationships,
    upsert_champion_stats,
)
from backend.external.riot_api import get_match_data, get_match_ids

LOG = logging.getLogger(__name__)

# teamPosition -> the champion_stats column that tracks games played there
_POSITION_FIELD = {
    "TOP": "games_top",
    "JUNGLE": "games_jungle",
    "MIDDLE": "games_mid",
    "BOTTOM": "games_bot",
    "UTILITY": "games_support",
}

# teamPosition -> the matches column suffix for that role
_TEAM_POSITION_SUFFIX = {
    "TOP": "top",
    "JUNGLE": "jungle",
    "MIDDLE": "middle",
    "BOTTOM": "bottom",
    "UTILITY": "support",
}

_BLUE_TEAM_ID = 100

_EMPTY_MATCH_ROW = {
    "blueside_win": None,
    "blueside_top_champ_id": None,
    "blueside_jungle_champ_id": None,
    "blueside_middle_champ_id": None,
    "blueside_bottom_champ_id": None,
    "blueside_support_champ_id": None,
    "redside_top_champ_id": None,
    "redside_jungle_champ_id": None,
    "redside_middle_champ_id": None,
    "redside_bottom_champ_id": None,
    "redside_support_champ_id": None,
}

_EMPTY_STATS_ROW = {
    "wins": 0,
    "games": 0,
    "games_top": 0,
    "games_jungle": 0,
    "games_mid": 0,
    "games_bot": 0,
    "games_support": 0,
}

_EMPTY_RELATIONSHIP_ROW = {
    "wins_as_ally": 0,
    "games_as_ally": 0,
    "wins_as_opponent": 0,
    "games_as_opponent": 0,
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
    last_synced_match_id = get_last_synced_match_id(puuid)
    LOG.info("Syncing player %s (patch: %s)", puuid, current_patch)
    start_index = 0
    stop_sync = False

    newest_match_id: str | None = None
    match_ids: list[str] = []
    match_rows: list[dict] = []
    stats: dict[int, dict[str, int]] = {}
    relationships: dict[tuple[int, int], dict[str, int]] = {}

    while not stop_sync:
        match_ids_batch = get_match_ids(puuid, start_index, batch_size)

        if not match_ids_batch:
            break

        if newest_match_id is None:
            newest_match_id = match_ids_batch[0]

        already_processed = get_processed_match_ids(match_ids_batch)

        for match_id in match_ids_batch:
            if match_id == last_synced_match_id:
                LOG.debug("Stopping sync for %s: reached prior sync point %s", puuid, match_id)
                stop_sync = True
                break

            if match_id in already_processed:
                # recorded via another challenger player's sync (shared match) - already
                # captured, but doesn't tell us anything about this player's own history
                LOG.debug("Skipping %s for %s: already processed via another player", match_id, puuid)
                continue

            match_data = get_match_data(match_id)

            if not is_on_current_patch(match_data, current_patch):
                LOG.debug("Stopping sync for %s: match %s not on current patch", puuid, match_id)
                stop_sync = True
                break

            LOG.debug("Aggregating match %s", match_id)
            match_ids.append(match_id)
            match_rows.append(build_match_row(match_id, match_data))
            aggregate_match(match_data, stats, relationships)
            if len(match_ids) % 10 == 0:
                LOG.info("Fetched %d matches for %s", len(match_ids), puuid)

        start_index += batch_size

    flush_player_data(puuid, newest_match_id, match_ids, match_rows, stats, relationships)
    LOG.info("Finished player %s: %d new matches processed", puuid, len(match_ids))


def is_on_current_patch(match_data: dict, current_patch: str) -> bool:
    #retrive and build truncated patch from match_data
    major, minor, *_ = match_data["info"]["gameVersion"].split(".")
    match_patch = f"{major}.{minor}"

    return match_patch == current_patch


def aggregate_match(
    match_data: dict,
    stats: dict[int, dict[str, int]],
    relationships: dict[tuple[int, int], dict[str, int]],
) -> None:
    # excludes remakes and other games where teamPosition wasn't assigned, so
    # they're skipped consistently by both champion_stats and champion_relationships
    participants = [
        p for p in match_data["info"]["participants"]
        if p["teamPosition"] in _POSITION_FIELD
    ]

    for participant in participants:
        row = stats.setdefault(participant["championId"], dict(_EMPTY_STATS_ROW))
        row["wins"] += int(participant["win"])
        row["games"] += 1
        row[_POSITION_FIELD[participant["teamPosition"]]] += 1

    for participant_a in participants:
        for participant_b in participants:
            if participant_a is participant_b:
                continue
            key = (participant_a["championId"], participant_b["championId"])
            row = relationships.setdefault(key, dict(_EMPTY_RELATIONSHIP_ROW))
            if participant_a["teamId"] == participant_b["teamId"]:
                row["wins_as_ally"] += int(participant_a["win"])
                row["games_as_ally"] += 1
            else:
                row["wins_as_opponent"] += int(participant_a["win"])
                row["games_as_opponent"] += 1


def build_match_row(match_id: str, match_data: dict) -> dict:
    row = dict(_EMPTY_MATCH_ROW, match_id=match_id)

    for participant in match_data["info"]["participants"]:
        suffix = _TEAM_POSITION_SUFFIX.get(participant["teamPosition"])
        if suffix is None:
            continue
        side = "blueside" if participant["teamId"] == _BLUE_TEAM_ID else "redside"
        row[f"{side}_{suffix}_champ_id"] = participant["championId"]
        if side == "blueside":
            row["blueside_win"] = participant["win"]

    return row


def flush_player_data(
    puuid: str,
    newest_match_id: str | None,
    match_ids: list[str],
    match_rows: list[dict],
    stats: dict[int, dict[str, int]],
    relationships: dict[tuple[int, int], dict[str, int]],
) -> None:
    if newest_match_id is None:
        return
    with db_connection() as conn, conn.pipeline():
        if match_ids:
            insert_matches(conn, match_rows)
            upsert_champion_stats(
                conn,
                [
                    (
                        champ_id,
                        row["wins"],
                        row["games"],
                        row["games_top"],
                        row["games_jungle"],
                        row["games_mid"],
                        row["games_bot"],
                        row["games_support"],
                    )
                    for champ_id, row in stats.items()
                ],
            )
            upsert_champion_relationships(
                conn,
                [
                    (
                        champ_id,
                        other_champ_id,
                        row["wins_as_ally"],
                        row["games_as_ally"],
                        row["wins_as_opponent"],
                        row["games_as_opponent"],
                    )
                    for (champ_id, other_champ_id), row in relationships.items()
                ],
            )
        update_last_synced_match_id(conn, puuid, newest_match_id)
